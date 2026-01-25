import { Skill, CareerRecommendation, RoadmapStep } from '@/types/career';

export const mockSkills: Skill[] = [
  { name: 'Python', level: 'advanced', category: 'technical' },
  { name: 'Machine Learning', level: 'intermediate', category: 'technical' },
  { name: 'Data Analysis', level: 'advanced', category: 'technical' },
  { name: 'SQL', level: 'advanced', category: 'technical' },
  { name: 'Communication', level: 'expert', category: 'soft' },
  { name: 'Problem Solving', level: 'advanced', category: 'soft' },
  { name: 'Team Management', level: 'intermediate', category: 'leadership' },
  { name: 'Strategic Planning', level: 'beginner', category: 'leadership' },
];

export const mockRecommendations: CareerRecommendation[] = [
  {
    title: 'Senior Data Scientist',
    matchScore: 87,
    matchReason: 'Your strong foundation in Python and data analysis, combined with growing ML expertise, positions you well for this role. Focus on deepening your statistical modeling skills.',
    estimatedSalary: '$130K - $180K',
    skillsToDevelope: ['Deep Learning', 'MLOps', 'A/B Testing', 'Statistical Modeling'],
    firstSteps: ['Complete a deep learning specialization', 'Build an end-to-end ML project'],
    timeToTransition: '6-12 months',
  },
  {
    title: 'ML Engineering Lead',
    matchScore: 72,
    matchReason: 'Your technical skills combined with emerging leadership abilities make this a natural progression. Need to strengthen MLOps and system design knowledge.',
    estimatedSalary: '$150K - $200K',
    skillsToDevelope: ['System Design', 'MLOps', 'Cloud Architecture', 'Kubernetes'],
    firstSteps: ['Lead a small ML project', 'Get AWS/GCP ML certification'],
    timeToTransition: '12-18 months',
  },
  {
    title: 'AI Product Manager',
    matchScore: 65,
    matchReason: 'Your technical background combined with strong communication skills creates a unique advantage for bridging technical and business teams.',
    estimatedSalary: '$140K - $190K',
    skillsToDevelope: ['Product Strategy', 'Stakeholder Management', 'Roadmap Planning', 'User Research'],
    firstSteps: ['Take a product management course', 'Shadow PMs at your company'],
    timeToTransition: '12-24 months',
  },
];

export const mockRoadmapSteps: RoadmapStep[] = [
  {
    id: '1',
    title: 'Foundation Strengthening',
    description: 'Solidify your core machine learning fundamentals and deepen statistical knowledge.',
    duration: '4 weeks',
    status: 'completed',
    skills: ['Statistics', 'Linear Algebra', 'Probability'],
  },
  {
    id: '2',
    title: 'Deep Learning Mastery',
    description: 'Master neural networks, CNNs, and transformers through hands-on projects.',
    duration: '8 weeks',
    status: 'in-progress',
    skills: ['PyTorch', 'Neural Networks', 'Transformers'],
  },
  {
    id: '3',
    title: 'MLOps & Deployment',
    description: 'Learn to deploy and maintain ML models in production environments.',
    duration: '6 weeks',
    status: 'upcoming',
    skills: ['Docker', 'Kubernetes', 'CI/CD', 'Monitoring'],
  },
  {
    id: '4',
    title: 'Portfolio & Networking',
    description: 'Build impressive projects and connect with industry professionals.',
    duration: '4 weeks',
    status: 'upcoming',
    skills: ['GitHub', 'Technical Writing', 'Networking'],
  },
  {
    id: '5',
    title: 'Interview Preparation',
    description: 'Practice system design, coding challenges, and behavioral interviews.',
    duration: '4 weeks',
    status: 'upcoming',
    skills: ['System Design', 'Algorithms', 'Communication'],
  },
];
