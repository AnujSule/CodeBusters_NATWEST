import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Spinner } from './components/ui/Spinner';
import { useAuthStore } from './store/authStore';

// Lazy-loaded pages for code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const AuditPage = lazy(() => import('./pages/AuditPage'));

/** Protected route wrapper that redirects to login if not authenticated. */
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAuthenticated } = useAuthStore();
    if (!isAuthenticated) return <Navigate to="/login" replace />;
    return <>{children}</>;
};

/** Public route wrapper that redirects to dashboard if already authenticated. */
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAuthenticated } = useAuthStore();
    if (isAuthenticated) return <Navigate to="/" replace />;
    return <>{children}</>;
};

const App: React.FC = () => (
    <BrowserRouter>
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-base"><Spinner size="lg" /></div>}>
            <Routes>
                {/* Public routes */}
                <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
                <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

                {/* Protected routes */}
                <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/audit" element={<AuditPage />} />
                </Route>

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Suspense>
    </BrowserRouter>
);

export default App;
