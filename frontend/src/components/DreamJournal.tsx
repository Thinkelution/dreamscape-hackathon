"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { listDreams, type DreamResult } from "@/lib/api";

interface DreamJournalProps {
  userId: string;
  onSelectDream: (dream: DreamResult) => void;
}

export default function DreamJournal({
  userId,
  onSelectDream,
}: DreamJournalProps) {
  const [dreams, setDreams] = useState<DreamResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await listDreams(userId);
        setDreams(data.dreams ?? []);
      } catch {
        setDreams([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [userId]);

  if (loading) {
    return (
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center py-20">
        <div className="w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-white/40 mt-4">Loading dream journal...</p>
      </div>
    );
  }

  if (dreams.length === 0) {
    return (
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center py-20">
        <p className="text-6xl mb-6">🌌</p>
        <h2 className="text-2xl font-bold text-white/80 mb-2">
          Your dream journal is empty
        </h2>
        <p className="text-white/40">
          Submit your first dream to begin building your visual journal.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative z-10 max-w-6xl mx-auto px-6"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold mb-2">
          <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            Dream Journal
          </span>
        </h2>
        <p className="text-white/40">{dreams.length} dreams recorded</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {dreams.map((dream, i) => {
          const schema = dream.dream_schema;
          return (
            <motion.button
              key={dream.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => onSelectDream(dream)}
              className="text-left rounded-xl border border-white/10 bg-white/[0.03] hover:bg-white/[0.06] p-5 transition-all group"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-violet-300 group-hover:text-violet-200 line-clamp-1">
                  {schema?.title ?? "Untitled Dream"}
                </h3>
                <span className="text-xs text-white/30 whitespace-nowrap ml-2">
                  {new Date(dream.created_at).toLocaleDateString()}
                </span>
              </div>

              {schema?.overall_mood && (
                <span className="inline-block px-2 py-0.5 rounded text-xs bg-violet-500/20 text-violet-300 mb-3">
                  {schema.overall_mood}
                </span>
              )}

              <p className="text-sm text-white/40 line-clamp-3">
                {dream.raw_text}
              </p>

              {schema?.symbols && schema.symbols.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {schema.symbols.slice(0, 4).map((s, j) => (
                    <span
                      key={j}
                      className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-white/30"
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
