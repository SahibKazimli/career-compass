# Career Compass

**An AI-powered career counseling platform that analyzes your resume and provides personalized career guidance.**

## Overview

Career Compass is an intelligent web application that uses Large Language Models (LLMs) to analyze professional backgrounds and suggest optimal career paths. Upload your resume and get instant AI-powered analysis of your skills, career recommendations, and a personalized roadmap to your dream role.

The system leverages **Google's Gemini AI** to parse resumes, extract skills and experience, and generate tailored career recommendations based on your profile.

## What It Does

1. **Resume Upload & Analysis**
   - Upload your PDF resume
   - AI extracts and categorizes your skills, experience, and education
   - Creates semantic embeddings for intelligent matching

2. **Skills Analysis**
   - Identifies your core technical and soft skills
   - Highlights standout capabilities
   - Suggests skills to strengthen for career growth
   - Recommends potential career directions

3. **Career Matching**
   - AI matches your profile to suitable career paths
   - Provides match scores and transition difficulty ratings
   - Identifies transferable skills and skill gaps
   - Shows salary ranges and market demand


## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: PostgreSQL with `pgvector` extension for semantic search
- **AI/LLM**: Google Gemini API (gemini-2.5-flash)
- **Vector Embeddings**: 768-dimensional embeddings via Gemini Embedding API
- **Database Driver**: psycopg3 with connection pooling
- **PDF Parsing**: Gemini Vision API for resume extraction

### Frontend
- **Framework**: [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Language**: TypeScript
- **Styling**: [TailwindCSS](https://tailwindcss.com/)
- **State Management**: React Query + Context API

### Infrastructure
- **Database**: PostgreSQL with pgvector for vector similarity search
- **File Storage**: Temporary filesystem (PDF processing)
- **Rate Limiting**: slowapi for API protection

## Key Features

- **AI Resume Parsing**: Extracts structured data from PDF resumes using Gemini
- **Semantic Search**: Vector-based similarity matching for career paths
- **Intelligent Recommendations**: AI-generated career matches with reasoning
- **Skills Gap Analysis**: Identifies what you need to learn next
- **Real-time Processing**: Streaming updates during resume processing

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (with pgvector extension)

### 1. Backend Setup

```bash
# Navigate to project root
cd career-compass

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Environment Setup
# Create a .env file with:
# DATABASE_URL=postgresql://user:password@localhost:5432/career_compass
# GOOGLE_API_KEY=your_gemini_api_key

# Initialize database (auto-runs on startup)
python -m uvicorn backend.api.app:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The application will be available at `http://localhost:8080`.

## How It Works

### Resume Processing Pipeline

1. **Upload**: User uploads PDF resume via frontend
2. **Parsing**: Gemini Vision API extracts text and structure
3. **Chunking**: Resume broken into sections (skills, experience, education)
4. **Embedding**: Each chunk converted to 768-dim vector embeddings
5. **Storage**: Raw text, parsed data, and embeddings stored in PostgreSQL
6. **Analysis**: AI agents analyze skills and generate recommendations
7. **Matching**: Vector similarity search matches profile to career paths

### AI Agents

- **Resume Analyzer** (`resume_analyzer.py`): Performs deep analysis of resume sections to extract core competencies, career progression patterns, and unique value propositions
- **Skills Agent** (`skills_agent.py`): Analyzes user's skillset, identifies gaps, and suggests learning paths for target roles
- **Recommender** (`recommender.py`): Generates AI-powered career recommendations based on resume data using vector embeddings
- **Career Matcher** (`career_matcher.py`): Matches user profiles to suitable career paths and creates detailed transition roadmaps with difficulty assessments
- **Resources Agent (Not Used) ** (`resources_agent.py`): Generates personalized learning resources (courses, books, projects) based on skill gaps
- **Orchestrator** (`orchestrator.py`): Manages the workflow pipeline and coordinates agent execution in parallel

### Database Architecture

PostgreSQL with pgvector stores:
- **Users**: Account information
- **Resumes**: Parsed resume data and embeddings
- **Resume Chunks**: Section-level embeddings for semantic search
- **Career Paths**: Pre-defined career paths with vector embeddings
- **Recommendations**: AI-generated career matches with skill gaps
- **Analysis Results**: Skills and resume analysis data

## Screenshots

*Resume Upload*  
![Resume Upload](/media/screenshots/Screenshot%202026-02-05%20at%2018.27.08.png)

*Skills Analysis*  
![Skills Analysis](/media/screenshots/Screenshot%202026-02-05%20at%2018.27.19.png)

*Career Matching*  
![Career Matching](/media/screenshots/Screenshot%202026-02-05%20at%2018.27.29.png)

## API Endpoints

### Core
- `GET /health` - Health check
- `POST /resume/process` - Upload and process resume
- `GET /resume/analyze/{user_id}` - Get resume analysis

### Analysis
- `GET /skills/{user_id}` - Get skills analysis
- `GET /recommendations/{user_id}` - Get career recommendations
- `GET /careers/{user_id}` - Get career matches
- `GET /roadmap/{user_id}` - Get career roadmap

### Search
- `GET /search/chunks?query={text}` - Semantic search across resume chunks

## Configuration

Required environment variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/career_compass
GOOGLE_API_KEY=your_gemini_api_key
JWT_SECRET=your_secret_key
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:5173
```

Note from Developer: Honestly JWT is super unnecessary, but I used it since I originally wanted to host this project safely. But since I'm focusing 
on building a startup, this isn't quite as high on the priority list as that. 

---

