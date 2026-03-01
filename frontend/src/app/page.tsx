"use client";

import { useState } from "react";
import StarField from "@/components/StarField";
import Header from "@/components/Header";
import DreamInput from "@/components/DreamInput";
import GenerationProgress from "@/components/GenerationProgress";
import DreamFilmPlayer from "@/components/DreamFilmPlayer";
import DreamJournal from "@/components/DreamJournal";
import AnalysisDashboard from "@/components/AnalysisDashboard";
import { useDreamPipeline } from "@/hooks/useDreamPipeline";
import { useAuth } from "@/hooks/useAuth";
import type { DreamResult } from "@/lib/api";

type Page = "home" | "journal" | "analysis";

export default function Home() {
  const [page, setPage] = useState<Page>("home");
  const [viewingDream, setViewingDream] = useState<DreamResult | null>(null);
  const { stage, progress, result, error, startDream, reset } =
    useDreamPipeline();
  const { userId } = useAuth();

  const handleSubmit = (
    text: string,
    artStyle: string,
    dreamerProfile?: { gender: string; age_range: string; ethnicity: string },
    narratorConfig?: { gender: string; style: string },
  ) => {
    startDream(text, userId, artStyle, dreamerProfile, narratorConfig);
  };

  const handleNewDream = () => {
    reset();
    setViewingDream(null);
    setPage("home");
  };

  const handleSelectDream = (dream: DreamResult) => {
    setViewingDream(dream);
  };

  const renderContent = () => {
    // Show a selected dream from the journal
    if (viewingDream) {
      return (
        <DreamFilmPlayer dream={viewingDream} onNewDream={handleNewDream} />
      );
    }

    // Journal page
    if (page === "journal") {
      return (
        <DreamJournal userId={userId} onSelectDream={handleSelectDream} />
      );
    }

    // Analysis page
    if (page === "analysis") {
      return <AnalysisDashboard userId={userId} />;
    }

    // Home: dream pipeline flow
    if (stage === "idle") {
      return (
        <DreamInput onSubmit={handleSubmit} isSubmitting={false} />
      );
    }

    if (stage === "complete" && result) {
      return <DreamFilmPlayer dream={result} onNewDream={handleNewDream} />;
    }

    if (stage === "failed") {
      return (
        <div className="relative z-10 max-w-3xl mx-auto px-6 text-center py-20">
          <p className="text-6xl mb-6">💫</p>
          <h2 className="text-2xl font-bold text-red-300 mb-2">
            Dream faded too quickly
          </h2>
          <p className="text-white/50 mb-6">
            {error ?? "Something went wrong during generation."}
          </p>
          <button
            onClick={handleNewDream}
            className="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 transition-all"
          >
            Try Again
          </button>
        </div>
      );
    }

    // Processing stages
    return <GenerationProgress stage={stage} progress={progress} />;
  };

  return (
    <div className="min-h-screen flex flex-col">
      <StarField />
      <Header
        onNavigate={(p) => {
          setViewingDream(null);
          setPage(p);
          if (p === "home") reset();
        }}
        currentPage={page}
      />
      <main className="flex-1 flex items-center justify-center py-12">
        {renderContent()}
      </main>
    </div>
  );
}
