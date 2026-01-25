import { cn } from '@/lib/utils';
import { Skill } from '@/types/career';

interface SkillsOverviewProps {
  skills: Skill[];
  className?: string;
}

const levelWidth = {
  beginner: 'w-1/4',
  intermediate: 'w-2/4',
  advanced: 'w-3/4',
  expert: 'w-full',
};

const levelColor = {
  beginner: 'bg-slate-300',
  intermediate: 'bg-amber-400',
  advanced: 'bg-primary',
  expert: 'bg-primary',
};

export function SkillsOverview({ skills, className }: SkillsOverviewProps) {
  const categories = {
    technical: skills.filter(s => s.category === 'technical'),
    soft: skills.filter(s => s.category === 'soft'),
    leadership: skills.filter(s => s.category === 'leadership'),
  };

  return (
    <div className={cn(
      "bg-card rounded-xl p-6 border border-border shadow-sm animate-fade-in",
      className
    )}>
      <h3 className="font-semibold text-foreground text-lg mb-4">Skills Overview</h3>
      
      <div className="space-y-6">
        {Object.entries(categories).map(([category, categorySkills]) => (
          categorySkills.length > 0 && (
            <div key={category}>
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">
                {category} Skills
              </p>
              <div className="space-y-3">
                {categorySkills.slice(0, 4).map((skill, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-foreground">{skill.name}</span>
                      <span className="text-xs text-muted-foreground capitalize">{skill.level}</span>
                    </div>
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div 
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          levelWidth[skill.level],
                          levelColor[skill.level]
                        )} 
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
}
