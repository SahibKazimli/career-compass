# Career Compass

An AI-powered guidance to help you find new and ideal career paths

## Overview

Career Compass is an AI-driven web application that analyzes your background, skills and goals to suggest personalized career paths. Additionally, updated learning resources recommendations and industry insights will be provided. 

Upload your resume and describe your interests, and let the system generate a tailored roadmap. 

This project combines natural language processing, semantic search, and LLM reasoning to deliver actionable career guidance. 

## Key Features
- Resume Upload & Parsing using OCR and NLP
- Embedding the users skills and background, compares them with job and career embeddings.
- Job Recommendation API 
- Skill Gap Analysis
- Learning Path Generation

## Tech Stack
| Component | Tool |
|------------|------|
| **Web Framework** | FastAPI |
| **Database (ORM)** | SQLite |
| **vectorDB** | ChromaDB | 
| **LLM** | Gemini/OpenAI |
| **OCR/NLP** | Tesseract |
| **Security** | python-dotenv |
| **Server** | uvicorn |
| **Frontend** | Streamlit (will probably create proper frontend later on) 

Note: A bit unsure if I should use ChromaDB or Postgres with pgvector. 

## Program Flow Idea

```bash
    Career Compass
    │
    ├── User uploads resume or fills form
    │
    ├── FastAPI backend parses & embeds text
    │   ├── Extracts skills, experience, education
    │   ├── Generates embeddings (OpenAI/Gemini)
    │   ├── Stores profile in SQLite + ChromaDB
    │
    ├── User queries “best career paths” or “skills to learn for ML engineer”
    │   ├── FastAPI retrieves embeddings
    │   ├── Runs LLM-based reasoning
    │   └── Returns personalized roadmap
    │
    └── Streamlit/React frontend displays results nicely
```

Installation guide will be given later on when I've started coding. 