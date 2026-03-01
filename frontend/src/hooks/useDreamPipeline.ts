"use client";

import { useCallback, useRef, useState } from "react";
import {
  submitDream,
  getDreamStatus,
  getDream,
  type DreamProgress,
  type DreamResult,
  type DreamerProfile,
  type NarratorConfig,
} from "@/lib/api";

export type PipelineStage =
  | "idle"
  | "submitting"
  | "interpreting"
  | "generating_visuals"
  | "generating_narration"
  | "composing_video"
  | "complete"
  | "failed";

export function useDreamPipeline() {
  const [stage, setStage] = useState<PipelineStage>("idle");
  const [dreamId, setDreamId] = useState<string | null>(null);
  const [progress, setProgress] = useState<DreamProgress[]>([]);
  const [result, setResult] = useState<DreamResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const startDream = useCallback(
    async (
      text: string,
      userId = "anonymous",
      artStyle = "anime",
      dreamerProfile?: DreamerProfile,
      narratorConfig?: NarratorConfig,
    ) => {
      setStage("submitting");
      setProgress([]);
      setResult(null);
      setError(null);

      try {
        const response = await submitDream(text, userId, artStyle, dreamerProfile, narratorConfig);
        setDreamId(response.dream_id);
        setStage("interpreting");

        // Poll for progress
        pollingRef.current = setInterval(async () => {
          try {
            const status = await getDreamStatus(response.dream_id);
            setProgress(status.progress);

            // Update stage based on latest progress event
            const lastEvent = status.progress[status.progress.length - 1];
            if (lastEvent) {
              switch (lastEvent.event) {
                case "interpretation_complete":
                  setStage("generating_visuals");
                  break;
                case "scene_image_generated":
                  setStage("generating_visuals");
                  break;
                case "narration_ready":
                  setStage("composing_video");
                  break;
                case "video_complete":
                  setStage("composing_video");
                  break;
                case "pipeline_complete":
                  setStage("complete");
                  stopPolling();
                  const dream = await getDream(response.dream_id);
                  setResult(dream);
                  break;
                case "pipeline_error":
                  setStage("failed");
                  setError(
                    (lastEvent.data?.error as string) ?? "Pipeline failed"
                  );
                  stopPolling();
                  break;
              }
            }

            if (
              status.status === "complete" ||
              status.status === "failed"
            ) {
              stopPolling();
              if (status.status === "complete") {
                setStage("complete");
                const dream = await getDream(response.dream_id);
                setResult(dream);
              }
            }
          } catch {
            // Continue polling even if one request fails
          }
        }, 1500);
      } catch (err) {
        setStage("failed");
        setError(err instanceof Error ? err.message : "Failed to submit dream");
      }
    },
    [stopPolling]
  );

  const reset = useCallback(() => {
    stopPolling();
    setStage("idle");
    setDreamId(null);
    setProgress([]);
    setResult(null);
    setError(null);
  }, [stopPolling]);

  return {
    stage,
    dreamId,
    progress,
    result,
    error,
    startDream,
    reset,
  };
}
