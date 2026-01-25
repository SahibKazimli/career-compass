import { BookOpen, ExternalLink, Clock, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const resources = [
  {
    id: 1,
    title: 'Deep Learning Specialization',
    provider: 'Coursera',
    skill: 'Deep Learning',
    duration: '4 months',
    rating: 4.8,
    type: 'course',
  },
  {
    id: 2,
    title: 'MLOps Fundamentals',
    provider: 'Google Cloud',
    skill: 'MLOps',
    duration: '6 weeks',
    rating: 4.6,
    type: 'course',
  },
  {
    id: 3,
    title: 'System Design for ML',
    provider: 'Educative',
    skill: 'System Design',
    duration: '3 weeks',
    rating: 4.7,
    type: 'course',
  },
  {
    id: 4,
    title: 'AWS Machine Learning Specialty',
    provider: 'AWS',
    skill: 'Cloud Architecture',
    duration: '2 months',
    rating: 4.5,
    type: 'certification',
  },
  {
    id: 5,
    title: 'Hands-On Machine Learning',
    provider: "O'Reilly",
    skill: 'Machine Learning',
    duration: 'Self-paced',
    rating: 4.9,
    type: 'book',
  },
  {
    id: 6,
    title: 'Full Stack Deep Learning',
    provider: 'FSDL',
    skill: 'MLOps',
    duration: '8 weeks',
    rating: 4.8,
    type: 'bootcamp',
  },
];

const typeStyles = {
  course: 'bg-primary/10 text-primary',
  certification: 'bg-amber-500/10 text-amber-600',
  book: 'bg-purple-500/10 text-purple-600',
  bootcamp: 'bg-emerald-500/10 text-emerald-600',
};

export default function Resources() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Learning Resources</h1>
        <p className="text-muted-foreground mt-1">
          Curated resources to accelerate your career transition
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 animate-fade-in" style={{ animationDelay: '100ms' }}>
        {['All', 'Courses', 'Certifications', 'Books', 'Bootcamps'].map((filter, index) => (
          <Button
            key={filter}
            variant={index === 0 ? 'default' : 'outline'}
            size="sm"
            className={index === 0 ? '' : 'border-border'}
          >
            {filter}
          </Button>
        ))}
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {resources.map((resource, index) => (
          <Card 
            key={resource.id}
            className="group hover:shadow-md transition-shadow animate-fade-in"
            style={{ animationDelay: `${150 + index * 50}ms` }}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <span className={cn(
                  "text-xs px-2 py-1 rounded-full capitalize font-medium",
                  typeStyles[resource.type as keyof typeof typeStyles]
                )}>
                  {resource.type}
                </span>
                <div className="flex items-center gap-1 text-amber-500">
                  <Star className="w-4 h-4 fill-current" />
                  <span className="text-sm font-medium">{resource.rating}</span>
                </div>
              </div>
              <CardTitle className="text-base mt-2 group-hover:text-primary transition-colors">
                {resource.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{resource.provider}</span>
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    {resource.duration}
                  </div>
                </div>
                
                <div className="flex items-center justify-between pt-3 border-t border-border">
                  <span className="text-xs px-2 py-1 bg-accent text-accent-foreground rounded">
                    {resource.skill}
                  </span>
                  <Button variant="ghost" size="sm" className="text-primary hover:text-primary">
                    View <ExternalLink className="w-3 h-3 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* CTA Section */}
      <Card className="bg-accent border-0 animate-fade-in" style={{ animationDelay: '500ms' }}>
        <CardContent className="py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Need personalized recommendations?</h3>
                <p className="text-sm text-muted-foreground">
                  Get AI-powered resource suggestions based on your goals
                </p>
              </div>
            </div>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
              Get Recommendations
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
