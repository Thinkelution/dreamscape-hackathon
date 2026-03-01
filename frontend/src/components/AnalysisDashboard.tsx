"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getAnalysis, refreshAnalysis } from "@/lib/api";

interface AnalysisDashboardProps {
  userId: string;
}

interface AnalysisData {
  total_dreams: number;
  recurring_symbols: Array<{
    symbol: string;
    count: number;
    interpretation: string;
  }>;
  emotional_patterns: Array<{
    pattern: string;
    frequency: string;
    correlation: string;
  }>;
  connections: Array<{
    shared_elements: string[];
    insight: string;
  }>;
}

export default function AnalysisDashboard({
  userId,
}: AnalysisDashboardProps) {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getAnalysis(userId);
        setAnalysis(data.analysis);
      } catch {
        setAnalysis(null);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [userId]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const data = await refreshAnalysis(userId);
      setAnalysis(data.analysis);
    } catch {
      // ignore
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center py-20">
        <div className="w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-white/40 mt-4">Analyzing your dreams...</p>
      </div>
    );
  }

  if (!analysis || analysis.total_dreams === 0) {
    return (
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center py-20">
        <p className="text-6xl mb-6">🔮</p>
        <h2 className="text-2xl font-bold text-white/80 mb-2">
          Not enough dreams to analyze
        </h2>
        <p className="text-white/40">
          Record more dreams to unlock pattern analysis and insights.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative z-10 max-w-5xl mx-auto px-6"
    >
      <div className="flex items-center justify-between mb-10">
        <div>
          <h2 className="text-3xl font-bold">
            <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
              Dream Analysis
            </span>
          </h2>
          <p className="text-white/40 mt-1">
            Patterns across {analysis.total_dreams} dreams
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 hover:bg-white/20 border border-white/10 transition-all disabled:opacity-50"
        >
          {refreshing ? "Analyzing..." : "Refresh Analysis"}
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recurring Symbols */}
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
            Recurring Symbols
          </h3>
          <div className="space-y-4">
            {analysis.recurring_symbols?.map((symbol, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-violet-300 font-medium capitalize">
                    {symbol.symbol}
                  </span>
                  <span className="text-xs text-white/30">
                    {symbol.count} dreams
                  </span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-1.5 mb-2">
                  <div
                    className="bg-gradient-to-r from-violet-500 to-indigo-500 h-1.5 rounded-full"
                    style={{
                      width: `${Math.min(
                        (symbol.count / analysis.total_dreams) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>
                <p className="text-sm text-white/50">
                  {symbol.interpretation}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Emotional Patterns */}
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
            Emotional Patterns
          </h3>
          <div className="space-y-4">
            {analysis.emotional_patterns?.map((pattern, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="rounded-lg bg-white/[0.03] p-4 border border-white/5"
              >
                <p className="text-white/80 font-medium mb-1">
                  {pattern.pattern}
                </p>
                {pattern.frequency && (
                  <p className="text-sm text-violet-300/70">
                    {pattern.frequency}
                  </p>
                )}
                {pattern.correlation && (
                  <p className="text-sm text-white/40 mt-1">
                    {pattern.correlation}
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Dream Connections */}
        {analysis.connections && analysis.connections.length > 0 && (
          <div className="md:col-span-2 rounded-xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
              Dream Connections
            </h3>
            <div className="grid sm:grid-cols-2 gap-4">
              {analysis.connections.map((conn, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="rounded-lg bg-white/[0.03] p-4 border border-white/5"
                >
                  <div className="flex flex-wrap gap-1 mb-2">
                    {conn.shared_elements?.map((el, j) => (
                      <span
                        key={j}
                        className="text-xs px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300"
                      >
                        {el}
                      </span>
                    ))}
                  </div>
                  <p className="text-sm text-white/60">{conn.insight}</p>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
