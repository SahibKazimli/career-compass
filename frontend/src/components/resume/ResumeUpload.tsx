import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ResumeUploadProps {
  onUpload?: (file: File) => void;
  className?: string;
}

type UploadState = 'idle' | 'uploading' | 'success' | 'error';

export function ResumeUpload({ onUpload, className }: ResumeUploadProps) {
  const [state, setState] = useState<UploadState>('idle');
  const [fileName, setFileName] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  const handleFile = useCallback((file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setState('error');
      return;
    }

    setFileName(file.name);
    setState('uploading');

    // Simulate upload - in real app, this would call the backend
    setTimeout(() => {
      setState('success');
      onUpload?.(file);
    }, 2000);
  }, [onUpload]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div className={cn("animate-fade-in", className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200",
          dragActive ? "border-primary bg-accent" : "border-border bg-card",
          state === 'success' && "border-primary bg-accent"
        )}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={state === 'uploading'}
        />

        <div className="flex flex-col items-center gap-4">
          {state === 'idle' && (
            <>
              <div className="w-14 h-14 rounded-full bg-secondary flex items-center justify-center">
                <Upload className="w-6 h-6 text-muted-foreground" />
              </div>
              <div>
                <p className="font-medium text-foreground">
                  Drop your resume here, or <span className="text-primary">browse</span>
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  Supports PDF files up to 10MB
                </p>
              </div>
            </>
          )}

          {state === 'uploading' && (
            <>
              <div className="w-14 h-14 rounded-full bg-accent flex items-center justify-center">
                <Loader2 className="w-6 h-6 text-primary animate-spin" />
              </div>
              <div>
                <p className="font-medium text-foreground">Analyzing resume...</p>
                <p className="text-sm text-muted-foreground mt-1">{fileName}</p>
              </div>
            </>
          )}

          {state === 'success' && (
            <>
              <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Resume uploaded successfully!</p>
                <p className="text-sm text-muted-foreground mt-1">{fileName}</p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => { setState('idle'); setFileName(''); }}
                className="mt-2"
              >
                <FileText className="w-4 h-4 mr-2" />
                Upload a different resume
              </Button>
            </>
          )}

          {state === 'error' && (
            <>
              <div className="w-14 h-14 rounded-full bg-destructive/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-destructive" />
              </div>
              <div>
                <p className="font-medium text-destructive">Only PDF files are supported</p>
                <p className="text-sm text-muted-foreground mt-1">Please try again with a PDF file</p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => setState('idle')}
                className="mt-2"
              >
                Try again
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
