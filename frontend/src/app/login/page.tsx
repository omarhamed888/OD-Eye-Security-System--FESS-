'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch('http://localhost:8000/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Access Denied');
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);

            router.push('/');
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
            {/* Background elements */}
            <div className="absolute inset-0 bg-background" />
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-accent/20 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />

            <div className="w-full max-w-lg p-12 glass rounded-[3rem] shadow-2xl space-y-10 animate-in fade-in zoom-in-95 duration-1000 relative z-10 border-white/10">
                <div className="text-center space-y-4">
                    <div className="inline-block p-4 rounded-3xl bg-gradient-to-br from-accent to-accent-secondary shadow-2xl mb-4 group hover:scale-110 transition-transform">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white uppercase">
                        Protocol <span className="text-accent">Login</span>
                    </h1>
                    <p className="text-slate-400 text-xs font-bold uppercase tracking-[0.4em]">Initialize Biological Uplink</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    {error && (
                        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-500 text-[10px] font-black uppercase tracking-widest text-center animate-bounce">
                            Error: {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest ml-4">Terminal Identifier</label>
                        <input
                            type="text"
                            required
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-6 py-5 bg-white/5 border border-white/5 rounded-2xl focus:ring-1 focus:ring-accent focus:border-accent transition-all outline-none text-white font-medium"
                            placeholder="OPERATOR_ID"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="block text-[10px] font-black text-slate-500 uppercase tracking-widest ml-4">Access Key</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-6 py-5 bg-white/5 border border-white/5 rounded-2xl focus:ring-1 focus:ring-accent focus:border-accent transition-all outline-none text-white font-medium"
                            placeholder="••••••••"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-5 bg-gradient-to-r from-accent to-accent-secondary hover:brightness-110 text-white font-black uppercase tracking-[0.2em] rounded-2xl shadow-2xl shadow-accent/40 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                    >
                        {loading ? 'Authenticating...' : 'Establish Link'}
                    </button>
                </form>

                <div className="text-center pt-4 border-t border-white/5">
                    <Link href="/register" className="text-slate-500 text-[10px] font-bold uppercase tracking-widest hover:text-white transition-colors">
                        Request New Clearances
                    </Link>
                </div>
            </div>
        </div>
    );
}
