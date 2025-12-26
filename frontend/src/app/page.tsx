'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  const [isStreaming, setIsStreaming] = useState(false);
  const [liveAlerts, setLiveAlerts] = useState<any[]>([]);
  const [stats, setStats] = useState({
    cameras: 1,
    alerts: 0,
    uptime: '99.9%',
  });
  const [systemStatus, setSystemStatus] = useState('SAFE');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    }

    // Fetch initial historical alert count
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/alerts/', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setStats(prev => ({ ...prev, alerts: data.length }));
          setLiveAlerts(data.slice(0, 5));
        }
      } catch (e) { console.error(e); }
    };
    fetchStats();
  }, [router]);

  // WebSocket Live Streaming Logic
  useEffect(() => {
    let ws: WebSocket | null = null;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');

    if (isStreaming && canvas && ctx) {
      ws = new WebSocket('ws://localhost:8000/api/v1/ws/stream');

      ws.onmessage = async (event) => {
        const blob = event.data;
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          URL.revokeObjectURL(img.src);
        };
        img.src = URL.createObjectURL(blob);
      };

      ws.onerror = (err) => {
        console.error("Streaming WebSocket error:", err);
        setIsStreaming(false);
      };
    }

    return () => {
      if (ws) ws.close();
    };
  }, [isStreaming]);

  // WebSocket Notifications Logic
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/notifications');

    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setLiveAlerts(prev => [alert, ...prev].slice(0, 5));
      setStats(prev => ({ ...prev, alerts: prev.alerts + 1 }));
      setSystemStatus('CRITICAL');

      // Auto-reset status after 5 seconds if no new alerts
      setTimeout(() => setSystemStatus('SAFE'), 5000);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-10 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      {/* Header with Glass Gradient */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <h1 className="text-5xl font-black text-white tracking-tight neo-text">
            Command <span className="text-accent">Center</span>
          </h1>
          <div className="flex items-center space-x-3 text-slate-400">
            <span className="flex items-center space-x-2 bg-white/5 px-3 py-1 rounded-full border border-white/10 text-xs font-mono">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Lat: 24.12 • Long: 55.75</span>
            </span>
            <span className="text-xs uppercase tracking-widest font-bold">Encrypted Connection Active</span>
          </div>
        </div>

        <div className={`px-6 py-3 rounded-2xl border transition-all duration-500 flex items-center space-x-4 ${systemStatus === 'CRITICAL'
            ? 'bg-red-500/20 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.3)] animate-pulse'
            : 'bg-green-500/10 border-green-500/30'
          }`}>
          <div className={`w-3 h-3 rounded-full ${systemStatus === 'CRITICAL' ? 'bg-red-500' : 'bg-green-500'}`} />
          <span className={`text-sm font-black uppercase tracking-widest ${systemStatus === 'CRITICAL' ? 'text-red-500' : 'text-green-500'}`}>
            System Status: {systemStatus}
          </span>
        </div>
      </header>

      {/* Modern Metric Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {[
          { label: 'Active Nodes', val: stats.cameras, icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z', color: 'text-accent' },
          { label: 'Neutralized Threats', val: stats.alerts, icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z', color: 'text-danger' },
          { label: 'Grid Stability', val: stats.uptime, icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', color: 'text-success' }
        ].map((item, idx) => (
          <div key={idx} className="glass-card p-8 rounded-[2.5rem] relative overflow-hidden">
            <div className={`absolute -top-4 -right-4 w-24 h-24 ${item.color} opacity-10 rotate-12`}>
              <svg fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d={item.icon} /></svg>
            </div>
            <div className="text-xs font-black text-muted uppercase tracking-[0.2em] mb-4">{item.label}</div>
            <div className="text-5xl font-black text-white tracking-tighter tabular-nums">{item.val}</div>
            <div className="mt-4 flex items-center space-x-2">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
              <span className="text-[10px] text-slate-500 font-bold uppercase">Real-time telemetry active</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Control Deck */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
        {/* Camera Feed - Large */}
        <div className="xl:col-span-8 space-y-6">
          <div className="glass rounded-[3rem] p-4 flex flex-col min-h-[500px] overflow-hidden group/feed relative border-white/10">
            {!isStreaming ? (
              <div className="flex-1 flex flex-col items-center justify-center space-y-8 bg-black/40 rounded-[2.5rem]">
                <div className="relative">
                  <div className="absolute inset-0 bg-accent/20 rounded-full blur-3xl animate-pulse" />
                  <div className="w-24 h-24 rounded-full bg-accent/10 flex items-center justify-center border border-accent/20 relative z-10">
                    <svg className="w-12 h-12 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                  </div>
                </div>
                <div className="text-center space-y-2">
                  <h3 className="text-2xl font-black text-white tracking-tight">OPTICAL SENSOR OFFLINE</h3>
                  <p className="text-slate-500 text-sm max-w-sm mx-auto font-medium lowercase italic">initiate uplink protocol to begin biological threat assessment.</p>
                </div>
                <button
                  onClick={() => setIsStreaming(true)}
                  className="group/btn relative px-10 py-4 bg-accent rounded-2xl text-white font-black uppercase tracking-widest shadow-2xl shadow-accent/40 hover:scale-105 active:scale-95 transition-all overflow-hidden"
                >
                  <span className="relative z-10">Initialize Uplink</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-accent via-white/20 to-accent scale-x-0 group-hover/btn:scale-x-100 transition-transform origin-left duration-500" />
                </button>
              </div>
            ) : (
              <div className="flex-1 rounded-[2.5rem] overflow-hidden bg-black relative shadow-2xl">
                <canvas ref={canvasRef} width="640" height="480" className="w-full h-full object-cover filter brightness-110 contrast-110" />

                <div className="absolute top-6 left-6 flex items-center space-x-4">
                  <div className="bg-red-600 px-3 py-1 rounded text-[10px] font-black text-white flex items-center space-x-2 shadow-lg">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    <span>REC</span>
                  </div>
                  <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded text-[10px] font-mono text-white border border-white/10 uppercase tracking-widest">
                    Cam_Node_01 // 1080p
                  </div>
                </div>

                <div className="absolute bottom-6 right-6 flex items-center space-x-3">
                  <button
                    onClick={() => setIsStreaming(false)}
                    className="px-6 py-2 bg-white/10 hover:bg-red-500 rounded-xl text-[10px] font-black uppercase tracking-widest text-white backdrop-blur-md border border-white/10 transition-all"
                  >
                    Terminate Feed
                  </button>
                </div>

                {/* Scanner Overlay UI */}
                <div className="absolute inset-x-0 top-0 h-10 bg-gradient-to-b from-accent/5 to-transparent pointer-events-none" />
                <div className="absolute inset-y-0 left-0 w-10 bg-gradient-to-r from-accent/5 to-transparent pointer-events-none" />
                <div className="absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-accent/5 to-transparent pointer-events-none" />
              </div>
            )}
          </div>
        </div>

        {/* Live HUD - Right */}
        <div className="xl:col-span-4 flex flex-col space-y-6">
          <div className="glass rounded-[3rem] p-8 flex flex-col flex-1 border-white/10 overflow-hidden">
            <div className="flex items-center justify-between mb-8 border-b border-white/5 pb-4">
              <h3 className="text-xl font-black text-white uppercase tracking-tighter">Combat HUD</h3>
              <div className="flex space-x-1">
                <div className="w-1 h-1 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                <div className="w-1 h-1 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-1 h-1 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>

            <div className="space-y-6 flex-1 overflow-y-auto pr-4 custom-scrollbar">
              {liveAlerts.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30 grayscale transition-all hover:opacity-50">
                  <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                  <p className="text-sm font-bold uppercase tracking-widest text-slate-500">Scanning environment...</p>
                </div>
              )}
              {liveAlerts.map((alert, i) => (
                <div key={alert.id} className="group/alert relative p-5 rounded-3xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer animate-in slide-in-from-right-8 duration-500">
                  <div className={`absolute top-0 left-0 bottom-0 w-1.5 rounded-l-3xl ${alert.severity === 'high' ? 'bg-danger shadow-[0_0_15px_rgba(255,0,110,0.4)]' : 'bg-warning shadow-[0_0_15px_rgba(251,133,0,0.4)]'}`} />

                  <div className="flex gap-4 items-start">
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-center mb-1">
                        <div className="text-[10px] font-black uppercase text-accent tracking-[0.2em]">Node_{alert.camera_id || '01'}</div>
                        <div className="text-[10px] font-mono text-slate-500">{new Date(alert.created_at).toLocaleTimeString()}</div>
                      </div>
                      <div className="text-sm font-black text-white uppercase truncate group-hover/alert:text-accent transition-colors">{alert.title}</div>
                      <div className="text-xs text-slate-400 line-clamp-2 mt-1 font-medium">{alert.description}</div>
                    </div>
                    {alert.image_path && (
                      <div className="w-14 h-14 rounded-xl overflow-hidden shadow-2xl border border-white/10 shrink-0">
                        <img src={`http://localhost:8000${alert.image_path}`} alt="Alert" className="w-full h-full object-cover group-hover/alert:scale-125 transition-transform duration-500" />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => router.push('/alerts')}
              className="mt-8 group/btn-h flex items-center justify-center space-x-3 w-full py-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
            >
              <span className="text-xs font-black uppercase tracking-widest text-slate-400 group-hover/btn-h:text-white transition-colors">Access Tactical Logs</span>
              <svg className="w-4 h-4 text-slate-600 group-hover/btn-h:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </button>
          </div>
        </div>
      </div>

      {/* Footer Branding */}
      <footer className="pt-10 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-[10px] font-black uppercase tracking-[0.5em] text-slate-700">
        <div>Falcon Eye Security System // V{process.env.NEXT_PUBLIC_VERSION || '1.2.0'}</div>
        <div className="flex space-x-8 mt-4 md:mt-0">
          <span className="hover:text-accent cursor-pointer transition-colors">Operational Protocols</span>
          <span className="hover:text-accent cursor-pointer transition-colors">Neural Net Status</span>
          <span className="text-slate-500">Built for Absolute Vigilance</span>
        </div>
      </footer>
    </div>
  );
}
