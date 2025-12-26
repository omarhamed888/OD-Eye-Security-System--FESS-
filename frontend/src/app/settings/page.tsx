'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SettingsPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState({
        camera_index: 0,
        confidence_threshold: 0.15,
        alert_cooldown: 30,
        telegram_enabled: true,
        roi_enabled: true,
        face_recognition: true
    });

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) router.push('/login');
    }, [router]);

    const handleSave = async () => {
        setLoading(true);
        // Simulate API call
        setTimeout(() => {
            setLoading(false);
            alert("Settings saved successfully! (Demo Mode)");
        }, 1000);
    };

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <header>
                <h1 className="text-3xl font-bold text-white">System Settings</h1>
                <p className="text-muted">Configure your falcon eye security parameters</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Hardware & Core */}
                <div className="glass rounded-3xl p-8 space-y-6">
                    <div className="flex items-center space-x-3 text-accent border-b border-white/5 pb-4">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
                        <h2 className="font-semibold text-lg text-white">Detection Core</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Camera Index</label>
                            <input
                                type="number"
                                value={config.camera_index}
                                onChange={(e) => setConfig({ ...config, camera_index: parseInt(e.target.value) })}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                                placeholder="0"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Confidence Threshold ({config.confidence_threshold})</label>
                            <input
                                type="range"
                                min="0.05"
                                max="0.95"
                                step="0.01"
                                value={config.confidence_threshold}
                                onChange={(e) => setConfig({ ...config, confidence_threshold: parseFloat(e.target.value) })}
                                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-accent"
                            />
                            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                                <span>Sensitive</span>
                                <span>Balanced</span>
                                <span>Strict</span>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Alert Cooldown (Seconds)</label>
                            <input
                                type="number"
                                value={config.alert_cooldown}
                                onChange={(e) => setConfig({ ...config, alert_cooldown: parseInt(e.target.value) })}
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent transition-colors"
                            />
                        </div>
                    </div>
                </div>

                {/* Automation & UI */}
                <div className="glass rounded-3xl p-8 space-y-6">
                    <div className="flex items-center space-x-3 text-purple-400 border-b border-white/5 pb-4">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <h2 className="font-semibold text-lg text-white">Features</h2>
                    </div>

                    <div className="space-y-4">
                        {[
                            { id: 'telegram_enabled', label: 'Telegram Notifications', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
                            { id: 'roi_enabled', label: 'Restricted Area (ROI)', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5z' },
                            { id: 'face_recognition', label: 'Face Recognition', icon: 'M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z' }
                        ].map((feature) => (
                            <div key={feature.id} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center">
                                        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={feature.icon}></path></svg>
                                    </div>
                                    <span className="text-sm font-medium text-slate-200">{feature.label}</span>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={config[feature.id]}
                                        onChange={() => setConfig({ ...config, [feature.id]: !config[feature.id] })}
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="flex justify-end pt-4">
                <button
                    onClick={handleSave}
                    disabled={loading}
                    className="px-8 py-3 bg-gradient-to-r from-accent to-accent-secondary rounded-2xl text-white font-bold shadow-xl shadow-accent/20 hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
                >
                    {loading ? 'Saving Changes...' : 'Save Configuration'}
                </button>
            </div>
        </div>
    );
}
