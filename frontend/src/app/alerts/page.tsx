'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AlertsPage() {
    const router = useRouter();
    const [alerts, setAlerts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        const fetchAlerts = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/v1/alerts/', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setAlerts(data);
                }
            } catch (error) {
                console.error('Failed to fetch alerts:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
    }, [router]);

    const markAsRead = async (id: string) => {
        const token = localStorage.getItem('access_token');
        try {
            const response = await fetch(`http://localhost:8000/api/v1/alerts/${id}/read`, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                setAlerts((prev) =>
                    prev.map((a) => a.id === id ? { ...a, is_read: true } : a)
                );
            }
        } catch (error) {
            console.error('Failed to mark alert as read:', error);
        }
    };

    const filteredAlerts = alerts.filter(alert => {
        if (filter === 'unread') return !alert.is_read;
        if (filter === 'critical') return alert.severity === 'high' || alert.severity === 'critical';
        return true;
    });

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black text-white tracking-tight underline decoration-accent/30 decoration-4">Security Archive</h1>
                    <p className="text-muted text-lg">Detailed history of all system detections</p>
                </div>

                <div className="flex bg-white/5 p-1 rounded-2xl border border-white/10">
                    {['all', 'unread', 'critical'].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-6 py-2 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${filter === f
                                    ? 'bg-accent text-white shadow-lg shadow-accent/20'
                                    : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </header>

            {loading ? (
                <div className="grid grid-cols-1 gap-4">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="glass h-32 rounded-3xl animate-pulse" />
                    ))}
                </div>
            ) : filteredAlerts.length === 0 ? (
                <div className="glass p-20 rounded-[3rem] text-center border-dashed border-2 border-white/5">
                    <div className="w-24 h-24 bg-accent/5 rounded-full flex items-center justify-center mx-auto mb-6 border border-accent/10">
                        <svg className="w-10 h-10 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 012 2v1a2 2 0 01-2 2H6a2 2 0 01-2-2v-1a2 2 0 012-2m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">No alerts found</h3>
                    <p className="text-muted max-w-sm mx-auto">Either your system is perfectly safe or the current filters are too strict.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {filteredAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={`glass-card p-6 rounded-[2rem] flex flex-col md:flex-row items-center gap-8 ${alert.is_read ? 'opacity-60 grayscale-[0.5]' : ''}`}
                            onClick={() => !alert.is_read && markAsRead(alert.id)}
                        >
                            <div className={`w-20 h-20 rounded-2xl flex items-center justify-center shrink-0 shadow-2xl ${(alert.severity === 'high' || alert.severity === 'critical')
                                    ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                                    : 'bg-orange-500/10 text-orange-500 border border-orange-500/20'
                                }`}>
                                <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>

                            <div className="flex-1 space-y-3">
                                <div className="flex flex-wrap items-center gap-3">
                                    <span className={`text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-tighter ${(alert.severity === 'high' || alert.severity === 'critical')
                                            ? 'bg-red-500 text-white shadow-lg shadow-red-500/30'
                                            : 'bg-orange-500 text-white shadow-lg shadow-orange-500/30'
                                        }`}>
                                        {alert.severity}
                                    </span>
                                    <h3 className="text-xl font-bold text-white">{alert.title}</h3>
                                    {!alert.is_read && <span className="w-2 h-2 bg-accent rounded-full animate-ping" />}
                                </div>
                                <p className="text-slate-400 leading-relaxed font-medium">{alert.description}</p>
                                <div className="flex items-center space-x-6">
                                    <div className="flex items-center space-x-2 text-xs font-mono text-slate-500">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        <span>{new Date(alert.created_at).toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-xs font-mono text-slate-500">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path></svg>
                                        <span>Camera 01</span>
                                    </div>
                                </div>
                            </div>

                            {alert.image_path && (
                                <div className="relative group/img w-full md:w-56 h-36 rounded-3xl overflow-hidden border border-white/5 shadow-2xl">
                                    <img
                                        src={`http://localhost:8000${alert.image_path}`}
                                        alt="Intruder"
                                        className="w-full h-full object-cover group-hover/img:scale-110 transition-transform duration-700"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover/img:opacity-100 transition-opacity flex items-end p-4">
                                        <button className="text-[10px] font-bold text-white uppercase tracking-widest bg-white/20 px-3 py-1 rounded-lg backdrop-blur-md">View HD</button>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
