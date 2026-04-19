import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BarChart3, Lock, Mail } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuthStore } from '../store/authStore';
import api from '../config/api';
import { toast } from 'sonner';
import type { TokenResponse, UserResponse } from '../types/api';

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { setTokens, setUser } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const { data: tokens } = await api.post<TokenResponse>('/auth/login', { email, password });
            // Use refresh_token if available, otherwise mirror access_token
            setTokens(tokens.access_token, tokens.refresh_token || tokens.access_token);

            const { data: user } = await api.get<UserResponse>('/auth/me', {
                headers: { Authorization: `Bearer ${tokens.access_token}` },
            });
            setUser({ id: user.id, email: user.email, full_name: user.full_name || '' });

            toast.success(`Welcome back, ${user.full_name || user.email}!`);
            navigate('/');
        } catch (error: any) {
            toast.error(error.message || 'Invalid credentials');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-base px-4">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <div className="flex items-center justify-center gap-3 mb-6">
                        <div className="p-3 rounded-xl bg-accent-amber/10">
                            <BarChart3 className="h-8 w-8 text-accent-amber" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold gradient-text mb-2">DataDialogue</h1>
                    <p className="text-text-secondary">Sign in to your account</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1.5">Email</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                required
                                className="input-field pl-10"
                                id="login-email"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1.5">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                className="input-field pl-10"
                                id="login-password"
                            />
                        </div>
                    </div>

                    <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
                        Sign in
                    </Button>
                </form>

                <p className="text-center text-sm text-text-secondary">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-accent-amber hover:text-amber-400 transition-colors">
                        Create one
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;
