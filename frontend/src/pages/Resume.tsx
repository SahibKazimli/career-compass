import { FileText, Sparkles, AlertCircle } from 'lucide-react';
import { ResumeUpload } from '@/components/resume/ResumeUpload';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const analysisHighlights = [
  { label: 'Core Competencies', value: 'Python, ML, Data Analysis, SQL' },
  { label: 'Career Pattern', value: 'Progressive technical growth with emerging leadership' },
  { label: 'Unique Value', value: 'Strong technical foundation with excellent communication' },
];

const improvements = [
  'Quantify achievements with specific metrics and numbers',
  'Add more details about ML project outcomes',
  'Include certifications and continuous learning',
  'Highlight leadership and mentoring experiences',
];

export default function Resume() {
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="w-5 h-5 text-primary" />
              Key Insights
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

      {/* Resume Preview Placeholder */}
      <Card className="animate-fade-in" style={{ animationDelay: '300ms' }}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="w-5 h-5 text-muted-foreground" />
            Resume Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 rounded-lg bg-secondary flex items-center justify-center">
            <p className="text-muted-foreground text-sm">
              Upload a resume to see the preview
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
