"use client";
import React, { useState, useMemo } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Search, Activity, Zap, Shield, Target, TrendingUp, Info } from 'lucide-react';

// --- INTERFACES BASADAS EN EL NUEVO OPPORTUNITY_ANALYZER.PY ---
interface HistoryPoint {
  date: string;
  value: number; // El Backend lo envía como 'value' en el reporte estándar
}

interface AnalysisResult {
  keyword: string;
  opportunity_score: number;
  demand_signal: number;
  monthly_searches: number;
  purchase_intent_score: number;
  total_supply: number;
  competition_level: string; // "BLUE OCEAN 🌊", "EXTREME 🔴", etc.
  supply_pressure: number;
  base_ratio: number;
  trend_velocity: number;
  momentum_multiplier: number;
  verdict: string;
  history: HistoryPoint[];
}

export default function HomePage() {
  const [inputVal, setInputVal] = useState("");
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  const fetchAnalysis = async () => {
    if (!inputVal) return;
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/analyze?keywords=${inputVal}`);
      const data = await response.json();
      setResults(data);
      if (data.length > 0) setSelectedProduct(data[0].keyword);
    } catch (error) {
      console.error("Error:", error);
      alert("Error conectando con el Backend. Asegúrate de que api.py esté corriendo.");
    }
    setLoading(false);
  };

  const current = useMemo(() => results.find(r => r.keyword === selectedProduct), [selectedProduct, results]);

  return (
    <div className="min-h-screen bg-[#050505] text-slate-100 p-8 font-sans">
      <header className="max-w-7xl mx-auto flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <div className="bg-orange-500 p-2 rounded-lg">
            <Activity size={24} className="text-black" />
          </div>
          <h1 className="text-2xl font-black tracking-tighter uppercase">TrendArbitrage <span className="text-orange-500">v2</span></h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto">
        {/* Input con estilo de terminal/moderno */}
        <div className="max-w-2xl mx-auto mb-16">
          <div className="flex gap-3 p-1.5 bg-[#111] border border-white/10 rounded-2xl">
            <input 
              className="flex-1 bg-transparent px-4 outline-none text-lg placeholder:text-slate-600"
              placeholder="Explorar nicho (ej. mechanical keyboards)..."
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchAnalysis()}
            />
            <button 
              onClick={fetchAnalysis}
              className="bg-orange-500 hover:bg-orange-400 text-black px-6 py-3 rounded-xl font-bold transition-all flex items-center gap-2"
            >
              {loading ? "Analizando..." : <><Search size={18} /> Analizar</>}
            </button>
          </div>
        </div>

        {results.length > 0 && current && (
          <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Sidebar con Niveles de Competencia */}
            <div className="col-span-12 lg:col-span-3 space-y-3">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] px-2">Top Hallazgos</h3>
              {results.map((res) => (
                <button
                  key={res.keyword}
                  onClick={() => setSelectedProduct(res.keyword)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    selectedProduct === res.keyword 
                    ? 'border-orange-500/50 bg-orange-500/5' 
                    : 'border-white/5 bg-[#0f0f0f] hover:bg-[#151515]'
                  }`}
                >
                  <p className="font-bold truncate">{res.keyword}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-[10px] font-mono text-slate-400">SCORE: {res.opportunity_score}</span>
                    <span className="text-[9px] px-2 py-0.5 rounded-full bg-white/5 text-slate-300 border border-white/10">
                      {res.competition_level.split(' ')[0]}
                    </span>
                  </div>
                </button>
              ))}
            </div>

            {/* Dashboard Basado en la Nueva Lógica */}
            <div className="col-span-12 lg:col-span-9 space-y-6">
              <div className="bg-[#0f0f0f] border border-white/5 p-8 rounded-3xl relative overflow-hidden">
                <div className="flex justify-between items-start mb-10">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-3 py-1 bg-white/5 border border-white/10 text-[10px] font-bold rounded-md uppercase tracking-wider">
                        {current.competition_level}
                      </span>
                      {current.momentum_multiplier > 1.3 && (
                        <span className="px-3 py-1 bg-orange-500/20 text-orange-500 text-[10px] font-bold rounded-md uppercase">
                          Hot Momentum 🔥
                        </span>
                      )}
                    </div>
                    <h2 className="text-5xl font-black tracking-tight">{current.keyword}</h2>
                  </div>
                  <div className="text-right">
                    <div className="text-6xl font-black text-orange-500 leading-none">{current.opportunity_score}</div>
                    <div className="text-[10px] text-slate-500 font-bold uppercase mt-2 tracking-widest">Opportunity Index</div>
                  </div>
                </div>

                {/* Gráfico de Tendencia REAL (Google Trends) */}
                <div className="h-[280px] w-full bg-white/[0.02] rounded-2xl p-4 border border-white/5">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={current.history}>
                      <defs>
                        <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f97316" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#222" />
                      <XAxis dataKey="date" hide />
                      <YAxis hide domain={[0, 100]} />
                      <Tooltip 
                        contentStyle={{backgroundColor: '#000', border: '1px solid #333', borderRadius: '8px'}}
                        itemStyle={{color: '#f97316'}}
                      />
                      <Area type="monotone" dataKey="value" stroke="#f97316" strokeWidth={3} fill="url(#colorTrend)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Veredicto Formateado (Preservando saltos de línea del Backend) */}
                <div className="mt-8 p-6 bg-orange-500/5 rounded-2xl border border-orange-500/10 relative">
                  <Info className="text-orange-500 absolute top-6 right-6 opacity-50" size={20} />
                  <pre className="whitespace-pre-wrap font-sans text-slate-300 leading-relaxed text-sm">
                    {current.verdict}
                  </pre>
                </div>
              </div>

              {/* Grid de Métricas de la Nueva Fórmula */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <MetricCard 
                  label="Demand Signal" 
                  value={current.demand_signal.toLocaleString()} 
                  icon={<Target size={16}/>} 
                  sub="Búsquedas cualificadas"
                />
                <MetricCard 
                  label="Supply Pressure" 
                  value={current.supply_pressure.toFixed(2)} 
                  icon={<Shield size={16}/>} 
                  sub="Escala logarítmica"
                />
                <MetricCard 
                  label="Base Ratio" 
                  value={current.base_ratio.toFixed(1)} 
                  icon={<TrendingUp size={16}/>} 
                  sub="Demanda / Presión"
                />
                <MetricCard 
                  label="Momentum" 
                  value={`${current.momentum_multiplier}x`} 
                  icon={<Zap size={16}/>} 
                  sub="Multiplicador trend"
                />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function MetricCard({ label, value, icon, sub }: { label: string, value: string | number, icon: React.ReactNode, sub: string }) {
  return (
    <div className="bg-[#0f0f0f] border border-white/5 p-5 rounded-2xl">
      <div className="flex items-center gap-2 text-slate-500 mb-3">
        {icon}
        <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-2xl font-black text-white">{value}</p>
      <p className="text-[9px] text-slate-600 font-medium mt-1 uppercase tracking-tighter">{sub}</p>
    </div>
  );
}