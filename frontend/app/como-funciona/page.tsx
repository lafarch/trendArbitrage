import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Activity, TrendingUp, Search, ShoppingCart } from 'lucide-react';

export default function HowItWorksPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-[#f58549] selection:text-black">
      
      {/* Header Simple */}
      <header className="py-6 px-8 max-w-4xl mx-auto">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-[#f58549] transition-colors">
          <ArrowLeft size={18} /> Volver al Inicio
        </Link>
      </header>

      <main className="max-w-4xl mx-auto px-8 pb-20">
        <h1 className="text-5xl font-black mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Cómo funciona TrendArbitrage
        </h1>

        <div className="space-y-16 text-gray-300 leading-relaxed">

          {/* Sección Intro */}
          <section className="glass-panel p-8 rounded-3xl">
            <h2 className="text-2xl font-bold text-white mb-4">El Problema del Dropshipping</h2>
            <p className="mb-4">
              El desafío crítico es encontrar productos que la gente quiere comprar <em>antes</em> de que todos los demás vendedores inunden el mercado. El método tradicional implica horas de búsqueda manual en redes sociales y marketplaces, a menudo llegando demasiado tarde a la tendencia.
            </p>
            <p className="font-medium text-white">
              TrendArbitrage automatiza este descubrimiento identificando la intersección entre alta demanda (Google Trends) y baja oferta (Amazon/eBay).
            </p>
          </section>

          {/* Sección Algoritmo */}
          <section>
            <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
              <Activity className="text-[#f58549]" /> El Algoritmo de 3 Fases
            </h2>
            
            <div className="grid gap-6">
              <div className="glass-panel p-6 rounded-2xl border-l-4 border-[#334195] flex gap-4">
                <div className="bg-[#334195]/20 p-3 rounded-xl h-fit"><TrendingUp className="text-[#334195]" /></div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Fase 1: Detección de Demanda (Interés)</h3>
                  <p>Consultamos Google Trends para medir el interés de búsqueda de 0 a 100. Buscamos palabras clave con una "velocidad" ascendente, indicando una tendencia viral en crecimiento, no una moda pasajera.</p>
                </div>
              </div>

              <div className="glass-panel p-6 rounded-2xl border-l-4 border-[#f58549] flex gap-4">
                <div className="bg-[#f58549]/20 p-3 rounded-xl h-fit"><Search className="text-[#f58549]" /></div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Fase 2: Verificación de Suministro (Oferta)</h3>
                  <p>Escaneamos marketplaces como Amazon y eBay en tiempo real para contar cuántos productos existen actualmente. Menos de 50 resultados suele indicar un mercado desatendido.</p>
                </div>
              </div>

              <div className="glass-panel p-6 rounded-2xl border-l-4 border-green-500 flex gap-4">
                 <div className="bg-green-500/20 p-3 rounded-xl h-fit"><ShoppingCart className="text-green-500" /></div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Fase 3: Cálculo de Oportunidad</h3>
                  <p>Cruzamos los datos para generar un score final. La "Alpha" se encuentra donde hay alto volumen de búsqueda pero bajo recuento de productos.</p>
                </div>
              </div>
            </div>
          </section>

          {/* Sección Score */}
          <section className="glass-panel p-8 rounded-3xl bg-gradient-to-br from-[#121212] to-[#334195]/10">
            <h2 className="text-2xl font-bold text-white mb-6">Entendiendo el "Opportunity Score"</h2>
            <div className="mb-8 p-6 bg-[#0a0a0a] rounded-xl text-center font-mono text-lg border border-white/10">
              Score = Interés de Búsqueda / (Suministro Total + 1)
            </div>
            <p>
              El score cuantifica la densidad de demanda por competidor. Un score alto significa que hay mucho interés de los compradores y muy pocas opciones de compra actuales.
            </p>
            
            <div className="mt-8 grid grid-cols-3 gap-4 text-center">
              <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                <div className="font-bold text-green-400 mb-1">🚀 STRONG BUY</div>
                <div className="text-sm opacity-80">Alta demanda, competencia mínima.</div>
              </div>
              <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
                <div className="font-bold text-yellow-400 mb-1">💡 CONSIDER</div>
                <div className="text-sm opacity-80">Buena oportunidad, competencia moderada.</div>
              </div>
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                <div className="font-bold text-red-400 mb-1">❌ AVOID</div>
                <div className="text-sm opacity-80">Mercado saturado o demanda baja.</div>
              </div>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}