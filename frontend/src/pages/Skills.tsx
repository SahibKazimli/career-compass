import { TrendingUp, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { mockSkills, mockRecommendations } from '@/data/mockData';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const skillGaps = [
  { skill: 'Deep Learning', priority: 'high', timeframe: '8 weeks' },
  { skill: 'MLOps', priority: 'high', timeframe: '6 weeks' },
  { skill: 'System Design', priority: 'medium', timeframe: '4 weeks' },
  { skill: 'Cloud Architecture', priority: 'medium', timeframe: '4 weeks' },
];

const priorityStyles = {
  high: 'bg-primary/10 text-primary border-primary/20',
  medium: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  low: 'bg-secondary text-muted-foreground border-border',
};

const levelPercent = {
  beginner: 25,
  intermediate: 50,
  advanced: 75,
  expert: 100,
};

export default function Skills() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Skills Analysis</h1>
        <p className="text-muted-foreground mt-1">
          Understanding your strengths and areas for growth
        </p>
      </div>

      {/* Skills Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Skills */}
        <Card className="animate-fade-in">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-primary" />
              Your Skills
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockSkills.map((skill, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-foreground">{skill.name}</span>
                    <span className={cn(
                      "text-xs px-2 py-0.5 rounded-full capitalize",
                      skill.category === 'technical' && "bg-primary/10 text-primary",
                      skill.category === 'soft' && "bg-amber-500/10 text-amber-600",
                      skill.category === 'leadership' && "bg-purple-500/10 text-purple-600"
                    )}>
                      {skill.category}
                    </span>
                  </div>
                  <span className="text-sm text-muted-foreground capitalize">{skill.level}</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div 
                    className={cn(
                      "h-full rounded-full transition-all duration-700",
                      skill.level === 'expert' ? "bg-primary" : 
                      skill.level === 'advanced' ? "bg-primary" :
                      skill.level === 'intermediate' ? "bg-amber-400" : "bg-slate-300"
                    )}
                    style={{ 
                      width: `${levelPercent[skill.level]}%`,
                      animationDelay: `${index * 100}ms`
                    }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Skill Gaps */}
        <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              Skills to Develop
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {skillGaps.map((gap, index) => (
              <div 
                key={index}
                className={cn(
                  "p-4 rounded-lg border",
                  priorityStyles[gap.priority as keyof typeof priorityStyles]
                )}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{gap.skill}</p>
                    <p className="text-sm opacity-80">Est. {gap.timeframe} to learn</p>
                  </div>
                  <span className={cn(
                    "text-xs px-2 py-1 rounded-full uppercase font-medium",
                    gap.priority === 'high' && "bg-primary text-primary-foreground",
                    gap.priority === 'medium' && "bg-amber-500 text-white",
                    gap.priority === 'low' && "bg-secondary text-muted-foreground"
                  )}>
                    {gap.priority}
                  </span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Readiness Score */}
      <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <div className="relative w-24 h-24">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    className="text-secondary"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${mockRecommendations[0].matchScore * 2.51} 251`}
                    className="text-primary transition-all duration-1000"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-foreground">
                  {mockRecommendations[0].matchScore}%
                </span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">Role Readiness</h3>
                <p className="text-muted-foreground">
                  Your current match for {mockRecommendations[0].title}
                </p>
              </div>
            </div>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
              View Full Roadmap <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Skill Categories Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Technical Skills', count: mockSkills.filter(s => s.category === 'technical').length, icon: TrendingUp, color: 'text-primary' },
          { label: 'Soft Skills', count: mockSkills.filter(s => s.category === 'soft').length, icon: CheckCircle, color: 'text-amber-500' },
          { label: 'Leadership', count: mockSkills.filter(s => s.category === 'leadership').length, icon: TrendingUp, color: 'text-purple-500' },
        ].map((category, index) => (
          <Card 
            key={index} 
            className="animate-fade-in" 
            style={{ animationDelay: `${300 + index * 100}ms` }}
          >
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{category.label}</p>
                  <p className="text-3xl font-bold text-foreground">{category.count}</p>
                </div>
                <category.icon className={cn("w-8 h-8", category.color)} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
