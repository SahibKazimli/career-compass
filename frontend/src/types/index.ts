export interface User {
    user_id: number;
    email: string;
    name: string;
    created_at?: string;
  }
  
  export interface ResumeChunk {
    section: string;
    content: string;
    summary: string;
  }
  
  export interface ParsedResume {
    resume_id: number;
    filename: string;
    parsed_data: {
      chunks: ResumeChunk[];
      skills: string[];
      experience: string[];
      total_chunks: number;
    };
  }
  
  export interface Recommendation {
    title: string;
    match_reason: string;
    relevant_existing_skills: string[];
    skills_to_develop: string[];
    transition_difficulty: "Easy" | "Medium" | "Hard";
    estimated_salary_range: string;
    first_steps: string[];
  }
  
  export interface RecommendationsResponse {
    recommendations: Recommendation[];
  }