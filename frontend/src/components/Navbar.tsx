'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function Navbar() {
    const router = useRouter();
    const pathname = usePathname();

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
    };

    const navLinks = [
        { name: 'Dashboard', href: '/' },
        { name: 'Alerts', href: '/alerts' },
        { name: 'Cameras', href: '/cameras' },
        { name: 'Settings', href: '/settings' },
    ];

    return (
        <nav className="sticky top-0 z-50 glass border-b border-white/5 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <Link href="/" className="group flex items-center space-x-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-accent to-accent-secondary rounded-xl flex items-center justify-center shadow-lg shadow-accent/20 group-hover:scale-110 transition-transform">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                    </div>
                    <span className="text-xl font-bold tracking-tight text-white uppercase hidden sm:block">
                        Falcon<span className="text-accent">Eye</span>
                    </span>
                </Link>

                <div className="flex items-center space-x-1 sm:space-x-4">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${pathname === link.href
                                    ? 'text-white bg-white/10'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            {link.name}
                        </Link>
                    ))}
                    <div className="w-px h-6 bg-white/10 mx-2 hidden sm:block" />
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-sm font-medium text-red-400 transition-all border border-red-500/20"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}
