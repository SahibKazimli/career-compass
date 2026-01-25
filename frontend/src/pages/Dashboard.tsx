import { Target, TrendingUp, BookOpen, Clock } from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { RecommendationCard } from '@/components/dashboard/RecommendationCard';
import { SkillsOverview } from '@/components/dashboard/SkillsOverview';
import { RoadmapTimeline } from '@/components/roadmap/RoadmapTimeline';
import { mockSkills, mockRecommendations, mockRoadmapSteps } from '@/data/mockData';

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Track your career progress and discover new opportunities
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Career Matches"
          value={3}
          subtitle="Based on your profile"
          icon={Target}
        />
        <StatCard
          title="Skills Analyzed"
          value={8}
          subtitle="4 advanced"
          icon={TrendingUp}
          trend={{ value: 12, positive: true }}
        />
        <StatCard
          title="Learning Resources"
          value={24}
          subtitle="Personalized for you"
          icon={BookOpen}
        />
        <StatCard
          title="Est. Transition"
          value="6-12 mo"
          subtitle="To target role"
          icon={Clock}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recommendations Section */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-foreground">Top Career Matches</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {mockRecommendations.slice(0, 2).map((rec, index) => (
              <RecommendationCard 
                key={index} 
                recommendation={rec}
              />
            ))}
          </div>
        </div>

        {/* Skills Overview */}
        <div className="lg:col-span-1">
          <SkillsOverview skills={mockSkills} />
        </div>
      </div>

      {/* Roadmap Preview */}
      <div className="bg-card rounded-xl p-6 border border-border shadow-sm animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Your Career Roadmap</h2>
            <p className="text-sm text-muted-foreground">
              Path to Senior Data Scientist
            </p>
          </div>
          <span className="text-sm text-primary font-medium">
            Step 2 of 5
          </span>
        </div>
        <RoadmapTimeline steps={mockRoadmapSteps.slice(0, 3)} />
      </div>
    </div>
  );
}
