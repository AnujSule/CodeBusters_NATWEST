import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BarChart3, Lock, Mail, User } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuthStore } from '../store/authStore';
import api from '../config/api';
import { toast } from 'sonner';
import type { TokenResponse } from '../types/api';

const RegisterPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { setTokens, setUser } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            // Register returns tokens — auto-login the user
            const { data } = await api.post<TokenResponse>('/auth/register', {
                email,
                password,
                full_name: fullName,
            });

            setTokens(data.access_token, data.refresh_token || data.access_token);
            setUser({ id: data.user_id || '', email, full_name: fullName });

            toast.success('Account created! Welcome to DataDialogue.');
            navigate('/');
        } catch (error: any) {
            toast.error(error.message || 'Registration failed');
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
                    <h1 className="text-3xl font-bold gradient-text mb-2">Create Account</h1>
                    <p className="text-text-secondary">Join DataDialogue</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1.5">Full Name</label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="John Smith"
                                required
                                className="input-field pl-10"
                                id="register-name"
                            />
                        </div>
                    </div>

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
                                id="register-email"
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
                                placeholder="Min. 8 characters"
                                required
                                minLength={8}
                                className="input-field pl-10"
                                id="register-password"
                            />
                        </div>
                    </div>

                    <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
                        Create Account
                    </Button>
                </form>

                <p className="text-center text-sm text-text-secondary">
                    Already have an account?{' '}
                    <Link to="/login" className="text-accent-amber hover:text-amber-400 transition-colors">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;
