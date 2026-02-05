import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useUser } from '../context/UserContext';
import { getAccessToken } from '../services/api';
import {
    Briefcase,
    Loader2,
    TrendingUp,
    Target,
    Clock,
    DollarSign,
    Flame,
    ChevronDown,
    ChevronUp,
    ArrowRight,
    Sparkles,
    AlertCircle
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

interface CareerMatch {
    title: string;
    match_score: number;
    match_type: 'direct' | 'stretch' | 'pivot';
    match_reason: string;
    industry?: string;
    transferable_skills: string[];
    skills_to_acquire: string[];
    experience_leverage?: string;
    transition_timeline: string;
    salary_range?: {
        entry?: string;
        mid?: string;
        senior?: string;
    };
    job_market_demand: 'Hot' | 'Warm' | 'Cool';
    growth_outlook?: string;
    first_steps: { step: number; action: string; timeline: string }[];
    success_stories?: string;
}

interface CareerMatchResponse {
    profile_summary?: string;
    career_matches: CareerMatch[];
    recommended_focus?: string;
    quick_wins?: string[];
    skills_with_highest_roi?: string[];
}

export default function Careers() {
    const { user } = useUser();
    const [isLoading, setIsLoading] = useState(false);
    const [careers, setCareers] = useState<CareerMatchResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [expandedCareers, setExpandedCareers] = useState<Set<number>>(new Set([0]));

    const fetchCareers = async () => {
        if (!user?.user_id) return;

        setIsLoading(true);
        setError(null);

        try {
            const token = getAccessToken();
            const response = await fetch(
                `${API_BASE}/careers/${user.user_id}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to fetch career matches');
            }

            const data = await response.json();
            setCareers(data.career_matches);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load career matches');
        } finally {
            setIsLoading(false);
        }
    };

    const toggleCareer = (index: number) => {
        const newExpanded = new Set(expandedCareers);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedCareers(newExpanded);
    };

    const getMatchTypeColor = (type: string) => {
        switch (type) {
            case 'direct': return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400';
            case 'stretch': return 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400';
            case 'pivot': return 'bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-400';
            default: return 'bg-secondary text-foreground';
        }
    };

    const getDemandIcon = (demand: string) => {
        switch (demand) {
            case 'Hot': return <Flame className="w-4 h-4 text-red-500" />;
            case 'Warm': return <TrendingUp className="w-4 h-4 text-amber-500" />;
            case 'Cool': return <Target className="w-4 h-4 text-blue-500" />;
            default: return null;
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-500';
        if (score >= 60) return 'text-amber-500';
        return 'text-blue-500';
    };

    return (
        <div className="space-y-6 max-w-5xl">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-foreground">Career Matching</h1>
                <p className="text-muted-foreground mt-1">
                    AI-powered career path recommendations based on your profile
                </p>
            </div>

            {/* Generate Button */}
            <Card className="animate-fade-in">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-primary" />
                        Discover Your Career Paths
                    </CardTitle>
                    <CardDescription>
                        Get personalized career matches based on your skills and experience
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Button onClick={fetchCareers} disabled={isLoading} size="lg">
                        {isLoading ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Briefcase className="w-4 h-4 mr-2" />
                                Find Career Matches
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {/* Error */}
            {error && (
                <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    {error}
                </div>
            )}

            {/* Profile Summary */}
            {careers?.profile_summary && (
                <Card className="animate-fade-in border-primary/50">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-base">Your Profile Assessment</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">{careers.profile_summary}</p>
                    </CardContent>
                </Card>
            )}

            {/* Quick Wins & High ROI Skills */}
            {(careers?.quick_wins || careers?.skills_with_highest_roi) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {careers.quick_wins && careers.quick_wins.length > 0 && (
                        <Card className="animate-fade-in">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm flex items-center gap-2">
                                    <Target className="w-4 h-4 text-green-500" />
                                    Quick Wins
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-1">
                                    {careers.quick_wins.slice(0, 3).map((win, i) => (
                                        <li key={i} className="text-xs text-muted-foreground flex items-start gap-1">
                                            <span className="text-green-500">→</span>
                                            {win}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    )}
                    {careers.skills_with_highest_roi && careers.skills_with_highest_roi.length > 0 && (
                        <Card className="animate-fade-in">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-amber-500" />
                                    Highest ROI Skills
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-1">
                                    {careers.skills_with_highest_roi.slice(0, 5).map((skill, i) => (
                                        <span key={i} className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400">
                                            {skill}
                                        </span>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            )}

            {/* Career Matches */}
            {careers?.career_matches && careers.career_matches.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-foreground">Your Career Matches</h2>
                    {careers.career_matches.map((career, index) => (
                        <Card key={index} className="animate-fade-in overflow-hidden" style={{ animationDelay: `${index * 100}ms` }}>
                            <CardHeader
                                className="cursor-pointer hover:bg-secondary/30 transition-colors"
                                onClick={() => toggleCareer(index)}
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 flex-wrap mb-1">
                                            <span className={`text-2xl font-bold ${getScoreColor(career.match_score)}`}>
                                                {career.match_score}%
                                            </span>
                                            <span className={`px-2 py-0.5 text-xs rounded-full ${getMatchTypeColor(career.match_type)}`}>
                                                {career.match_type}
                                            </span>
                                            <span className="flex items-center gap-1 text-xs text-muted-foreground">
                                                {getDemandIcon(career.job_market_demand)}
                                                {career.job_market_demand}
                                            </span>
                                        </div>
                                        <CardTitle className="text-lg">{career.title}</CardTitle>
                                        <CardDescription className="mt-1">{career.match_reason}</CardDescription>
                                    </div>
                                    {expandedCareers.has(index) ? (
                                        <ChevronUp className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                                    ) : (
                                        <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                                    )}
                                </div>
                            </CardHeader>

                            {expandedCareers.has(index) && (
                                <CardContent className="pt-0 space-y-4 border-t border-border/50">
                                    {/* Key Info */}
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
                                        <div className="flex items-center gap-2">
                                            <Clock className="w-4 h-4 text-muted-foreground" />
                                            <div>
                                                <p className="text-xs text-muted-foreground">Timeline</p>
                                                <p className="text-sm font-medium">{career.transition_timeline}</p>
                                            </div>
                                        </div>
                                        {career.salary_range?.mid && (
                                            <div className="flex items-center gap-2">
                                                <DollarSign className="w-4 h-4 text-muted-foreground" />
                                                <div>
                                                    <p className="text-xs text-muted-foreground">Mid Salary</p>
                                                    <p className="text-sm font-medium">{career.salary_range.mid}</p>
                                                </div>
                                            </div>
                                        )}
                                        {career.industry && (
                                            <div className="flex items-center gap-2">
                                                <Briefcase className="w-4 h-4 text-muted-foreground" />
                                                <div>
                                                    <p className="text-xs text-muted-foreground">Industry</p>
                                                    <p className="text-sm font-medium">{career.industry}</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Skills */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <h4 className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">
                                                ✓ Your Transferable Skills
                                            </h4>
                                            <div className="flex flex-wrap gap-1">
                                                {career.transferable_skills.slice(0, 6).map((skill, i) => (
                                                    <span key={i} className="text-xs px-2 py-1 rounded bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400">
                                                        {skill}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-medium text-amber-600 dark:text-amber-400 mb-2">
                                                ↑ Skills to Develop
                                            </h4>
                                            <div className="flex flex-wrap gap-1">
                                                {career.skills_to_acquire.slice(0, 6).map((skill, i) => (
                                                    <span key={i} className="text-xs px-2 py-1 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400">
                                                        {skill}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* First Steps */}
                                    {career.first_steps && career.first_steps.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                                                <ArrowRight className="w-4 h-4" />
                                                First Steps
                                            </h4>
                                            <div className="space-y-2">
                                                {career.first_steps.map((step, i) => (
                                                    <div key={i} className="flex items-start gap-3 p-2 rounded-lg bg-secondary/50">
                                                        <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium shrink-0">
                                                            {step.step}
                                                        </span>
                                                        <div>
                                                            <p className="text-sm">{step.action}</p>
                                                            <p className="text-xs text-muted-foreground">{step.timeline}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Growth Outlook */}
                                    {career.growth_outlook && (
                                        <div className="p-3 rounded-lg bg-secondary/30">
                                            <h4 className="text-xs font-medium text-muted-foreground mb-1">Growth Outlook</h4>
                                            <p className="text-sm">{career.growth_outlook}</p>
                                        </div>
                                    )}
                                </CardContent>
                            )}
                        </Card>
                    ))}
                </div>
            )}

            {/* Recommended Focus */}
            {careers?.recommended_focus && (
                <Card className="animate-fade-in">
                    <CardHeader>
                        <CardTitle className="text-base flex items-center gap-2">
                            <Target className="w-5 h-5 text-primary" />
                            Recommended Focus
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">{careers.recommended_focus}</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
