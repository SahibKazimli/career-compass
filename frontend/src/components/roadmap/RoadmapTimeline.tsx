import { cn } from '@/lib/utils';
import { Check, Clock, Circle } from 'lucide-react';
import { RoadmapStep } from '@/types/career';

interface RoadmapTimelineProps {
  steps: RoadmapStep[];
  className?: string;
}

const statusIcons = {
  completed: Check,
  'in-progress': Clock,
  upcoming: Circle,
};

const statusStyles = {
  completed: 'bg-primary text-primary-foreground',
  'in-progress': 'bg-accent text-primary border-2 border-primary',
  upcoming: 'bg-secondary text-muted-foreground',
};

const lineStyles = {
  completed: 'bg-primary',
  'in-progress': 'bg-primary',
  upcoming: 'bg-border',
};

export function RoadmapTimeline({ steps, className }: RoadmapTimelineProps) {
  return (
    <div className={cn("relative", className)}>
      {steps.map((step, index) => {
        const Icon = statusIcons[step.status];
        const isLast = index === steps.length - 1;

        return (
          <div 
            key={step.id} 
            className={cn(
              "relative pl-12 pb-8 animate-fade-in",
              isLast && "pb-0"
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            {/* Vertical line */}
            {!isLast && (
              <div 
                className={cn(
                  "absolute left-[18px] top-10 w-0.5 h-[calc(100%-24px)]",
                  lineStyles[step.status]
                )}
              />
            )}

            {/* Icon */}
            <div 
              className={cn(
                "absolute left-0 w-9 h-9 rounded-full flex items-center justify-center",
                statusStyles[step.status]
              )}
            >
              <Icon className="w-4 h-4" />
            </div>

            {/* Content */}
            <div className={cn(
              "bg-card rounded-xl p-5 border border-border shadow-sm",
              step.status === 'in-progress' && "border-primary"
            )}>
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-foreground">{step.title}</h4>
                <span className={cn(
                  "text-xs px-2 py-1 rounded-full capitalize",
                  step.status === 'completed' && "bg-primary/10 text-primary",
                  step.status === 'in-progress' && "bg-primary/10 text-primary animate-pulse-subtle",
                  step.status === 'upcoming' && "bg-secondary text-muted-foreground"
                )}>
                  {step.status === 'in-progress' ? 'In Progress' : step.status}
                </span>
              </div>

              <p className="text-sm text-muted-foreground mb-3">
                {step.description}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex flex-wrap gap-1.5">
                  {step.skills.map((skill, idx) => (
                    <span 
                      key={idx}
                      className="px-2 py-0.5 bg-accent text-accent-foreground text-xs rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap ml-4">
                  {step.duration}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
