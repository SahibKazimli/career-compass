import { cn } from '@/lib/utils';
import { ArrowRight, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CareerRecommendation } from '@/types/career';

interface RecommendationCardProps {
  recommendation: CareerRecommendation;
  className?: string;
}

export function RecommendationCard({ recommendation, className }: RecommendationCardProps) {
  const matchColor = recommendation.matchScore >= 80 
    ? 'text-primary' 
    : recommendation.matchScore >= 60 
    ? 'text-amber-500' 
    : 'text-muted-foreground';

  return (
    <div className={cn(
      "bg-card rounded-xl p-6 border border-border shadow-sm hover:shadow-md transition-shadow animate-fade-in",
      className
    )}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-foreground text-lg">{recommendation.title}</h3>
          <p className="text-sm text-muted-foreground">{recommendation.estimatedSalary}</p>
        </div>
        <div className={cn("flex items-center gap-1 font-bold text-lg", matchColor)}>
          <TrendingUp className="w-5 h-5" />
          {recommendation.matchScore}%
        </div>
      </div>

      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
        {recommendation.matchReason}
      </p>

      <div className="mb-4">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
          Skills to develop
        </p>
        <div className="flex flex-wrap gap-2">
          {recommendation.skillsToDevelope.slice(0, 3).map((skill, index) => (
            <span 
              key={index}
              className="px-2 py-1 bg-accent text-accent-foreground text-xs rounded-md"
            >
              {skill}
            </span>
          ))}
          {recommendation.skillsToDevelope.length > 3 && (
            <span className="px-2 py-1 text-xs text-muted-foreground">
              +{recommendation.skillsToDevelope.length - 3} more
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-border">
        <span className="text-xs text-muted-foreground">
          Est. transition: {recommendation.timeToTransition}
        </span>
        <Button variant="ghost" size="sm" className="text-primary hover:text-primary">
          View Roadmap <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}
