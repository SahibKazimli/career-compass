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
| **Frontend** | Streamlit (will create proper frontend later on) 

Note: A bit unsure if I should use ChromaDB or Postgres with pgvector. 
