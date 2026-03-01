"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { PipelineStage } from "@/hooks/useDreamPipeline";
import type { DreamProgress } from "@/lib/api";

interface GenerationProgressProps {
  stage: PipelineStage;
  progress: DreamProgress[];
}

const PIPELINE_STAGES = [
  {
    key: "interpreting",
    label: "Dream Interpreter",
    description: "Parsing your dream into scenes, symbols, and emotions...",
    icon: "🌙",
  },
  {
    key: "generating_visuals",
    label: "Visual Director",
    description: "Generating surrealist imagery with Gemini interleaved output...",
    icon: "🎨",
  },
  {
    key: "generating_narration",
    label: "Narrative Voice",
    description: "Creating ethereal narration with Cloud TTS...",
    icon: "🎙️",
  },
  {
    key: "composing_video",
    label: "Scene Composer",
    description: "Composing dream film with Ken Burns effects...",
    icon: "🎬",
  },
];

function getStageIndex(stage: PipelineStage): number {
  const map: Record<string, number> = {
    interpreting: 0,
    generating_visuals: 1,
    generating_narration: 2,
    composing_video: 3,
    complete: 4,
  };
  return map[stage] ?? -1;
}

export default function GenerationProgress({
  stage,
  progress,
}: GenerationProgressProps) {
  const currentIndex = getStageIndex(stage);

  const interpretationData = progress.find(
    (p) => p.event === "interpretation_complete"
  );
  const sceneImages = progress.filter(
    (p) => p.event === "scene_image_generated"
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative z-10 max-w-4xl mx-auto px-6"
    >
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold mb-2">
          <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            Generating your dream film
          </span>
        </h2>
        {interpretationData && (
          <motion.p
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-white/60 text-lg"
          >
            &ldquo;{(interpretationData.data.title as string) ?? ""}&rdquo;
          </motion.p>
        )}
      </div>

      {/* Pipeline stages */}
      <div className="grid gap-4 mb-10">
        {PIPELINE_STAGES.map((s, i) => {
          const isActive = i === currentIndex;
          const isDone = i < currentIndex;

          return (
            <motion.div
              key={s.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`flex items-center gap-4 rounded-xl p-4 border transition-all duration-500 ${
                isActive
                  ? "border-violet-500/50 bg-violet-500/10"
                  : isDone
                  ? "border-green-500/30 bg-green-500/5"
                  : "border-white/5 bg-white/[0.02]"
              }`}
            >
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center text-xl ${
                  isActive
                    ? "bg-violet-500/20"
                    : isDone
                    ? "bg-green-500/20"
                    : "bg-white/5"
                }`}
              >
                {isDone ? "✓" : s.icon}
              </div>
              <div className="flex-1">
                <p
                  className={`font-medium ${
                    isActive
                      ? "text-violet-300"
                      : isDone
                      ? "text-green-300"
                      : "text-white/30"
                  }`}
                >
                  {s.label}
                </p>
                <p
                  className={`text-sm ${
                    isActive ? "text-white/50" : "text-white/20"
                  }`}
                >
                  {s.description}
                </p>
              </div>
              {isActive && (
                <div className="w-5 h-5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Scene image previews as they come in */}
      <AnimatePresence>
        {sceneImages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <h3 className="text-sm font-medium text-white/40 uppercase tracking-wider mb-4">
              Scenes generated: {sceneImages.length} /{" "}
              {(sceneImages[0]?.data?.total_scenes as number) ?? "?"}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {sceneImages.map((img, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.2 }}
                  className="aspect-video rounded-lg bg-white/5 border border-white/10 overflow-hidden flex items-center justify-center"
                >
                  <div className="text-center p-4">
                    <p className="text-xs text-white/40">Scene {i + 1}</p>
                    <p className="text-xs text-white/60 mt-1 line-clamp-2">
                      {(img.data?.narration as string)?.slice(0, 80)}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
