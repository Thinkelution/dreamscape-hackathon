"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface DreamInputProps {
  onSubmit: (text: string) => void;
  isSubmitting: boolean;
}

const PLACEHOLDERS = [
  "I was flying over an ocean of glass, and the clouds were made of whispers...",
  "There was a staircase that spiraled into the sky, each step a different color...",
  "I found myself in a library where the books had wings and flew around me...",
  "A giant clock was melting over a floating island covered in purple flowers...",
];

export default function DreamInput({ onSubmit, isSubmitting }: DreamInputProps) {
  const [text, setText] = useState("");
  const [placeholder] = useState(
    () => PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]
  );

  const handleSubmit = () => {
    if (text.trim().length > 10) {
      onSubmit(text.trim());
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="relative z-10 max-w-3xl mx-auto px-6"
    >
      <div className="text-center mb-12">
        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-5xl md:text-6xl font-bold mb-4"
        >
          <span className="bg-gradient-to-r from-violet-400 via-purple-300 to-indigo-400 bg-clip-text text-transparent">
            Describe your dream
          </span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-lg text-white/50"
        >
          Write it messy, write it raw — we&apos;ll turn it into a surrealist
          film
        </motion.p>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="relative"
      >
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-1 glow-border">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={placeholder}
            disabled={isSubmitting}
            rows={8}
            className="w-full bg-transparent text-white/90 placeholder-white/20 text-lg leading-relaxed px-6 py-5 rounded-xl resize-none focus:outline-none"
          />
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/5">
            <span className="text-sm text-white/30">
              {text.length > 0
                ? `${text.length} characters`
                : "Minimum 10 characters"}
            </span>
            <button
              onClick={handleSubmit}
              disabled={text.trim().length <= 10 || isSubmitting}
              className="px-8 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {isSubmitting ? "Entering the dream..." : "Generate Dream Film"}
            </button>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
        className="mt-8 text-center"
      >
        <p className="text-sm text-white/25">
          Powered by Gemini 2.0 Flash — interleaved text + image generation
        </p>
      </motion.div>
    </motion.div>
  );
}
