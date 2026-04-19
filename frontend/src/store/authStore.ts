/** Zustand auth store for managing authentication state. */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
    accessToken: string | null;
    refreshToken: string | null;
    user: {
        id: string;
        email: string;
        full_name: string;
    } | null;
    isAuthenticated: boolean;
    setTokens: (accessToken: string, refreshToken: string) => void;
    setUser: (user: { id: string; email: string; full_name: string }) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            accessToken: null,
            refreshToken: null,
            user: null,
            isAuthenticated: false,

            setTokens: (accessToken: string, refreshToken: string) =>
                set({
                    accessToken,
                    refreshToken,
                    isAuthenticated: true,
                }),

            setUser: (user: { id: string; email: string; full_name: string }) =>
                set({ user }),

            logout: () =>
                set({
                    accessToken: null,
                    refreshToken: null,
                    user: null,
                    isAuthenticated: false,
                }),
        }),
        {
            name: 'datadialogue-auth',
            partialize: (state) => ({
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
