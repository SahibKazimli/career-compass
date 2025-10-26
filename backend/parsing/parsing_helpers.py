from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import init_db, get_db, User, Resume
from contextlib import asynccontextmanager
import tempfile
import os
import json
from resume_parser import genai_parse_pdf
from utils.embeddings import embed_resume_chunks


def parse_upload(
    file: UploadFile = File(...)
):
     # Save to temporary file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    
        # Parse the PDF using Gemini
        print(f"Parsing resume: {file.filename}")
        parsed_resume = genai_parse_pdf(tmp_path, file.filename)
        
        # Embed the parsed chunks
        print(f"Embedding chunks...")
        embedded_resume = embed_resume_chunks(parsed_resume)
        
        # Extract skills and experience from chunks
        skills = []
        experience = []
        raw_text_parts = []
        
        for chunk in embedded_resume['chunks']:
            section = chunk['section'].lower()
            content = chunk['content']
            
            raw_text_parts.append(f"{chunk['section']}:\n{content}\n")
            
            # Extract skills from skills section
            if 'skill' in section:
                # Simple extraction - you can make this more sophisticated
                skills.append(content)
            
            # Extract experience from work/experience sections
            if any(keyword in section for keyword in ['work', 'experience', 'employment']):
                experience.append(content)
        
        # Combine all chunks for raw_text
        raw_text = "\n".join(raw_text_parts)
        return raw_text