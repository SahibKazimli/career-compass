import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useUser } from '../context/UserContext';
import { getAccessToken } from '../services/api';
import {
    BookOpen,
    Loader2,
    ExternalLink,
    Clock,
    Zap,
    Play,
    Book,
    Code,
    Award,
    ChevronDown,
    ChevronUp,
    AlertCircle,
    HelpCircle
} from 'lucide-react';

// Debug function
const debug = (...args: any[]) => {
    console.log('Resources Debug:', ...args);
};

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

interface Resource {
    name: string;
    url?: string;
    url_or_info?: string;
    type?: string;
    description: string;
    platform?: string;
    price_range?: string;
    author?: string;
    difficulty?: string;
}

interface LearningPlanItem {
    skill: string;
    priority: string;
    estimated_time: string;
    resources: {
        free?: Resource[];
        premium?: Resource[];
        books?: Resource[];
        projects?: Resource[];
        certifications?: Resource[];
    };
}

// Error Boundary for the page
function ResourcesErrorFallback({ error, onRetry }: { error: Error; onRetry: () => void }) {
    return (
        <div className="p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-600 mb-2">Error Loading Resources</h2>
            <p className="text-muted-foreground mb-4">{error.message}</p>
            <div className="flex gap-2 justify-center">
                <button 
                    onClick={onRetry} 
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
                >
                    Try Again
                </button>
                <button 
                    onClick={() => window.location.reload()} 
                    className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90"
                >
                    Reload Page
                </button>
            </div>
        </div>
    );
}

export default function Resources() {
    const { user } = useUser();
    const [isLoading, setIsLoading] = useState(false);
    const [resources, setResources] = useState<{
        learning_plan?: LearningPlanItem[];
        recommended_learning_path?: { order: number; skill: string; duration: string; reason: string }[];
        quick_wins?: string[];
        summary?: string;
    } | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [fetchError, setFetchError] = useState<Error | null>(null);
    const [expandedSkills, setExpandedSkills] = useState<Set<number>>(new Set([0]));
    const [timeCommitment, setTimeCommitment] = useState<'low' | 'medium' | 'high'>('medium');

    const fetchResources = async () => {
        debug('=== FETCH RESOURCES CALLED ===');
        debug('User:', user);
        
        if (!user?.user_id) {
            setError('Please log in to generate resources');
            debug('No user ID - aborting');
            return;
        }

        setIsLoading(true);
        setError(null);
        setFetchError(null);

        try {
            debug('Getting access token...');
            const token = getAccessToken();
            debug('Access token:', token ? 'FOUND' : 'NOT FOUND');
            
            if (!token) {
                throw new Error('No authentication token found. Please log in again.');
            }

            debug('Calling API...');
            const response = await fetch(
                `${API_BASE}/resources/${user.user_id}?time_commitment=${timeCommitment}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            debug('API response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                debug('API error response:', errorText);
                
                if (response.status === 404) {
                    throw new Error('No skills analysis found. Please upload a resume first.');
                } else if (response.status === 401) {
                    throw new Error('Session expired. Please log in again.');
                } else {
                    throw new Error(`Failed to fetch resources: ${response.status} ${errorText}`);
                }
            }

            const data = await response.json();
            debug('API data received:', data);
            
            // Validate data structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format from server');
            }
            
            debug('Setting resources...');
            setResources(data.resources || data);
        } catch (err) {
            console.error('Error fetching resources:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to load resources';
            setError(errorMessage);
            setFetchError(err instanceof Error ? err : new Error(errorMessage));
        } finally {
            setIsLoading(false);
            debug('Fetch complete, loading:', isLoading);
        }
    };

    const toggleSkill = (index: number) => {
        const newExpanded = new Set(expandedSkills);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedSkills(newExpanded);
    };

    const getTypeIcon = (type: string) => {
        switch (type?.toLowerCase()) {
            case 'video': return <Play className="w-4 h-4" />;
            case 'docs':
            case 'documentation': return <Book className="w-4 h-4" />;
            case 'tutorial':
            case 'article': return <BookOpen className="w-4 h-4" />;
            default: return <ExternalLink className="w-4 h-4" />;
        }
    };

    // If there was a fatal error during fetch, show error fallback
    if (fetchError && !resources) {
        return (
            <div className="space-y-6 max-w-5xl">
                <div className="animate-fade-in">
                    <h1 className="text-2xl font-bold text-foreground">Learning Resources</h1>
                    <p className="text-muted-foreground mt-1">
                        AI-curated resources tailored to your skill gaps
                    </p>
                </div>
                <ResourcesErrorFallback 
                    error={fetchError} 
                    onRetry={() => {
                        setFetchError(null);
                        fetchResources();
                    }} 
                />
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-5xl">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-foreground">Learning Resources</h1>
                <p className="text-muted-foreground mt-1">
                    AI-curated resources tailored to your skill gaps
                </p>
            </div>

            {/* Generation Controls */}
            <Card className="animate-fade-in">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Zap className="w-5 h-5 text-primary" />
                        Generate Your Learning Plan
                    </CardTitle>
                    <CardDescription>
                        Get personalized resources based on your skills analysis
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">Time commitment:</span>
                            <div className="flex gap-1">
                                {(['low', 'medium', 'high'] as const).map((level) => (
                                    <button
                                        key={level}
                                        onClick={() => setTimeCommitment(level)}
                                        className={`px-3 py-1 text-sm rounded-full transition-colors ${timeCommitment === level
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
                                            }`}
                                    >
                                        {level.charAt(0).toUpperCase() + level.slice(1)}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <Button onClick={fetchResources} disabled={isLoading || !user?.user_id}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <BookOpen className="w-4 h-4 mr-2" />
                                    Generate Resources
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Debug Info */}
            {resources && (
                <div className="p-4 rounded-lg bg-blue-50 border border-blue-200 text-sm">
                    <p className="font-semibold text-blue-700 mb-2">Debug Info:</p>
                    <p className="text-blue-600">Resources loaded: {resources.learning_plan ? resources.learning_plan.length : 0} items</p>
                    <p className="text-blue-600">Has quick_wins: {resources.quick_wins ? 'Yes' : 'No'}</p>
                    <p className="text-blue-600">Has summary: {resources.summary ? 'Yes' : 'No'}</p>
                    <p className="text-blue-600">User ID: {user?.user_id || 'Unknown'}</p>
                    <p className="text-blue-600">Time commitment: {timeCommitment}</p>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-5 h-5" />
                        <span className="font-semibold">Error</span>
                    </div>
                    <p>{error}</p>
                    <button 
                        onClick={() => {
                            setError(null);
                            fetchResources();
                        }}
                        className="mt-3 px-3 py-1 text-sm bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
                    >
                        Retry
                    </button>
                </div>
            )}

            {/* Quick Wins */}
            {resources?.quick_wins && Array.isArray(resources.quick_wins) && resources.quick_wins.length > 0 && (
                <Card className="animate-fade-in border-primary/50">
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2 text-base">
                            <Zap className="w-5 h-5 text-amber-500" />
                            Quick Wins
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {resources.quick_wins.map((win, index) => (
                                <li key={index} className="flex items-start gap-2 text-sm">
                                    <span className="text-amber-500 mt-1">→</span>
                                    <span>{typeof win === 'string' ? win : String(win)}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}

            {/* Learning Plan */}
            {resources?.learning_plan && Array.isArray(resources.learning_plan) && resources.learning_plan.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-foreground">Your Learning Plan</h2>
                    {resources.learning_plan.map((item, index) => (
                        <Card key={index} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                            <CardHeader
                                className="cursor-pointer hover:bg-secondary/30 transition-colors"
                                onClick={() => toggleSkill(index)}
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle className="flex items-center gap-2 text-base">
                                            <span className={`px-2 py-0.5 text-xs rounded-full ${item.priority === 'High' ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400' :
                                                    item.priority === 'Medium' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400' :
                                                        'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400'
                                                }`}>
                                                {item.priority}
                                            </span>
                                            {item.skill}
                                        </CardTitle>
                                        <CardDescription className="flex items-center gap-2 mt-1">
                                            <Clock className="w-3 h-3" />
                                            {item.estimated_time}
                                        </CardDescription>
                                    </div>
                                    {expandedSkills.has(index) ? (
                                        <ChevronUp className="w-5 h-5 text-muted-foreground" />
                                    ) : (
                                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                                    )}
                                </div>
                            </CardHeader>

                            {expandedSkills.has(index) && (
                                <CardContent className="pt-0 space-y-4">
                                    {/* Free Resources */}
                                    {item.resources?.free && Array.isArray(item.resources.free) && item.resources.free.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                                                <span className="text-green-500">●</span> Free Resources
                                            </h4>
                                            <div className="space-y-2">
                                                {item.resources.free.map((res, i) => (
                                                    <div key={i} className="p-3 rounded-lg bg-secondary/50 flex items-start gap-3">
                                                        <span className="text-muted-foreground mt-0.5">
                                                            {getTypeIcon(res?.type || '')}
                                                        </span>
                                                        <div className="flex-1">
                                                            <p className="text-sm font-medium">{res?.name || 'Unnamed Resource'}</p>
                                                            <p className="text-xs text-muted-foreground">{res?.description || 'No description'}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Premium Courses */}
                                    {item.resources?.premium && Array.isArray(item.resources.premium) && item.resources.premium.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                                                <span className="text-purple-500">●</span> Premium Courses
                                            </h4>
                                            <div className="space-y-2">
                                                {item.resources.premium.map((res, i) => (
                                                    <div key={i} className="p-3 rounded-lg bg-secondary/50 flex items-start gap-3">
                                                        <Award className="w-4 h-4 text-purple-500 mt-0.5" />
                                                        <div className="flex-1">
                                                            <p className="text-sm font-medium">{res?.name || 'Unnamed Course'}</p>
                                                            <p className="text-xs text-muted-foreground">
                                                                {res?.platform || 'Unknown platform'} {res?.price_range && `• ${res.price_range}`}
                                                            </p>
                                                            <p className="text-xs text-muted-foreground">{res?.description || 'No description'}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Projects */}
                                    {item.resources?.projects && Array.isArray(item.resources.projects) && item.resources.projects.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                                                <span className="text-blue-500">●</span> Hands-on Projects
                                            </h4>
                                            <div className="space-y-2">
                                                {item.resources.projects.map((res, i) => (
                                                    <div key={i} className="p-3 rounded-lg bg-secondary/50 flex items-start gap-3">
                                                        <Code className="w-4 h-4 text-blue-500 mt-0.5" />
                                                        <div className="flex-1">
                                                            <p className="text-sm font-medium">{res?.name || 'Unnamed Project'}</p>
                                                            <p className="text-xs text-muted-foreground">{res?.description || 'No description'}</p>
                                                            {res?.difficulty && (
                                                                <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400">
                                                                    {res.difficulty}
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            )}
                        </Card>
                    ))}
                </div>
            )}

            {/* Summary */}
            {resources?.summary && typeof resources.summary === 'string' && (
                <Card className="animate-fade-in">
                    <CardHeader>
                        <CardTitle className="text-base">Learning Strategy</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">{resources.summary}</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
