import { User, Bell, Shield, Link2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

export default function Settings() {
  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account and preferences
        </p>
      </div>

      {/* Profile Section */}
      <Card className="animate-fade-in">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5 text-muted-foreground" />
            Profile
          </CardTitle>
          <CardDescription>Update your personal information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" defaultValue="John Doe" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" defaultValue="john@example.com" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="current-role">Current Role</Label>
              <Input id="current-role" defaultValue="Data Analyst" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="target-role">Target Role</Label>
              <Input id="target-role" defaultValue="Senior Data Scientist" />
            </div>
          </div>
          <Button className="bg-primary text-primary-foreground">Save Changes</Button>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card className="animate-fade-in" style={{ animationDelay: '100ms' }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-muted-foreground" />
            Notifications
          </CardTitle>
          <CardDescription>Configure how you receive updates</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { label: 'Email notifications', description: 'Receive updates via email' },
            { label: 'Progress reminders', description: 'Get reminded about your learning goals' },
            { label: 'New recommendations', description: 'Be notified when new career paths are found' },
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-foreground">{item.label}</p>
                <p className="text-sm text-muted-foreground">{item.description}</p>
              </div>
              <Switch defaultChecked={index < 2} />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* API Integration */}
      <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Link2 className="w-5 h-5 text-muted-foreground" />
            API Integration
          </CardTitle>
          <CardDescription>Connect to your backend service</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-url">Backend URL</Label>
            <Input id="api-url" placeholder="http://localhost:8000" />
          </div>
          <div className="flex gap-2">
            <Button variant="outline">Test Connection</Button>
            <Button className="bg-primary text-primary-foreground">Save</Button>
          </div>
        </CardContent>
      </Card>

      {/* Privacy */}
      <Card className="animate-fade-in" style={{ animationDelay: '300ms' }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-muted-foreground" />
            Privacy & Security
          </CardTitle>
          <CardDescription>Manage your data and security settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-foreground">Data sharing</p>
              <p className="text-sm text-muted-foreground">Allow anonymous data for improving recommendations</p>
            </div>
            <Switch />
          </div>
          <div className="pt-4 border-t border-border">
            <Button variant="outline" className="text-destructive border-destructive/30 hover:bg-destructive/10">
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
