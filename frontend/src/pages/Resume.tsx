import { FileText, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import { ResumeUpload } from '../components/resume/ResumeUpload';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { useResumeAnalysis, useSkillsAnalysis, useAnalyzeResume } from '../hooks/useApi';
import { useUser } from '../context/UserContext';

export default function Resume() {
    const { user, hasResume } = useUser();
    const { data: analysisData, isLoading: analysisLoading } = useResumeAnalysis();
    const { data: skillsData, isLoading: skillsLoading } = useSkillsAnalysis();
    const { data: resumeAnalyze, isLoading: resumeLoading } = useAnalyzeResume();

    const isLoading = analysisLoading || skillsLoading || resumeLoading;

    // Helper to safely convert value to string
    const valueToString = (value: unknown, maxLength = 200): string => {
        if (value === null || value === undefined) return '';
        if (typeof value === 'string') return value.slice(0, maxLength);
        if (Array.isArray(value)) {
            // Flatten array items to strings
            const items = value.slice(0, 6).map(v => {
                if (typeof v === 'string') return v;
                if (v && typeof v === 'object') {
                    const obj = v as Record<string, unknown>;
                    return obj.name || obj.title || obj.skill || Object.values(obj).find(x => typeof x === 'string') || '';
                }
                return String(v);
            }).filter(Boolean);
            return items.join(', ');
        }
        if (typeof value === 'object') {
            const obj = value as Record<string, unknown>;

            // If object has arrays of skills, flatten them
            const allValues: string[] = [];
            for (const [key, val] of Object.entries(obj)) {
                if (Array.isArray(val)) {
                    // Extract items from arrays
                    for (const item of val.slice(0, 4)) {
                        if (typeof item === 'string') {
                            allValues.push(item);
                        } else if (item && typeof item === 'object') {
                            const itemObj = item as Record<string, unknown>;
                            const str = itemObj.name || itemObj.title || itemObj.skill;
                            if (typeof str === 'string') allValues.push(str as string);
                        }
                    }
                } else if (typeof val === 'string' && val.length < 100) {
                    allValues.push(val);
                }
            }

            if (allValues.length > 0) {
                return allValues.slice(0, 6).join(', ');
            }

            // Fallback: try direct properties
            if (obj.name) return String(obj.name);
            if (obj.title) return String(obj.title);
            if (obj.value) return String(obj.value);
            if (obj.summary) return String(obj.summary).slice(0, maxLength);

            // Last resort: stringify but make it readable
            const jsonStr = JSON.stringify(value);
            if (jsonStr.length <= maxLength) return jsonStr;
            return jsonStr.slice(0, maxLength) + '...';
        }
        return String(value);
    };

    // Extract analysis highlights from API data
    const getAnalysisHighlights = () => {
        if (!analysisData?.analysis || typeof analysisData.analysis !== 'object') {
            return [
                { label: 'Core Competencies', value: 'Upload resume to analyze' },
                { label: 'Career Pattern', value: 'Upload resume to analyze' },
                { label: 'Unique Value', value: 'Upload resume to analyze' },
            ];
        }

        const analysis = analysisData.analysis as Record<string, unknown>;
        const highlights = [];

        // Try different possible field names for core competencies
        const competencies = analysis.core_competencies || analysis.coreCompetencies ||
            analysis.key_strengths || analysis.keyStrengths ||
            analysis.strengths || analysis.technical_strengths;
        if (competencies) {
            highlights.push({
                label: 'Core Competencies',
                value: valueToString(competencies),
            });
        }

        // Career pattern
        const careerPattern = analysis.career_progression_pattern || analysis.career_pattern ||
            analysis.careerProgressionPattern || analysis.career_trajectory || analysis.experience_summary;
        if (careerPattern) {
            highlights.push({
                label: 'Career Pattern',
                value: valueToString(careerPattern),
            });
        }

        // Unique value proposition
        const uniqueValue = analysis.unique_value_proposition || analysis.unique_value ||
            analysis.uniqueValueProposition || analysis.unique_strengths || analysis.standout_qualities;
        if (uniqueValue) {
            highlights.push({
                label: 'Unique Value',
                value: valueToString(uniqueValue),
            });
        }

        // Add skills if available
        if (skillsData?.skills && typeof skillsData.skills === 'object') {
            const skills = skillsData.skills as Record<string, unknown>;
            const topSkills = skills.top_skills || skills.skills || skills.technical_skills;
            if (topSkills) {
                highlights.push({
                    label: 'Top Skills',
                    value: valueToString(topSkills),
                });
            }
        }

        // If no specific fields found, try to extract any available data
        if (highlights.length === 0) {
            const keys = Object.keys(analysis).slice(0, 3);
            for (const key of keys) {
                highlights.push({
                    label: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
                    value: valueToString(analysis[key]),
                });
            }
        }

        return highlights.length > 0 ? highlights : [
            { label: 'Status', value: 'Analysis available - check dashboard for full results' },
        ];
    };

    // Extract improvement suggestions from API data
    const getImprovements = () => {
        if (!analysisData?.analysis || typeof analysisData.analysis !== 'object') {
            return [
                'Upload your resume to get personalized improvement suggestions',
            ];
        }

        const analysis = analysisData.analysis as Record<string, unknown>;
        const improvements: string[] = [];

        // Check for actionable resume improvements (primary source)
        if (analysis.actionable_resume_improvements || analysis.actionable_improvements ||
            analysis.actionableImprovements || analysis.actionableResumeImprovements) {
            const items = analysis.actionable_resume_improvements || analysis.actionable_improvements ||
                analysis.actionableImprovements || analysis.actionableResumeImprovements;
            if (Array.isArray(items)) {
                // Clean up markdown formatting from the items
                improvements.push(...items.map(item => {
                    const str = String(item);
                    // Remove markdown bold markers
                    return str.replace(/\*\*/g, '').replace(/^[\s-•]*/, '').trim();
                }));
            }
        }

        if (analysis.areas_for_development || analysis.areasForDevelopment) {
            const items = analysis.areas_for_development || analysis.areasForDevelopment;
            if (Array.isArray(items) && improvements.length === 0) {
                improvements.push(...items.map(String));
            }
        }

        if (analysis.suggestions && improvements.length === 0) {
            const items = analysis.suggestions;
            if (Array.isArray(items)) {
                improvements.push(...items.map(String));
            }
        }

        return improvements.length > 0 ? improvements.slice(0, 5) : [
            'Complete your profile for personalized suggestions',
        ];
    };

    // Get resume sections preview
    const getResumeSections = () => {
        if (!resumeAnalyze?.analysis?.sections) {
            return [];
        }
        return resumeAnalyze.analysis.sections;
    };

    const analysisHighlights = getAnalysisHighlights();
    const improvements = getImprovements();
    const resumeSections = getResumeSections();

    return (
        <div className="space-y-6 max-w-4xl">
            {/* Header */}
            <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-foreground">Resume Analysis</h1>
                <p className="text-muted-foreground mt-1">
                    Upload your resume to get AI-powered career insights
                </p>
            </div>

            {/* Upload Section */}
            <ResumeUpload />

            {/* Analysis Results */}
            {(hasResume || analysisData?.analysis) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
                        <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-base">
                                <Sparkles className="w-5 h-5 text-primary" />
                                Key Insights
                                {isLoading && <Loader2 className="w-4 h-4 animate-spin ml-auto" />}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {analysisHighlights.map((item, index) => (
                                <div key={index}>
                                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                        {item.label}
                                    </p>
                                    <p className="text-sm text-foreground mt-1">{item.value}</p>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
                        <CardHeader className="pb-3">
                            <CardTitle className="flex items-center gap-2 text-base">
                                <AlertCircle className="w-5 h-5 text-amber-500" />
                                Suggested Improvements
                                {isLoading && <Loader2 className="w-4 h-4 animate-spin ml-auto" />}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="space-y-3">
                                {improvements.map((item, index) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <span className="w-5 h-5 rounded-full bg-secondary text-muted-foreground text-xs flex items-center justify-center shrink-0 mt-0.5">
                                            {index + 1}
                                        </span>
                                        <span className="text-sm text-foreground">{item}</span>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Resume Preview / Sections */}
            <Card className="animate-fade-in" style={{ animationDelay: '300ms' }}>
                <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base">
                        <FileText className="w-5 h-5 text-muted-foreground" />
                        Resume Preview
                        {resumeLoading && <Loader2 className="w-4 h-4 animate-spin ml-auto" />}
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {resumeSections.length > 0 ? (
                        <div className="space-y-4">
                            {resumeSections.map((section: { section: string; sample: string }, index: number) => (
                                <div key={index} className="border-l-2 border-primary/30 pl-4">
                                    <p className="text-sm font-medium text-foreground">{section.section}</p>
                                    <p className="text-sm text-muted-foreground mt-1 line-clamp-3">
                                        {section.sample}
                                    </p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="h-64 rounded-lg bg-secondary flex items-center justify-center">
                            <p className="text-muted-foreground text-sm">
                                {hasResume ? 'Loading resume sections...' : 'Upload a resume to see the preview'}
                            </p>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
