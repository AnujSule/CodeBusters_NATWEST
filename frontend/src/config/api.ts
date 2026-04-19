/** Axios instance with interceptors for API communication. */

import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor: add Authorization header
api.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor: handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            const { status, data } = error.response;

            // Unauthorized — clear auth and redirect to login
            if (status === 401) {
                useAuthStore.getState().logout();
                window.location.href = '/login';
            }

            // Extract error message from FastAPI response
            // FastAPI uses 'detail' field for error messages
            if (data?.detail) {
                if (typeof data.detail === 'string') {
                    error.message = data.detail;
                } else if (Array.isArray(data.detail)) {
                    // Validation errors
                    const messages = data.detail.map(
                        (err: { msg?: string; message?: string; loc?: string[] }) =>
                            err.msg || err.message || JSON.stringify(err)
                    );
                    error.message = messages.join('; ');
                }
            } else if (data?.error) {
                error.message = data.error;
            }
        }

        return Promise.reject(error);
    }
);

export default api;
