// API Service Layer for Career Compass
// Handles all communication with the FastAPI backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types for API responses
export interface User {
    user_id: number;
    email: string;
    name: string;
    created_at: string;
}

export interface ResumeUploadResponse {
    message: string;
    resume_id: number;
    filename: string;
    parsed_data: {
        chunks: Array<{
            section: string;
            content: string;
            summary: string;
        }>;
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
    transition_difficulty: 'Easy' | 'Medium' | 'Hard';
    estimated_salary_range: string;
    first_steps: string[];
}

export interface RecommendationsResponse {
    user_id: number;
    resume_id?: number;
    recommendations: {
        recommendations: Recommendation[];
        overall_assessment: string;
        model_used?: string;
    };
}

export interface SkillsAnalysisResponse {
    user_id: number;
    analysis_id?: number;
    skills: Record<string, unknown>;
    created_at?: string;
    message?: string;
}

export interface ResumeAnalysisResponse {
    user_id: number;
    analysis_id?: number;
    analysis: Record<string, unknown> | null;
    created_at?: string;
    message?: string;
}

export interface RoadmapResponse {
    user_id: number;
    recommendations: Record<string, unknown>;
    skill_gaps: string[];
    learning_path: string[];
    created_at?: string;
    message?: string;
}

// API Error class
export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

// Helper function for API requests
async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new ApiError(response.status, errorData.detail || 'Request failed');
    }

    return response.json();
}

// =====================
// User API
// =====================

export async function createUser(email: string, name: string): Promise<User> {
    return apiRequest<User>(`/users?email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`, {
        method: 'POST',
    });
}

export async function getUserById(userId: number): Promise<User> {
    return apiRequest<User>(`/users/${userId}`);
}

export async function getUserByEmail(email: string): Promise<User> {
    return apiRequest<User>(`/users/email/${encodeURIComponent(email)}`);
}

// =====================
// Resume API
// =====================

export async function uploadResume(userId: number, file: File): Promise<ResumeUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Use /resume/process without streaming to get full pipeline (parse + recommendations)
    const response = await fetch(`${API_BASE_URL}/resume/process?user_id=${userId}&stream=false`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new ApiError(response.status, errorData.detail || 'Upload failed');
    }

    return response.json();
}

export async function processResume(
    userId: number,
    file: File,
    onProgress?: (event: { type: string; data: unknown }) => void
): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
        `${API_BASE_URL}/resume/process?user_id=${userId}&stream=true`,
        {
            method: 'POST',
            body: formData,
        }
    );

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Processing failed' }));
        throw new ApiError(response.status, errorData.detail || 'Processing failed');
    }

    // Handle NDJSON streaming response
    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.trim()) {
                try {
                    const event = JSON.parse(line);
                    onProgress?.(event);
                } catch (e) {
                    console.error('Failed to parse event:', line);
                }
            }
        }
    }
}

export async function analyzeResume(userId: number): Promise<{
    user_id: number;
    resume_id: number;
    analysis: {
        sections: Array<{ section: string; sample: string }>;
        note: string;
    };
}> {
    return apiRequest(`/resume/analyze/${userId}`);
}

// =====================
// Recommendations API
// =====================

export async function getRecommendations(
    userId: number,
    options?: {
        user_interests?: string;
        current_role?: string;
    }
): Promise<RecommendationsResponse> {
    const params = new URLSearchParams();
    if (options?.user_interests) {
        params.set('user_interests', options.user_interests);
    }
    if (options?.current_role) {
        params.set('current_role', options.current_role);
    }

    const queryString = params.toString();
    const endpoint = `/recommendations/${userId}${queryString ? `?${queryString}` : ''}`;

    return apiRequest<RecommendationsResponse>(endpoint);
}

// =====================
// Skills API
// =====================

export async function getSkillsAnalysis(userId: number): Promise<SkillsAnalysisResponse> {
    return apiRequest<SkillsAnalysisResponse>(`/skills/${userId}`);
}

// =====================
// Analysis API
// =====================

export async function getResumeAnalysis(userId: number): Promise<ResumeAnalysisResponse> {
    return apiRequest<ResumeAnalysisResponse>(`/analysis/${userId}`);
}

// =====================
// Roadmap API
// =====================

export async function getRoadmap(userId: number): Promise<RoadmapResponse> {
    return apiRequest<RoadmapResponse>(`/roadmap/${userId}`);
}

// =====================
// Search API
// =====================

export async function searchChunks(
    query: string,
    userId?: number
): Promise<{ query: string; results: unknown[] }> {
    const params = new URLSearchParams({ query });
    if (userId) {
        params.set('user_id', userId.toString());
    }
    return apiRequest(`/search/chunks?${params.toString()}`);
}
