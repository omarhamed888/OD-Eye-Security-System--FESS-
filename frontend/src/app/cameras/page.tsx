'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CamerasPage() {
    const router = useRouter();
    const [cameras, setCameras] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        const fetchCameras = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/v1/cameras/', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (response.ok) {
                    const data = await response.json();
                    setCameras(data);
                }
            } catch (error) {
                console.error('Failed to fetch cameras:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchCameras();
    }, [router]);

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-6 duration-1000">
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-2">
                    <h1 className="text-4xl font-black text-white tracking-tight uppercase tracking-[0.1em]">Detection <span className="text-accent underline decoration-4 decoration-accent/20">Nodes</span></h1>
                    <p className="text-slate-400 font-medium">Provision and manage high-precision optical sensors</p>
                </div>
                <button className="group relative px-8 py-3 bg-gradient-to-r from-accent to-accent-secondary rounded-2xl text-white font-black uppercase tracking-widest shadow-xl shadow-accent/20 hover:scale-105 transition-all">
                    Register New Node
                </button>
            </header>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="glass h-80 rounded-[2.5rem] animate-pulse" />
                    ))}
                </div>
            ) : cameras.length === 0 ? (
                <div className="glass p-20 rounded-[3rem] text-center border-dashed border-2 border-white/5 bg-gradient-to-br from-white/5 to-transparent">
                    <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-8 border border-white/10 group hover:border-accent/50 transition-colors">
                        <svg className="w-12 h-12 text-slate-500 group-hover:text-accent transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                    </div>
                    <h3 className="text-3xl font-black text-white mb-3">No active nodes detected</h3>
                    <p className="text-slate-400 max-w-sm mx-auto font-medium mb-10 leading-relaxed">Establish a high-speed uplink to your primary optical hardware to begin 24/7 autonomous monitoring.</p>
                    <button className="px-10 py-4 bg-white/5 hover:bg-white/10 rounded-2xl text-xs font-black uppercase tracking-widest text-white border border-white/10 transition-all active:scale-95 shadow-2xl">
                        Identify Hardware Interfaces
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {cameras.map((camera: any) => (
                        <div key={camera.id} className="glass-card rounded-[3rem] overflow-hidden group">
                            <div className="h-56 bg-gradient-to-br from-slate-900 to-black relative flex items-center justify-center overflow-hidden">
                                <svg className="w-20 h-20 text-white/5 group-hover:scale-125 transition-transform duration-1000" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>

                                <div className="absolute top-6 right-6">
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${camera.is_active ? 'bg-green-500 text-white' : 'bg-slate-700 text-slate-300'} shadow-lg`}>
                                        {camera.status}
                                    </span>
                                </div>

                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-8">
                                    <button className="w-full py-3 bg-accent rounded-xl text-xs font-black text-white uppercase tracking-[0.2em] shadow-xl shadow-accent/20">Connect Feed</button>
                                </div>
                            </div>

                            <div className="p-8 space-y-4">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-2xl font-black text-white tracking-tight uppercase">{camera.name}</h3>
                                        <p className="text-[10px] text-accent font-black uppercase tracking-widest mt-1 italic">{camera.location || 'Tactical Sector A-1'}</p>
                                    </div>
                                    <div className={`w-3 h-3 rounded-full mt-2 ${camera.is_active ? 'bg-green-500 shadow-[0_0_10px_#22c55e]' : 'bg-slate-600'}`} />
                                </div>

                                <div className="pt-6 grid grid-cols-2 gap-4 border-t border-white/5 text-[10px] font-black uppercase tracking-widest">
                                    <div className="text-slate-500">Uplink: <span className="text-white">{camera.source_type}</span></div>
                                    <div className="text-slate-500 text-right">FPS: <span className="text-white">{camera.fps || 30}</span></div>
                                </div>

                                <div className="flex justify-between items-center pt-2">
                                    <div className="text-slate-600 text-[8px] font-mono">{camera.id}</div>
                                    <button className="text-accent text-xs font-black uppercase tracking-widest hover:underline active:scale-95 transition-transform">Configure Node</button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
