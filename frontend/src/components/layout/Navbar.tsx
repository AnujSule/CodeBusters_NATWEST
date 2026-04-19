import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BarChart3, LogOut, Shield, User } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export const Navbar: React.FC = () => {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="h-16 bg-surface border-b border-border flex items-center justify-between px-6 sticky top-0 z-50 backdrop-blur-md bg-surface/95">
            <Link to="/" className="flex items-center gap-3 group">
                <div className="p-2 rounded-lg bg-accent-amber/10 group-hover:bg-accent-amber/20 transition-colors">
                    <BarChart3 className="h-5 w-5 text-accent-amber" />
                </div>
                <span className="text-lg font-bold gradient-text">DataDialogue</span>
            </Link>

            <div className="flex items-center gap-4">
                <Link
                    to="/audit"
                    className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors text-sm"
                >
                    <Shield className="h-4 w-4" />
                    <span>Audit Log</span>
                </Link>

                {user && (
                    <div className="flex items-center gap-3 ml-4 pl-4 border-l border-border">
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-elevated border border-border flex items-center justify-center">
                                <User className="h-4 w-4 text-text-secondary" />
                            </div>
                            <span className="text-sm text-text-secondary hidden sm:block">{user.full_name}</span>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-2 rounded-lg text-text-muted hover:text-accent-red hover:bg-elevated transition-colors"
                            title="Logout"
                        >
                            <LogOut className="h-4 w-4" />
                        </button>
                    </div>
                )}
            </div>
        </nav>
    );
};
