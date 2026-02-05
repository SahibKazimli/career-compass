import type { ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { useSkillsAnalysis } from '../hooks/useApi';
import type { SkillsData } from '../services/api';
import {
    Zap,
    TrendingUp,
    Star,
    Target,
    Loader2,
    Lightbulb,
    Compass,
    AlertCircle
} from 'lucide-react';

// Error Boundary for the page
function SkillsErrorFallback({ error }: { error: Error }) {
    return (
        <div className="p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-600 mb-2">Error Loading Skills</h2>
            <p className="text-muted-foreground mb-4">{error.message}</p>
            <button 
                onClick={() => window.location.reload()} 
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
            >
                Reload Page
            </button>
        </div>
    );
}

export default function Skills() {
    const { data: skillsData, isLoading, error: queryError } = useSkillsAnalysis();

    // Log for debugging
    console.log('Skills Debug:', { skillsData, isLoading, queryError });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (queryError) {
        return <SkillsErrorFallback error={queryError instanceof Error ? queryError : new Error('Unknown error')} />;
    }

    // Handle missing data gracefully
    if (!skillsData?.skills) {
        return (
            <div className="text-center py-12">
                <Zap className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-foreground">No Skills Analysis Yet</h2>
                <p className="text-muted-foreground mt-2">
                    Upload your resume on the Resume page to get your skills analyzed.
                </p>
            </div>
        );
    }

    // Safely cast with validation
    let skills: SkillsData;
    try {
        skills = skillsData.skills as SkillsData;
        
        // Validate that skills is an object
        if (!skills || typeof skills !== 'object') {
            throw new Error('Invalid skills data structure');
        }
    } catch (err) {
        console.error('Skills casting error:', err);
        return <SkillsErrorFallback error={err instanceof Error ? err : new Error('Failed to parse skills data')} />;
    }

    // Helper to render skill list with safety checks
    const renderSkillList = (items: string[] | undefined, icon: ReactNode, color: string) => {
        // Safety check: ensure items is an array
        if (!Array.isArray(items)) {
            console.warn('renderSkillList received non-array:', items);
            return null;
        }
        
        if (items.length === 0) return null;
        
        return items.map((skill, index) => {
            // Ensure skill is a string
            const skillText = typeof skill === 'string' ? skill : String(skill);
            return (
                <div key={index} className="flex items-start gap-2 py-2 border-b border-border/50 last:border-0">
                    <span className={`mt-1 ${color}`}>{icon}</span>
                    <span className="text-sm text-foreground">{skillText}</span>
                </div>
            );
        });
    };

    // Safely get arrays with defaults
    const technicalSkills = Array.isArray(skills.core_technical_skills) ? skills.core_technical_skills : [];
    const softSkills = Array.isArray(skills.soft_skills) ? skills.soft_skills : [];
    const standoutSkills = Array.isArray(skills.standout_skills) ? skills.standout_skills : [];
    const skillsToStrengthen = Array.isArray(skills.skills_to_strengthen) ? skills.skills_to_strengthen : [];
    const careerDirections = Array.isArray(skills.potential_career_directions) ? skills.potential_career_directions : [];

    return (
        <div className="space-y-6 max-w-5xl">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-foreground">Skills Analysis</h1>
                <p className="text-muted-foreground mt-1">
                    AI-powered breakdown of your skills and career potential
                </p>
            </div>

            {/* Skills Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Technical Skills */}
                <Card className="animate-fade-in">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Zap className="w-5 h-5 text-blue-500" />
                            Technical Skills
                        </CardTitle>
                        <CardDescription>Your core technical competencies</CardDescription>
                    </CardHeader>
                    <CardContent className="max-h-80 overflow-y-auto">
                        {renderSkillList(
                            technicalSkills,
                            <div className="w-2 h-2 rounded-full bg-blue-500" />,
                            "text-blue-500"
                        )}
                    </CardContent>
                </Card>

                {/* Soft Skills */}
                <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Lightbulb className="w-5 h-5 text-purple-500" />
                            Soft Skills
                        </CardTitle>
                        <CardDescription>Interpersonal and cognitive abilities</CardDescription>
                    </CardHeader>
                    <CardContent className="max-h-80 overflow-y-auto">
                        {renderSkillList(
                            softSkills,
                            <div className="w-2 h-2 rounded-full bg-purple-500" />,
                            "text-purple-500"
                        )}
                    </CardContent>
                </Card>

                {/* Standout Skills */}
                <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Star className="w-5 h-5 text-amber-500" />
                            Standout Skills
                        </CardTitle>
                        <CardDescription>What makes you unique</CardDescription>
                    </CardHeader>
                    <CardContent className="max-h-80 overflow-y-auto">
                        {renderSkillList(
                            standoutSkills,
                            <Star className="w-3 h-3 fill-amber-500 text-amber-500" />,
                            "text-amber-500"
                        )}
                    </CardContent>
                </Card>

                {/* Skills to Strengthen */}
                <Card className="animate-fade-in" style={{ animationDelay: '300ms' }}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Target className="w-5 h-5 text-rose-500" />
                            Skills to Strengthen
                        </CardTitle>
                        <CardDescription>Areas for growth</CardDescription>
                    </CardHeader>
                    <CardContent className="max-h-80 overflow-y-auto">
                        {renderSkillList(
                            skillsToStrengthen,
                            <TrendingUp className="w-3 h-3 text-rose-500" />,
                            "text-rose-500"
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Career Directions */}
            {careerDirections.length > 0 && (
                <Card className="animate-fade-in" style={{ animationDelay: '400ms' }}>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Compass className="w-5 h-5 text-emerald-500" />
                            Potential Career Directions
                        </CardTitle>
                        <CardDescription>Based on your skill profile</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {careerDirections.map((direction: string, index: number) => {
                                const directionText = typeof direction === 'string' ? direction : String(direction);
                                return (
                                    <div
                                        key={index}
                                        className="p-4 rounded-lg bg-secondary/50 border border-border/50 hover:border-primary/50 transition-colors"
                                    >
                                        <p className="text-sm text-foreground">{directionText}</p>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
