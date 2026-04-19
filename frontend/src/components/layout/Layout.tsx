import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';

export const Layout: React.FC = () => (
    <div className="min-h-screen flex flex-col bg-base">
        <Navbar />
        <main className="flex-1 flex overflow-hidden">
            <Outlet />
        </main>
    </div>
);
