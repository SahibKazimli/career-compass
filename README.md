# Career Compass

**An AI-powered career counseling platform that helps you find your ideal path.**


## Overview

Career Compass is an intelligent web application designed to analyze your professional background and provide personalized career guidance. By leveraging Large Language Models (LLMs) and vector search, it compares your profile against thousands of potential career paths to suggest the best matches.

Currently, the system focuses on **Resume Analysis** and **Career Matching**, providing a dashboard that gives you instant feedback on your profile's strength and potential directions.

> **Note from the Developer:**
> This project is currently in an MVP (Minimum Viable Product) state. I am currently focusing on a startup venture, so features like the detailed **Interactive Roadmap**, **Deep Skills Analysis**, and **Learning Resources** aggregation are currently disabled/not implemented. They are part of the long-term vision to make this a full-fledged career navigation platform.

## Tech Stack

This project is built with a modern, high-performance stack separating concerns between a robust backend and a responsive frontend.

### Frontend
- **Framework:** [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Language:** TypeScript
- **Styling:** [TailwindCSS](https://tailwindcss.com/)
- **UI Components:** Custom components based on [shadcn/ui](https://ui.shadcn.com/) design patterns
- **State/Fetching:** React Query + Context API

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** PostgreSQL with `pgvector` for semantic search
- **AI/LLM:** Google Gemini API
- **Vector Embeddings:** For skill and job matching

## Key Features

- **Resume Upload & Parsing**: instantly extracts skills, experience, and education from your PDF resume.
- **AI Analysis**: Uses Gemini to analyze your profile's core competencies and unique value proposition.
- **Smart Recommendations**: Suggests job titles and career paths based on semantic similarity to your background.
- **Gap Analysis**: Identifies high-level missing skills for recommended roles.

## Getting Started

Follow these steps to run the application locally.

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

# Run the server
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

## Future Roadmap

As I find time to return to this project, the following features are planned for implementation:

- **Interactive Roadmap**: A dynamic timeline where users can track their learning progress step-by-step.
- **Resource Aggregator**: Automated scraping of Coursera/Udemy/YouTube to find specific courses for your skill gaps.
- **Detailed Skills Graph**: A visual knowledge graph connecting your current skills to target skills.
- **User Accounts**: Full authentication system to save progress over time.

---

