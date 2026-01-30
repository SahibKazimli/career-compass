import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getRecommendations,
    getSkillsAnalysis,
    getResumeAnalysis,
    getRoadmap,
    uploadResume,
    processResume,
    analyzeResume,
    RecommendationsResponse,
    SkillsAnalysisResponse,
    ResumeAnalysisResponse,
    RoadmapResponse,
    ResumeUploadResponse,
} from '../services/api';
import { useUser } from '../context/UserContext';

// =====================
// Recommendations Hook
// =====================

export function useRecommendations(options?: {
    user_interests?: string;
    current_role?: string;
}) {
    const { user } = useUser();

    return useQuery<RecommendationsResponse>({
        queryKey: ['recommendations', user?.user_id, options],
        queryFn: () => {
            if (!user?.user_id) throw new Error('User not logged in');
            return getRecommendations(user.user_id, options);
        },
        enabled: !!user?.user_id,
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: false,
    });
}

// =====================
// Skills Analysis Hook
// =====================

export function useSkillsAnalysis() {
    const { user } = useUser();

    return useQuery<SkillsAnalysisResponse>({
        queryKey: ['skills', user?.user_id],
        queryFn: () => {
            if (!user?.user_id) throw new Error('User not logged in');
            return getSkillsAnalysis(user.user_id);
        },
        enabled: !!user?.user_id,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });
}

// =====================
// Resume Analysis Hook
// =====================

export function useResumeAnalysis() {
    const { user } = useUser();

    return useQuery<ResumeAnalysisResponse>({
        queryKey: ['analysis', user?.user_id],
        queryFn: () => {
            if (!user?.user_id) throw new Error('User not logged in');
            return getResumeAnalysis(user.user_id);
        },
        enabled: !!user?.user_id,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });
}

// =====================
// Roadmap Hook
// =====================

export function useRoadmap() {
    const { user } = useUser();

    return useQuery<RoadmapResponse>({
        queryKey: ['roadmap', user?.user_id],
        queryFn: () => {
            if (!user?.user_id) throw new Error('User not logged in');
            return getRoadmap(user.user_id);
        },
        enabled: !!user?.user_id,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });
}

// =====================
// Resume Upload Hook
// =====================

export function useResumeUpload() {
    const { user, setHasResume } = useUser();
    const queryClient = useQueryClient();

    return useMutation<ResumeUploadResponse, Error, File>({
        mutationFn: async (file: File) => {
            if (!user?.user_id) throw new Error('User not logged in');
            return uploadResume(user.user_id, file);
        },
        onSuccess: () => {
            setHasResume(true);
            // Invalidate all user-related queries to refetch with new data
            queryClient.invalidateQueries({ queryKey: ['recommendations'] });
            queryClient.invalidateQueries({ queryKey: ['skills'] });
            queryClient.invalidateQueries({ queryKey: ['analysis'] });
            queryClient.invalidateQueries({ queryKey: ['roadmap'] });
        },
    });
}

// =====================
// Resume Process Hook (with streaming)
// =====================

export function useResumeProcess() {
    const { user, setHasResume } = useUser();
    const queryClient = useQueryClient();

    return useMutation<void, Error, { file: File; onProgress?: (event: { type: string; data: unknown }) => void }>({
        mutationFn: async ({ file, onProgress }) => {
            if (!user?.user_id) throw new Error('User not logged in');
            return processResume(user.user_id, file, onProgress);
        },
        onSuccess: () => {
            setHasResume(true);
            // Invalidate all user-related queries
            queryClient.invalidateQueries({ queryKey: ['recommendations'] });
            queryClient.invalidateQueries({ queryKey: ['skills'] });
            queryClient.invalidateQueries({ queryKey: ['analysis'] });
            queryClient.invalidateQueries({ queryKey: ['roadmap'] });
        },
    });
}

// =====================
// Resume Analyze Hook
// =====================

export function useAnalyzeResume() {
    const { user } = useUser();

    return useQuery({
        queryKey: ['resume-analyze', user?.user_id],
        queryFn: () => {
            if (!user?.user_id) throw new Error('User not logged in');
            return analyzeResume(user.user_id);
        },
        enabled: !!user?.user_id,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });
}
