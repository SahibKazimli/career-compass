import { Target, TrendingUp, Clock, Loader2, AlertCircle } from 'lucide-react';
import { StatCard } from '../components/dashboard/StatCard';
import { RecommendationCard } from '../components/dashboard/RecommendationCard';
import { SkillsOverview } from '../components/dashboard/SkillsOverview';
import { RoadmapTimeline } from '../components/roadmap/RoadmapTimeline';
import { useRecommendations, useSkillsAnalysis, useRoadmap } from '../hooks/useApi';
import { useUser } from '../context/UserContext';
import { mockSkills, mockRecommendations, mockRoadmapSteps } from '../data/mockData';
import { Skill, CareerRecommendation, RoadmapStep } from '../types/career';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Link } from 'react-router-dom';

export default function Dashboard() {
    const { user, hasResume } = useUser();
    const { data: recommendationsData, isLoading: recLoading, error: recError } = useRecommendations();
    const { data: skillsData, isLoading: skillsLoading } = useSkillsAnalysis();
    const { data: roadmapData, isLoading: roadmapLoading } = useRoadmap();

    // Transform API data to frontend types
    const transformRecommendations = (): CareerRecommendation[] => {
        if (!recommendationsData?.recommendations?.recommendations) {
            return mockRecommendations;
        }

        return recommendationsData.recommendations.recommendations.map((rec) => ({
            title: rec.title,
            matchScore: 75, // Default score if not provided
            matchReason: rec.match_reason,
            estimatedSalary: rec.estimated_salary_range,
            skillsToDevelope: rec.skills_to_develop,
            firstSteps: rec.first_steps,
            timeToTransition: rec.transition_difficulty === 'Easy' ? '3-6 months' :
                rec.transition_difficulty === 'Medium' ? '6-12 months' : '12-18 months',
        }));
    };

    const transformSkills = (): Skill[] => {
        if (!skillsData?.skills || typeof skillsData.skills !== 'object') {
            return mockSkills;
        }

        // Try to extract skills from the analysis data
        const skills = skillsData.skills as Record<string, unknown>;
        // Check various likely structures
        if (skills.skills && Array.isArray(skills.skills)) {
            return (skills.skills as any[]).map((s: any) => {
                if (typeof s === 'string') {
                    return { name: s, level: 'intermediate', category: 'technical' };
                }
                return {
                    name: s.name || s.skill || 'Unknown',
                    level: s.level || 'intermediate',
                    category: s.category || 'technical'
                };
            });
        }

        // Flatten logic if skills are categorized objects in top-level
        const extractedSkills: Skill[] = [];
        if (skills.technical_skills && Array.isArray(skills.technical_skills)) {
            extractedSkills.push(...(skills.technical_skills as string[]).map(s => ({ name: s, level: 'intermediate' as const, category: 'technical' as const })));
        }
        if (skills.soft_skills && Array.isArray(skills.soft_skills)) {
            extractedSkills.push(...(skills.soft_skills as string[]).map(s => ({ name: s, level: 'intermediate' as const, category: 'soft' as const })));
        }
        if (extractedSkills.length > 0) return extractedSkills;

        return mockSkills;
    };

    const transformRoadmap = (): RoadmapStep[] => {
        if (!roadmapData?.learning_path || roadmapData.learning_path.length === 0) {
            return mockRoadmapSteps;
        }

        return roadmapData.learning_path.map((step: any, index: number) => ({
            id: String(index + 1),
            title: typeof step === 'string' ? step : step.step || 'Learning Step',
            description: step.description || '',
            duration: step.duration || '4 weeks',
            status: index === 0 ? 'in-progress' as const : 'upcoming' as const,
            skills: step.skills || [],
        }));
    };

    const recommendations = transformRecommendations();
    const skills = transformSkills();
    const roadmapSteps = transformRoadmap();

    const isLoading = recLoading || skillsLoading || roadmapLoading;
    const hasData = hasResume || (recommendationsData?.recommendations?.recommendations?.length ?? 0) > 0;

    // Welcome state for users without resume
    if (!user || (!hasResume && !hasData)) {
        return (
            <div className="space-y-6">
                <div className="animate-fade-in">
                    <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">
                        Track your career progress and discover new opportunities
                    </p>
                </div>

                <Card className="animate-fade-in">
                    <CardContent className="pt-6">
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                                <Target className="w-8 h-8 text-primary" />
                            </div>
                            <h2 className="text-xl font-semibold text-foreground mb-2">
                                Welcome to Career Compass
                            </h2>
                            <p className="text-muted-foreground max-w-md mx-auto mb-6">
                                Upload your resume to get personalized career recommendations, skill analysis,
                                and a roadmap to your dream role.
                            </p>
                            <Link to="/resume">
                                <Button size="lg">
                                    Upload Your Resume
                                </Button>
                            </Link>
                        </div>
                    </CardContent>
                </Card>

                {/* Show mock data preview */}

            </div>
        );
    }

    // Loading state
    if (isLoading) {
        return (
            <div className="space-y-6">
                <div className="animate-fade-in">
                    <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">
                        Track your career progress and discover new opportunities
                    </p>
                </div>

                <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                        <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
                        <p className="text-muted-foreground">Loading your career data...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Error state
    if (recError) {
        return (
            <div className="space-y-6">
                <div className="animate-fade-in">
                    <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">
                        Track your career progress and discover new opportunities
                    </p>
                </div>

                <Card className="animate-fade-in border-destructive/50">
                    <CardContent className="pt-6">
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-4">
                                <AlertCircle className="w-8 h-8 text-destructive" />
                            </div>
                            <h2 className="text-xl font-semibold text-foreground mb-2">
                                Unable to Load Data
                            </h2>
                            <p className="text-muted-foreground max-w-md mx-auto mb-4">
                                {recError instanceof Error ? recError.message : 'Failed to load recommendations'}
                            </p>
                            <Link to="/resume">
                                <Button variant="outline">
                                    Try Uploading a Resume
                                </Button>
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                <p className="text-muted-foreground mt-1">
                    Track your career progress and discover new opportunities
                </p>
            </div>



            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recommendations Section */}
                <div className="lg:col-span-2 space-y-4">
                    <h2 className="text-lg font-semibold text-foreground">Top Career Matches</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {recommendations.slice(0, 2).map((rec, index) => (
                            <RecommendationCard
                                key={index}
                                recommendation={rec}
                            />
                        ))}
                    </div>
                </div>

                {/* Skills Overview */}
                <div className="lg:col-span-1">
                    <SkillsOverview skills={skills} />
                </div>
            </div>

            {/* Roadmap Preview */}
            <div className="bg-card rounded-xl p-6 border border-border shadow-sm animate-fade-in">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-lg font-semibold text-foreground">Your Career Roadmap</h2>
                        <p className="text-sm text-muted-foreground">
                            Path to {recommendations[0]?.title || 'Your Dream Role'}
                        </p>
                    </div>
                    <span className="text-sm text-primary font-medium">
                        Step 1 of {roadmapSteps.length}
                    </span>
                </div>
                <RoadmapTimeline steps={roadmapSteps.slice(0, 3)} />
            </div>
        </div>
    );
}
