// API Service Layer for Career Compass
// Handles all communication with the FastAPI backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'career_compass_access_token';
const REFRESH_TOKEN_KEY = 'career_compass_refresh_token';

// Types for API responses
export interface User {
    user_id: number;
    email: string;
    name: string;
    created_at: string;
}

export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
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

// =====================
// Token Management
// =====================

export function getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(tokens: AuthTokens): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function isAuthenticated(): boolean {
    return !!getAccessToken();
}

// =====================
// API Request Helper
// =====================

async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth: boolean = false
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Add authorization header if token exists
    const token = getAccessToken();
    if (token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    } else if (requireAuth) {
        throw new ApiError(401, 'Authentication required');
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    // Handle 401 - try to refresh token
    if (response.status === 401 && token) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            // Retry the request with new token
            const newToken = getAccessToken();
            (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
            const retryResponse = await fetch(url, { ...options, headers });

            if (!retryResponse.ok) {
                const errorData = await retryResponse.json().catch(() => ({ detail: 'Unknown error' }));
                throw new ApiError(retryResponse.status, errorData.detail || 'Request failed');
            }
            return retryResponse.json();
        } else {
            clearTokens();
            throw new ApiError(401, 'Session expired. Please login again.');
        }
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new ApiError(response.status, errorData.detail || 'Request failed');
    }

    return response.json();
}

async function tryRefreshToken(): Promise<boolean> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const tokens: AuthTokens = await response.json();
            setTokens(tokens);
            return true;
        }
        return false;
    } catch {
        return false;
    }
}

// =====================
// Authentication API
// =====================

export async function register(email: string, name: string, password: string): Promise<AuthTokens> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, password }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
        throw new ApiError(response.status, errorData.detail || 'Registration failed');
    }

    const tokens: AuthTokens = await response.json();
    setTokens(tokens);
    return tokens;
}

export async function login(email: string, password: string): Promise<AuthTokens> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
        throw new ApiError(response.status, errorData.detail || 'Invalid email or password');
    }

    const tokens: AuthTokens = await response.json();
    setTokens(tokens);
    return tokens;
}

export async function logout(): Promise<void> {
    clearTokens();
}

export async function getCurrentUser(): Promise<User> {
    return apiRequest<User>('/auth/me', {}, true);
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiRequest('/auth/password', {
        method: 'PUT',
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }, true);
}

export async function deleteAccount(): Promise<void> {
    await apiRequest('/auth/account', { method: 'DELETE' }, true);
    clearTokens();
}

// =====================
// Legacy User API (backward compatibility)
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

    const headers: HeadersInit = {};
    const token = getAccessToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/resume/process?user_id=${userId}&stream=false`, {
        method: 'POST',
        headers,
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

    const headers: HeadersInit = {};
    const token = getAccessToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}/resume/process?user_id=${userId}&stream=true`,
        {
            method: 'POST',
            headers,
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
