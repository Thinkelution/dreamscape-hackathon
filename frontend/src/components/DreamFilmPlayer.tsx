"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import type { DreamResult } from "@/lib/api";

interface DreamFilmPlayerProps {
  dream: DreamResult;
  onNewDream: () => void;
}

export default function DreamFilmPlayer({
  dream,
  onNewDream,
}: DreamFilmPlayerProps) {
  const [activeScene, setActiveScene] = useState(0);
  const [showOverlay, setShowOverlay] = useState(true);

  const schema = dream.dream_schema;
  const scenes = schema?.scenes ?? [];
  const assets = dream.generated_assets;
  const analysis = dream.analysis;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className="relative z-10 max-w-5xl mx-auto px-6"
    >
      {/* Title */}
      <div className="text-center mb-8">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-bold mb-3"
        >
          <span className="bg-gradient-to-r from-violet-400 via-purple-300 to-indigo-400 bg-clip-text text-transparent">
            {schema?.title ?? "Your Dream Film"}
          </span>
        </motion.h1>
        <p className="text-white/40">
          {schema?.overall_mood} &middot;{" "}
          {scenes.length} scenes &middot;{" "}
          {schema?.symbols?.map((s) => s.name).join(", ")}
        </p>
      </div>

      {/* Video Player or Scene Gallery */}
      {assets?.final_video ? (
        <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-black mb-8">
          <video
            src={assets.final_video}
            controls
            autoPlay
            className="w-full aspect-video"
          />
        </div>
      ) : (
        <div className="mb-8">
          {scenes.length > 0 && (
            <div className="relative rounded-2xl overflow-hidden border border-white/10 bg-gradient-to-br from-violet-950/50 to-indigo-950/50 aspect-video mb-4 flex items-center justify-center">
              {scenes[activeScene]?.image_url ? (
                <img
                  src={scenes[activeScene].image_url}
                  alt={scenes[activeScene].description}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-center p-8">
                  <p className="text-6xl mb-4">🌙</p>
                  <p className="text-white/50 text-lg max-w-md">
                    {scenes[activeScene]?.description}
                  </p>
                </div>
              )}

              {showOverlay && scenes[activeScene]?.narration_text && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute bottom-0 inset-x-0 p-6 bg-gradient-to-t from-black/80 to-transparent"
                >
                  <p className="text-white/90 text-lg italic leading-relaxed">
                    &ldquo;{scenes[activeScene].narration_text}&rdquo;
                  </p>
                </motion.div>
              )}

              <button
                onClick={() => setShowOverlay(!showOverlay)}
                className="absolute top-4 right-4 w-8 h-8 rounded-full bg-black/50 flex items-center justify-center text-white/60 hover:text-white/90"
              >
                {showOverlay ? "T" : "t"}
              </button>
            </div>
          )}

          <div className="flex gap-2 overflow-x-auto pb-2">
            {scenes.map((scene, i) => (
              <button
                key={i}
                onClick={() => setActiveScene(i)}
                className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm transition-all ${
                  i === activeScene
                    ? "bg-violet-500/20 border-violet-500/50 text-violet-300"
                    : "bg-white/5 border-white/10 text-white/40 hover:text-white/70"
                } border`}
              >
                Scene {i + 1}: {scene.emotion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Audio Player */}
      {assets?.narration_audio && (
        <div className="mb-8 rounded-xl border border-white/10 bg-white/[0.03] p-4">
          <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-3">
            Narration Audio
          </h3>
          <audio src={assets.narration_audio} controls className="w-full" />
        </div>
      )}

      {/* Dream details */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Symbols */}
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
            Dream Symbols
          </h3>
          <div className="space-y-3">
            {schema?.symbols?.map((symbol, i) => (
              <div key={i}>
                <p className="text-violet-300 font-medium capitalize">
                  {symbol.name}
                </p>
                <p className="text-sm text-white/50">
                  {symbol.possible_meaning}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Narrative arc */}
        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
            Narrative Arc
          </h3>
          <p className="text-white/70 leading-relaxed">
            {schema?.narrative_arc}
          </p>

          {schema?.color_palette && schema.color_palette.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-2">
                Color Palette
              </h4>
              <div className="flex gap-2">
                {schema.color_palette.map((color, i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-lg border border-white/10"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dreamer Insights */}
      {analysis && (analysis.dreamer_insights?.length > 0 || analysis.attitude_summary) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="mb-8"
        >
          <div className="rounded-2xl border border-violet-500/20 bg-gradient-to-br from-violet-950/30 to-indigo-950/20 p-6">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-5">
              What Your Dream Reveals About You
            </h3>

            {/* Attitude Summary */}
            {analysis.attitude_summary && (
              <div className="mb-6 p-4 rounded-xl bg-white/[0.03] border border-white/5">
                <p className="text-white/75 leading-relaxed italic">
                  {analysis.attitude_summary}
                </p>
              </div>
            )}

            {/* Individual Insights */}
            {analysis.dreamer_insights?.length > 0 && (
              <div className="grid md:grid-cols-2 gap-3">
                {analysis.dreamer_insights.map((insight, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + i * 0.1, duration: 0.4 }}
                    className="p-3.5 rounded-xl bg-white/[0.03] border border-white/5"
                  >
                    <p className="text-sm font-semibold text-violet-300 mb-1.5">
                      {insight.trait}
                    </p>
                    <p className="text-xs text-white/50 leading-relaxed">
                      {insight.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <button
          onClick={onNewDream}
          className="px-8 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 transition-all"
        >
          Dream Again
        </button>
      </div>
    </motion.div>
  );
}
