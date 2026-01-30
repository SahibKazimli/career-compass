export interface Skill {
    name: string;
    level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    category: 'technical' | 'soft' | 'leadership';
}

export interface SkillGap {
    skill: string;
    priority: 'high' | 'medium' | 'low';
    timeframe: string;
}

export interface CareerRecommendation {
    title: string;
    matchScore: number;
    matchReason: string;
    estimatedSalary: string;
    skillsToDevelope: string[];
    firstSteps: string[];
    timeToTransition: string;
}

export interface LearningResource {
    skill: string;
    resources: string[];
}

export interface ResumeAnalysis {
    coreCompetencies: string[];
    careerProgressionPattern: string;
    leadershipQualities: string[];
    uniqueValueProposition: string;
    potentialCareerPivots: string[];
    strengthsToLeverage: string[];
    areasForDevelopment: string[];
    actionableImprovements: string[];
}

export interface RoadmapStep {
    id: string;
    title: string;
    description: string;
    duration: string;
    status: 'completed' | 'in-progress' | 'upcoming';
    skills: string[];
}

export interface UserProfile {
    id: number;
    name: string;
    email: string;
    currentRole?: string;
    targetRole?: string;
    resumeUploaded: boolean;
}
