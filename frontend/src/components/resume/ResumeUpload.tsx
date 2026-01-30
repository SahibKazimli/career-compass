import { useState, useCallback } from 'react';
import { cn } from '../../lib/utils';
import { Upload, FileText, CheckCircle, Loader2, User, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { useUser } from '../../context/UserContext';
import { useResumeUpload } from '../../hooks/useApi';
import { toast } from 'sonner';

interface ResumeUploadProps {
    className?: string;
}

type UploadState = 'login' | 'idle' | 'uploading' | 'processing' | 'success' | 'error';

export function ResumeUpload({ className }: ResumeUploadProps) {
    const { user, login, isLoading: userLoading } = useUser();
    const { mutateAsync: uploadResume, isPending } = useResumeUpload();

    const [state, setState] = useState<UploadState>(user ? 'idle' : 'login');
    const [fileName, setFileName] = useState<string>('');
    const [dragActive, setDragActive] = useState(false);
    const [processingStep, setProcessingStep] = useState<string>('');
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [errorMessage, setErrorMessage] = useState<string>('');

    // Handle login
    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email || !name) {
            toast.error('Please enter both email and name');
            return;
        }

        try {
            await login(email, name);
            setState('idle');
            toast.success('Welcome to Career Compass!');
        } catch (error) {
            toast.error('Failed to login. Please try again.');
        }
    };

    const handleFile = useCallback(async (file: File) => {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            setState('error');
            setErrorMessage('Only PDF files are supported');
            return;
        }

        if (!user) {
            setState('login');
            return;
        }

        setFileName(file.name);
        setState('processing');
        setProcessingStep('Uploading and analyzing resume...');

        try {
            const result = await uploadResume(file);

            setState('success');
            toast.success(`Resume processed! Found ${result.parsed_data.total_chunks} sections.`);
        } catch (error) {
            setState('error');
            setErrorMessage(error instanceof Error ? error.message : 'Processing failed');
            toast.error('Failed to process resume');
        }
    }, [user, uploadResume]);

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

    const resetUpload = () => {
        setState(user ? 'idle' : 'login');
        setFileName('');
        setProcessingStep('');
        setErrorMessage('');
    };

    // Login form
    if (state === 'login' || (!user && !userLoading)) {
        return (
            <div className={cn("animate-fade-in", className)}>
                <div className="border-2 border-dashed rounded-xl p-8 bg-card border-border">
                    <div className="max-w-md mx-auto">
                        <div className="flex flex-col items-center gap-4 mb-6">
                            <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                                <User className="w-6 h-6 text-primary" />
                            </div>
                            <div className="text-center">
                                <h3 className="font-semibold text-foreground">Welcome to Career Compass</h3>
                                <p className="text-sm text-muted-foreground mt-1">
                                    Enter your details to get started
                                </p>
                            </div>
                        </div>

                        <form onSubmit={handleLogin} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    type="text"
                                    placeholder="Your name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required
                                />
                            </div>
                            <Button type="submit" className="w-full" disabled={userLoading}>
                                {userLoading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Loading...
                                    </>
                                ) : (
                                    'Get Started'
                                )}
                            </Button>
                        </form>
                    </div>
                </div>
            </div>
        );
    }

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
                    disabled={state === 'processing' || isPending}
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
                                {user && (
                                    <p className="text-xs text-muted-foreground mt-2">
                                        Logged in as: <span className="font-medium">{user.name}</span>
                                    </p>
                                )}
                            </div>
                        </>
                    )}

                    {(state === 'uploading' || state === 'processing') && (
                        <>
                            <div className="w-14 h-14 rounded-full bg-accent flex items-center justify-center">
                                <Loader2 className="w-6 h-6 text-primary animate-spin" />
                            </div>
                            <div>
                                <p className="font-medium text-foreground">
                                    {processingStep || 'Processing resume...'}
                                </p>
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
                                <p className="font-medium text-foreground">Resume processed successfully!</p>
                                <p className="text-sm text-muted-foreground mt-1">{fileName}</p>
                            </div>
                            <Button
                                variant="outline"
                                onClick={resetUpload}
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
                                <AlertTriangle className="w-6 h-6 text-destructive" />
                            </div>
                            <div>
                                <p className="font-medium text-destructive">{errorMessage}</p>
                                <p className="text-sm text-muted-foreground mt-1">Please try again</p>
                            </div>
                            <Button
                                variant="outline"
                                onClick={resetUpload}
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
