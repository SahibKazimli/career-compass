import { cn } from '../../lib/utils';
import {
    Compass,
    LayoutDashboard,
    FileText,
    Target,
    TrendingUp,
    BookOpen,
    Settings,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: FileText, label: 'Resume', path: '/resume' },
    { icon: Target, label: 'Roadmap', path: '/roadmap' },
    { icon: TrendingUp, label: 'Skills', path: '/skills' },
    { icon: BookOpen, label: 'Resources', path: '/resources' },
];

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
    return (
        <aside
            className={cn(
                "h-screen sticky top-0 bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
                collapsed ? "w-16" : "w-64"
            )}
        >
            {/* Logo */}
            <div className="h-16 flex items-center justify-between px-4 border-b border-sidebar-border">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-sidebar-primary flex items-center justify-center">
                        <Compass className="w-5 h-5 text-sidebar-primary-foreground" />
                    </div>
                    {!collapsed && (
                        <span className="font-semibold text-sidebar-foreground whitespace-nowrap">
                            Career Compass
                        </span>
                    )}
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-4 px-2">
                <ul className="space-y-1">
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <NavLink
                                to={item.path}
                                className={({ isActive }) =>
                                    cn(
                                        "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                                        "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                                        isActive && "bg-sidebar-accent text-sidebar-primary font-medium"
                                    )
                                }
                            >
                                <item.icon className="w-5 h-5 shrink-0" />
                                {!collapsed && <span>{item.label}</span>}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* Footer */}
            <div className="p-2 border-t border-sidebar-border">
                <NavLink
                    to="/settings"
                    className={({ isActive }) =>
                        cn(
                            "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                            "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                            isActive && "bg-sidebar-accent text-sidebar-primary font-medium"
                        )
                    }
                >
                    <Settings className="w-5 h-5 shrink-0" />
                    {!collapsed && <span>Settings</span>}
                </NavLink>

                <button
                    onClick={onToggle}
                    className="w-full flex items-center gap-3 px-3 py-2.5 mt-1 rounded-lg transition-colors text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                >
                    {collapsed ? (
                        <ChevronRight className="w-5 h-5" />
                    ) : (
                        <>
                            <ChevronLeft className="w-5 h-5" />
                            <span>Collapse</span>
                        </>
                    )}
                </button>
            </div>
        </aside>
    );
}
