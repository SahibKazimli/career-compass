import json
from typing import Dict, Any, List, Optional

from backend.db.pg import get_conn
from backend.db.events import (
    fetch_pending_events,
    mark_event_status,
    increment_attempts,
    append_run_state,
    mark_run_status,
    publish_event,
    create_run,
)
from backend.db.pg_vectors import (
    fetch_latest_resume,
    fetch_resume_chunks,
)
from backend.parsing.parsing_helpers import parse_upload
from backend.agents.resume_analyzer import analyze_resume_deep
from backend.agents.skills_agent import analyze_skills
from backend.agents.recommender import generate_recommendations
from backend.utils.llm import _json_load_safe


class Orchestrator:
    """
    Minimal orchestrator for the multi-agent system.

    Responsibilities:
    - Poll pending events from Postgres (agent_events table).
    - Dispatch each event_type to a handler.
    - Use existing helpers/agents for parsing, analysis, and recommendations.
    - Update event + run state in Postgres, nothing more.
    """

    def __init__(self, max_events_per_tick: int = 10, max_attempts: int = 3):
        self.max_events_per_tick = max_events_per_tick
        self.max_attempts = max_attempts
    
    def tick(self) -> int:
        """
        Process up to `max_events_per_tick` pending events once.

        Returns:
            Number of events successfully processed.
        """
        processed = 0

        conn = next(get_conn())
        try:
            events = fetch_pending_events(conn, limit=self.max_events_per_tick)

            for event in events:
                event_id = event["event_id"]
                attempts = event.get("attempts", 0)

                if attempts >= self.max_attempts:
                    mark_event_status(conn, event_id, "failed")
                    continue

                try:
                    increment_attempts(conn, event_id)
                    mark_event_status(conn, event_id, "processing")

                    self._handle_event(conn, event)

                    mark_event_status(conn, event_id, "completed")
                    processed += 1

                except Exception as e:
                    # TODO: need to implement proper logging maybe?
                    print(f"[orchestrator] Error handling event {event_id}: {e}")
                    mark_event_status(conn, event_id, "error")

            conn.commit()
        finally:
            conn.close()

        return processed
    
    
    def _handle_event(self, conn, event: Dict[str, Any]) -> None:
        event_type = event["event_type"]
        user_id: Optional[int] = event.get("user_id")
        resume_id: Optional[int] = event.get("resume_id")
        run_id: Optional[str] = event.get("run_id")
        payload: Dict[str, Any] = event.get("payload") or {}

        if event_type == "start_career_run":
            self._on_start_career_run(conn, user_id=user_id, payload=payload)

        elif event_type == "resume_uploaded":
            self._on_resume_uploaded(conn, user_id=user_id, resume_id=resume_id, payload=payload)

        elif event_type == "resume_parsed":
            self._on_resume_parsed(conn, user_id=user_id, resume_id=resume_id, payload=payload)

        elif event_type == "skills_analyzed":
            self._on_skills_analyzed(conn, user_id=user_id, resume_id=resume_id, payload=payload)

        elif event_type == "recommendations_ready":
            self._on_recommendations_ready(conn, run_id=run_id, payload=payload)

        else:
            print(f"[orchestrator] Ignoring unknown event_type={event_type}")
            
    
    def _on_start_career_run(
        self,
        conn,
        user_id: Optional[int],
        payload: Dict[str, Any],
    ) -> None:
        if user_id is None:
            raise ValueError("start_career_run requires user_id")

        target_role = payload.get("target_role", "career_change")
        notes = payload.get("notes")
        resume_id = payload.get("resume_id")

        run_id = create_run(conn, user_id=user_id, target_role=target_role)
        append_run_state(
            conn,
            run_id,
            {
                "status": "started",
                "target_role": target_role,
                "notes": notes,
                "resume_id": resume_id,
            },
        )

        if resume_id is not None:
            publish_event(
                conn,
                event_type="resume_uploaded",
                user_id=user_id,
                resume_id=resume_id,
                run_id=run_id,
                payload={},
            )


    def _on_resume_uploaded(
        self,
        conn,
        user_id: Optional[int],
        resume_id: Optional[int],
        payload: Dict[str, Any],
    ) -> None:
        if user_id is None:
            raise ValueError("resume_uploaded requires user_id")

        if resume_id is None:
            row = fetch_latest_resume(conn, user_id=user_id)
            if not row:
                raise ValueError(f"No resume found for user_id={user_id}")
            resume_id = row["id"]
        else:
            row = fetch_latest_resume(conn, user_id=user_id)

        raw_text = row.get("raw_text") if row else None
        if not raw_text:
            raise ValueError(f"Resume {resume_id} for user {user_id} has no raw_text")

        parsed = parse_upload(raw_text)
        deep_analysis = analyze_resume_deep(parsed)

        run_id = payload.get("run_id") or row.get("run_id")
        if run_id:
            append_run_state(
                conn,
                run_id,
                {
                    "status": "resume_parsed",
                    "resume_id": resume_id,
                    "parsed": deep_analysis,
                },
            )

        publish_event(
            conn,
            event_type="resume_parsed",
            user_id=user_id,
            resume_id=resume_id,
            run_id=run_id,
            payload={"parsed": deep_analysis},
        )
        
        
    
    def _on_resume_parsed(
        self,
        conn,
        user_id: Optional[int],
        resume_id: Optional[int],
        payload: Dict[str, Any],
    ) -> None:
        if user_id is None or resume_id is None:
            raise ValueError("resume_parsed requires user_id and resume_id")

        parsed = payload.get("parsed")
        if parsed is None:
            row = fetch_latest_resume(conn, user_id=user_id)
            chunks = fetch_resume_chunks(conn, resume_id=resume_id)
            parsed = {
                "raw_text": row.get("raw_text") if row else "",
                "chunks": chunks,
            }

        skills_result = analyze_skills(parsed)

        run_id = payload.get("run_id")
        if run_id:
            append_run_state(
                conn,
                run_id,
                {
                    "status": "skills_analyzed",
                    "resume_id": resume_id,
                    "skills": skills_result,
                },
            )
        
        publish_event(
            conn,
            event_type="skills_analyzed",
            user_id=user_id,
            resume_id=resume_id,
            run_id=run_id,
            payload={"skills": skills_result},
        )