"use client";
import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Search, Plus, X, Activity, ShoppingCart, TrendingUp, Home as HomeIcon, HelpCircle } from 'lucide-react';

// --- TIPOS DE DATOS ---
interface HistoryPoint {
  date: string; // Ej: "Oct 15, 2023" o "2023-10-15"
  value: number;
}

interface AnalysisResult {
  keyword: string;
  interest_score: number;
  total_supply: number;
  opportunity_score: number;
  amazon_count: number;
  ebay_count: number;
  recommendation: string;
  history: HistoryPoint[]; 
}

type TimeRange = "7d" | "1m" | "3m" | "6m" | "12m";

export default function HomePage() {
  // Estados principales
  const [inputVal, setInputVal] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Estados de visualización
  const [timeRange, setTimeRange] = useState<TimeRange>("12m");
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  // --- MANEJO DE KEYWORDS ---
  const addKeyword = () => {
    const trimmed = inputVal.trim();
    if (trimmed && keywords.length < 10 && !keywords.includes(trimmed)) {
      setKeywords([...keywords, trimmed]);
      setInputVal("");
    }
  };

  const removeKeyword = (kw: string) => {
    setKeywords(keywords.filter(k => k !== kw));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') addKeyword();
  };

  // --- LLAMADA A API ---
  const fetchAnalysis = async () => {
    if (keywords.length === 0) return;
    setLoading(true);
    setResults([]);
    setSelectedProduct(null); // Reset selección
    
    try {
      const query = keywords.join(",");
      // Asegúrate de que este puerto sea el correcto para tu backend FastAPI
      const response = await fetch(`http://127.0.0.1:8000/analyze?keywords=${query}`);
      const data = await response.json();
      setResults(data);
      if (data.length > 0) setSelectedProduct(data[0].keyword);
    } catch (error) {
      console.error("API Error:", error);
      alert("No se pudo conectar con el motor de análisis (Backend apagado).");
    }
    setLoading(false);
  };

  // --- CORRECCIÓN CRÍTICA: LÓGICA DE FILTRADO DE FECHAS ---
  const chartData = useMemo(() => {
    if (!selectedProduct || results.length === 0) return [];
    const productData = results.find(r => r.keyword === selectedProduct);
    if (!productData || !productData.history || productData.history.length === 0) return [];

    const fullHistory = productData.history;

    // 1. Calcular la fecha de corte basada en el rango seleccionado
    const now = new Date();
    const cutoffDate = new Date();

    switch(timeRange) {
      case '7d': cutoffDate.setDate(now.getDate() - 7); break;
      case '1m': cutoffDate.setMonth(now.getMonth() - 1); break;
      case '3m': cutoffDate.setMonth(now.getMonth() - 3); break;
      case '6m': cutoffDate.setMonth(now.getMonth() - 6); break;
      case '12m': cutoffDate.setFullYear(now.getFullYear() - 1); break;
    }

    // 2. Filtrar usando comparación de fechas real
    const filteredData = fullHistory.filter(point => {
      // Javascript intenta parsear el string de fecha que viene de Python
      const pointDate = new Date(point.date);
      // Si la fecha es inválida, no la incluimos
      if (isNaN(pointDate.getTime())) return false;
      return pointDate >= cutoffDate;
    });
    
    // Si el filtro nos deja sin datos (ej. data muy vieja), mostramos lo que haya
    return filteredData.length > 0 ? filteredData : fullHistory.slice(-5);

  }, [selectedProduct, timeRange, results]);


  const currentProductStats = results.find(r => r.keyword === selectedProduct);

  return (
    <div className="min-h-screen font-sans selection:bg-[#f58549] selection:text-black">
      
      {/* HEADER RENOVADO (Navegación + Sin borde inferior) */}
      <header className="py-6 px-8 flex justify-between items-center max-w-7xl mx-auto">
         <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-[#f58549] to-[#f58549]/60 p-2.5 rounded-xl shadow-lg shadow-[#f58549]/20">
              <Activity size={22} className="text-white" />
            </div>
            <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              TrendArbitrage
            </h1>
          </div>
          <nav className="flex gap-6 text-sm font-medium text-gray-400">
             <Link href="/" className="hover:text-[#f58549] flex items-center gap-2 transition-colors">
               <HomeIcon size={16} /> Home
             </Link>
             <Link href="/como-funciona" className="hover:text-[#f58549] flex items-center gap-2 transition-colors">
               <HelpCircle size={16} /> ¿Cómo funciona?
             </Link>
          </nav>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 pb-20">
        
        {/* SECCIÓN DE BÚSQUEDA ("Hero" Section) */}
        <section className="mb-16 text-center max-w-3xl mx-auto">
          <h2 className="text-4xl font-extrabold mb-6 leading-tight">
            Descubre oportunidades de nicho <br/>
            <span className="text-[#f58549]">antes que el mercado se sature.</span>
          </h2>

          {/* Consola de Búsqueda (Diseño suavizado) */}
          <div className="glass-panel rounded-3xl p-6 text-left animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Tags Area */}
            <div className="flex flex-wrap gap-2 min-h-[40px] mb-4 p-2 bg-[#0a0a0a]/50 rounded-xl border border-white/5">
              {keywords.length === 0 && (
                <span className="text-gray-500 text-sm italic self-center pl-2">Ej: "mechanical keyboard", "cat toy"...</span>
              )}
              {keywords.map(kw => (
                <span key={kw} className="bg-[#334195]/80 text-white px-3 py-1.5 rounded-lg flex items-center gap-2 text-sm font-medium shadow-sm transition-all hover:bg-[#334195]">
                  {kw}
                  <button onClick={() => removeKeyword(kw)} className="text-white/70 hover:text-white">
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>

            {/* Input y Botón */}
            <div className="flex gap-3 h-14">
              <div className="relative flex-1 h-full">
                <input
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={keywords.length > 0 ? "Añadir otro..." : "Ingresa hasta 10 productos..."}
                  disabled={keywords.length >= 10}
                  className="w-full h-full bg-[#0a0a0a] border border-white/10 rounded-xl px-5 text-lg focus:outline-none focus:border-[#f58549]/50 transition-colors placeholder:text-gray-600"
                />
                {inputVal && (
                  <button 
                    onClick={addKeyword}
                    className="absolute right-3 top-1/2 -translate-y-1/2 bg-[#222] hover:bg-[#333] p-2 rounded-lg text-gray-300 transition-colors"
                  >
                    <Plus size={20} />
                  </button>
                )}
              </div>
              <button 
                onClick={fetchAnalysis}
                disabled={keywords.length === 0 || loading}
                className="h-full bg-gradient-to-r from-[#f58549] to-[#e07538] hover:from-[#e07538] hover:to-[#d06528] text-white px-8 rounded-xl font-bold transition-all disabled:opacity-50 disabled:grayscale flex items-center gap-3 text-lg shadow-lg shadow-[#f58549]/20"
              >
                {loading ? <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"/> : <Search size={20} />}
                <span>Analizar</span>
              </button>
            </div>
             <p className="text-xs text-gray-500 mt-3 text-right px-2">{keywords.length}/10 Keywords</p>
          </div>
        </section>


        {/* SECCIÓN DE RESULTADOS (Layout 2 columnas, Gráfica dominante) */}
        {results.length > 0 && (
          <section className="grid grid-cols-12 gap-8 animate-in fade-in zoom-in duration-500">
            
            {/* COLUMNA IZQUIERDA: Lista de Resultados */}
            <div className="col-span-12 lg:col-span-4 space-y-4">
              <h3 className="text-lg font-bold text-gray-300 flex items-center gap-2 px-2">
                <ShoppingCart size={18} className="text-[#f58549]" /> Resultados del Análisis
              </h3>
              
              <div className="flex flex-col gap-3 max-h-[750px] overflow-y-auto pr-2 custom-scrollbar">
                {results.map((item) => {
                 const isSelected = selectedProduct === item.keyword;
                 const score = item.opportunity_score.toFixed(1);
                 let scoreColor = "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
                 if(item.recommendation.includes('STRONG')) scoreColor = "text-green-400 bg-green-400/10 border-green-400/20";
                 if(item.recommendation.includes('Avoid')) scoreColor = "text-red-400 bg-red-400/10 border-red-400/20";

                 return (
                  <div 
                    key={item.keyword}
                    onClick={() => setSelectedProduct(item.keyword)}
                    className={`p-5 rounded-2xl cursor-pointer transition-all border relative overflow-hidden group ${
                      isSelected 
                        ? 'glass-panel border-[#f58549]/50 bg-gradient-to-br from-[#f58549]/10 to-transparent' 
                        : 'glass-panel border-transparent hover:border-white/10 hover:bg-[#1a1a1a]'
                    }`}
                  >
                    {isSelected && <div className="absolute left-0 top-0 h-full w-1 bg-[#f58549]"></div>}
                    <div className="flex justify-between items-start mb-3">
                      <h4 className={`font-bold text-lg capitalize ${isSelected ? 'text-white': 'text-gray-300'}`}>
                        {item.keyword}
                      </h4>
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-black border ${scoreColor}`}>
                        Score: {score}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                       <div className="bg-[#0a0a0a]/50 p-2 rounded-lg">
                          <span className="block text-gray-500 text-xs mb-1">Saturación (Oferta)</span>
                          <span className="font-bold text-white">{item.total_supply > 0 ? item.total_supply : "N/A"}</span>
                       </div>
                       <div className="bg-[#0a0a0a]/50 p-2 rounded-lg">
                          <span className="block text-gray-500 text-xs mb-1">Interés (Demanda)</span>
                          <span className="font-bold text-white">{item.interest_score}/100</span>
                       </div>
                    </div>
                  </div>
                 )
                })}
              </div>
            </div>


            {/* COLUMNA DERECHA: Visualización Principal (Dominante) */}
            <div className="col-span-12 lg:col-span-8 space-y-6">
              
              {/* Contenedor de la Gráfica */}
              <div className="glass-panel p-8 rounded-3xl h-[500px] flex flex-col relative overflow-hidden">
                 {/* Fondo de gradiente sutil */}
                 <div className="absolute inset-0 bg-gradient-to-tr from-[#334195]/10 via-transparent to-[#f58549]/5 pointer-events-none"></div>

                <div className="flex flex-wrap justify-between items-center mb-8 relative z-10">
                  <div>
                    <h3 className="text-2xl font-black flex items-center gap-3">
                      <TrendingUp size={24} className="text-[#f58549]" /> 
                      <span className="capitalize">{selectedProduct}</span>
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Histórico de Interés de Búsqueda (Google Trends)
                    </p>
                  </div>
                  
                  {/* Botones de Filtro Temporal */}
                  <div className="flex bg-[#0a0a0a] rounded-xl p-1 border border-white/5">
                    {(['7d', '1m', '3m', '6m', '12m'] as TimeRange[]).map((range) => (
                      <button
                        key={range}
                        onClick={() => setTimeRange(range)}
                        className={`px-4 py-1.5 text-sm font-bold rounded-lg transition-all ${
                          timeRange === range 
                            ? 'bg-[#334195] text-white shadow-md' 
                            : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                        }`}
                      >
                        {range.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                {/* GRÁFICA RECHARTS CORREGIDA */}
                <div className="flex-1 w-full relative z-10">
                  {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorInterest" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f58549" stopOpacity={0.6}/>
                          <stop offset="95%" stopColor="#f58549" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis 
                        dataKey="date" 
                        stroke="#444"
                        fontSize={11}
                        tickMargin={15}
                        minTickGap={40}
                        axisLine={false}
                        tickFormatter={(value) => {
                            // Formatear fecha corta si es necesario
                            const d = new Date(value);
                            return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                        }}
                      />
                      <YAxis 
                        stroke="#444"
                        fontSize={11}
                        domain={[0, 100]}
                        axisLine={false}
                        tickLine={false}
                        tickMargin={10}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#121212', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
                        itemStyle={{ color: '#f58549', fontWeight: 'bold' }}
                        labelStyle={{ color: '#888', marginBottom: '5px' }}
                        cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }}
                      />
                      
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#f58549"
                        strokeWidth={3}
                        fillOpacity={1} 
                        fill="url(#colorInterest)" 
                        name="Interés (0-100)"
                        activeDot={{ r: 6, stroke: '#121212', strokeWidth: 2, fill: '#f58549' }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                  ) : (
                      <div className="h-full flex items-center justify-center text-gray-500 flex-col gap-2">
                          <Activity size={40} className="text-gray-700 mb-2" />
                          <p>No hay datos históricos suficientes para este rango.</p>
                      </div>
                  )}
                </div>
              </div>

              {/* Breakdown de Marketplaces (Tarjetas inferiores) */}
              {currentProductStats && (
                <div className="grid grid-cols-4 gap-4">
                  {[
                    { name: 'Amazon', val: currentProductStats.amazon_count, icon: 'A' },
                    { name: 'eBay', val: currentProductStats.ebay_count, icon: 'E' },
                    { name: 'Walmart', val: 0, icon: 'W' }, 
                    { name: 'AliExpress', val: 0, icon: 'Al' },
                  ].map((m) => (
                    <div key={m.name} className="glass-panel p-5 rounded-2xl flex flex-col items-center justify-center text-center relative overflow-hidden group">
                       <div className="text-3xl font-black text-white mb-1 relative z-10">
                        {m.val > 0 ? m.val.toLocaleString() : <span className="text-gray-600 text-xl">N/A</span>}
                       </div>
                      <p className="text-gray-500 text-xs uppercase font-bold tracking-wider relative z-10">{m.name}</p>
                      {/* Icono de fondo decorativo */}
                      <span className="absolute -bottom-4 -right-2 text-7xl font-black text-white/5 select-none group-hover:text-white/10 transition-colors">
                        {m.icon}
                      </span>
                    </div>
                  ))}
                </div>
              )}

            </div>
          </section>
        )}
      </main>
    </div>
  );
}