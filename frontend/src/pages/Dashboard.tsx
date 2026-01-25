import { User, FileText, Compass } from "lucide-react";

const stats = [
  { label: "Profile Status", value: "Complete", icon: User, color: "text-emerald-600" },
  { label: "Resumes Uploaded", value: "1", icon: FileText, color: "text-blue-600" },
  { label: "Career Paths", value: "5", icon: Compass, color: "text-violet-600" },
];

export function Dashboard() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's your career overview.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white p-6 rounded-xl border border-border shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold text-foreground mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-muted ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white p-6 rounded-xl border border-border shadow-sm">
        <h2 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <a
            href="/upload"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Upload Resume
          </a>
          <a
            href="/recommendations"
            className="px-4 py-2 bg-muted text-foreground rounded-lg text-sm font-medium hover:bg-border transition-colors"
          >
            View Recommendations
          </a>
        </div>
      </div>
    </div>
  );
}