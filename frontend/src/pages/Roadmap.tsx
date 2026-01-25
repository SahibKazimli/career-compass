import { Target, Calendar, CheckCircle2 } from 'lucide-react';
import { RoadmapTimeline } from '@/components/roadmap/RoadmapTimeline';
import { mockRoadmapSteps, mockRecommendations } from '@/data/mockData';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export default function Roadmap() {
  const activeRecommendation = mockRecommendations[0];
  const completedSteps = mockRoadmapSteps.filter(s => s.status === 'completed').length;
  const totalSteps = mockRoadmapSteps.length;
  const progress = Math.round((completedSteps / totalSteps) * 100);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Career Roadmap</h1>
        <p className="text-muted-foreground mt-1">
          Your personalized path to {activeRecommendation.title}
        </p>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="animate-fade-in">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Target className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Target Role</p>
                <p className="font-semibold text-foreground">{activeRecommendation.title}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center">
                <Calendar className="w-6 h-6 text-accent-foreground" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Est. Timeline</p>
                <p className="font-semibold text-foreground">{activeRecommendation.timeToTransition}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Progress</p>
                <p className="font-semibold text-foreground">{completedSteps} of {totalSteps} steps</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Bar */}
      <div className="animate-fade-in" style={{ animationDelay: '300ms' }}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-foreground">Overall Progress</span>
          <span className="text-sm font-medium text-primary">{progress}%</span>
        </div>
        <div className="h-3 bg-secondary rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="animate-fade-in" style={{ animationDelay: '400ms' }}>
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold text-foreground mb-6">Your Journey</h2>
              <RoadmapTimeline steps={mockRoadmapSteps} />
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card className="animate-fade-in" style={{ animationDelay: '500ms' }}>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-foreground mb-4">Skills to Develop</h3>
              <div className="space-y-2">
                {activeRecommendation.skillsToDevelope.map((skill, index) => (
                  <div 
                    key={index}
                    className={cn(
                      "px-3 py-2 rounded-lg text-sm",
                      index === 0 ? "bg-primary/10 text-primary font-medium" : "bg-secondary text-foreground"
                    )}
                  >
                    {skill}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '600ms' }}>
            <CardContent className="pt-6">
              <h3 className="font-semibold text-foreground mb-4">First Steps</h3>
              <ul className="space-y-3">
                {activeRecommendation.firstSteps.map((step, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <span className="text-sm text-foreground">{step}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
