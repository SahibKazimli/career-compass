import { NavLink } from "react-router-dom";
import { LayoutDashboard, Upload, Compass } from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/upload", icon: Upload, label: "Upload Resume" },
  { to: "/recommendations", icon: Compass, label: "Recommendations" },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-border min-h-screen p-6">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-foreground">Career Compass</h1>
        <p className="text-sm text-muted-foreground">Find your path</p>
      </div>
      
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}