"use client";
import React, { useState } from 'react';
import Image from "next/image";
import { 
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, 
  Tooltip, ResponsiveContainer, CartesianGrid 
} from 'recharts';
import { Search, Rocket, TrendingUp, AlertCircle, ShoppingBag } from 'lucide-react';

export default function Home() {
  const [keywords, setKeywords] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Función para conectar con tu API de FastAPI
  const fetchAnalysis = async () => {
    if (!keywords) return;
    setLoading(true);
    try {
      // Asegúrate de que tu uvicorn esté corriendo en el puerto 8000
      const response = await fetch(`http://127.0.0.1:8000/analyze?keywords=${keywords}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Error conectando con la API:", error);
      alert("No se pudo conectar con el servidor. Revisa que el backend esté activo.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        
        {/* Encabezado */}
        <header className="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-4xl font-black text-cyan-400 mb-2 flex items-center gap-3">
              <ShoppingBag className="text-cyan-400" /> TrendArbitrage AI
            </h1>
            <p className="text-slate-400 text-lg">
              Niche Discovery Engine: Demand → Supply → Opportunity
            </p>
          </div>
          <div className="bg-slate-900 px-6 py-3 rounded-2xl border border-slate-800">
            <span className="text-slate-500 text-sm block">Status</span>
            <span className="text-green-400 font-bold flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /> API Conectada
            </span>
          </div>
        </header>

        {/* Buscador Estilo Profesional */}
        <div className="flex flex-col md:flex-row gap-4 mb-12 bg-slate-900 p-5 rounded-3xl border border-slate-800 shadow-2xl">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-4 text-slate-500" size={24} />
            <input 
              className="w-full bg-slate-950 border-none rounded-2xl py-4 pl-14 pr-4 text-lg focus:ring-2 focus:ring-cyan-500 outline-none transition-all"
              placeholder="Escribe productos separados por comas (ej: plush, toy, gadget)..."
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchAnalysis()}
            />
          </div>
          <button 
            onClick={fetchAnalysis}
            className="bg-cyan-600 hover:bg-cyan-500 text-white px-10 py-4 rounded-2xl font-bold transition-all flex items-center justify-center gap-3 text-lg"
            disabled={loading}
          >
            {loading ? (
              <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <> <Rocket size={22} /> Analizar Mercado </>
            )}
          </button>
        </div>

        {results.length > 0 && (
          <>
            {/* Visualizaciones Principales */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
              
              {/* Mapa de Oportunidad */}
              <div className="lg:col-span-2 bg-slate-900 p-8 rounded-3xl border border-slate-800 h-[550px] shadow-lg">
                <h2 className="text-xl font-bold mb-8 flex items-center gap-3 text-slate-300">
                  <TrendingUp className="text-cyan-400" /> Mapa de Arbitraje Digital
                </h2>
                <ResponsiveContainer width="100%" height="85%">
                  <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis 
                      type="number" 
                      dataKey="total_supply" 
                      name="Suministro" 
                      stroke="#64748b" 
                      label={{ value: 'OFERTA (Competencia)', position: 'bottom', offset: 20, fill: '#94a3b8' }} 
                    />
                    <YAxis 
                      type="number" 
                      dataKey="demand_signal" 
                      name="Demanda" 
                      stroke="#64748b" 
                      label={{ value: 'DEMANDA (Interés)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} 
                    />
                    <ZAxis type="number" dataKey="opportunity_score" range={[150, 1200]} />
                    <Tooltip 
                      cursor={{ strokeDasharray: '3 3' }} 
                      contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '15px'}}
                      itemStyle={{color: '#22d3ee'}}
                    />
                    <Scatter name="Productos" data={results} fill="#22d3ee" fillOpacity={0.6} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              {/* Card de Resumen Rápido */}
              <div className="bg-gradient-to-br from-cyan-950/40 to-slate-900 p-8 rounded-3xl border border-cyan-500/20 shadow-lg flex flex-col justify-center">
                <div className="bg-cyan-500/10 w-16 h-16 rounded-2xl flex items-center justify-center mb-6">
                  <AlertCircle className="text-cyan-400" size={32} />
                </div>
                <h2 className="text-3xl font-bold mb-4">Análisis de Oportunidad</h2>
                <p className="text-slate-400 mb-8 leading-relaxed">
                  El algoritmo ha cruzado datos de 4 plataformas. Los productos en la esquina superior izquierda del mapa son tus mejores opciones.
                </p>
                <div className="space-y-5">
                  <div className="flex justify-between items-center p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                    <span className="text-slate-400">Total Analizados</span>
                    <span className="text-2xl font-black text-cyan-400">{results.length}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                    <span className="text-slate-400">Mejor Opción</span>
                    <span className="text-xl font-bold text-green-400 uppercase">
                      {results.sort((a,b) => b.opportunity_score - a.opportunity_score)[0]?.keyword || "-"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Tabla Detallada */}
            <div className="bg-slate-900 rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
              <div className="p-6 border-b border-slate-800 bg-slate-800/20">
                <h2 className="text-xl font-bold">Desglose por Producto</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-slate-500 text-sm uppercase tracking-widest">
                      <th className="p-6 font-semibold">Producto</th>
                      <th className="p-6 font-semibold text-center">Demanda (Score)</th>
                      <th className="p-6 font-semibold text-center">Oferta (Stock)</th>
                      <th className="p-6 font-semibold text-center text-cyan-500">Opp. Score</th>
                      <th className="p-6 font-semibold">Estado del Mercado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {results.map((item: any) => (
                      <tr key={item.keyword} className="hover:bg-cyan-500/5 transition-all group">
                        <td className="p-6">
                          <span className="font-black text-xl uppercase group-hover:text-cyan-400 transition-colors">
                            {item.keyword}
                          </span>
                        </td>
                        <td className="p-6 text-center text-lg font-medium">{item.demand_signal}</td>
                        <td className="p-6 text-center text-lg font-medium">{item.total_supply}</td>
                        <td className="p-6 text-center">
                          <span className="px-4 py-1 bg-cyan-900/30 text-cyan-400 rounded-lg font-mono font-bold text-xl">
                            {item.opportunity_score.toFixed(2)}
                          </span>
                        </td>
                        <td className="p-6">
                          <span className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-black border-2 ${
                            item.recommendation.includes('STRONG') 
                              ? 'bg-green-500/10 text-green-400 border-green-500/30' 
                              : item.recommendation.includes('Avoid')
                              ? 'bg-red-500/10 text-red-400 border-red-500/30'
                              : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                          }`}>
                            {item.recommendation.toUpperCase()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
      
      {/* Footer / Info */}
      <footer className="mt-20 text-center text-slate-600 text-sm pb-10">
        <p>© 2024 TrendArbitrage Portfolio Project • Powered by SerpApi & Next.js</p>
      </footer>
    </div>
  );
}