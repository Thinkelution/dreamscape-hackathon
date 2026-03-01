"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface DreamerProfile {
  gender: string;
  age_range: string;
  ethnicity: string;
}

export interface NarratorConfig {
  gender: string;
  style: string;
}

interface DreamInputProps {
  onSubmit: (
    text: string,
    artStyle: string,
    dreamerProfile: DreamerProfile,
    narratorConfig: NarratorConfig
  ) => void;
  isSubmitting: boolean;
}

const PLACEHOLDERS = [
  "I was flying over an ocean of glass, and the clouds were made of whispers...",
  "There was a staircase that spiraled into the sky, each step a different color...",
  "I found myself in a library where the books had wings and flew around me...",
  "A giant clock was melting over a floating island covered in purple flowers...",
];

const ART_STYLES = [
  { id: "anime", label: "Anime", icon: "🌸" },
  { id: "realistic", label: "Realistic", icon: "📷" },
  { id: "watercolor", label: "Watercolor", icon: "🎨" },
  { id: "oil-painting", label: "Oil Painting", icon: "🖼️" },
  { id: "pixel-art", label: "Pixel Art", icon: "👾" },
  { id: "cyberpunk", label: "Cyberpunk", icon: "🌃" },
  { id: "fantasy", label: "Fantasy", icon: "🧙" },
];

const GENDERS = [
  { id: "unspecified", label: "Any" },
  { id: "male", label: "Male" },
  { id: "female", label: "Female" },
  { id: "non-binary", label: "Non-binary" },
];

const AGE_RANGES = [
  { id: "unspecified", label: "Any" },
  { id: "child", label: "Child" },
  { id: "teenager", label: "Teen" },
  { id: "young adult", label: "Young Adult" },
  { id: "adult", label: "Adult" },
  { id: "elder", label: "Elder" },
];

const ETHNICITIES = [
  { id: "unspecified", label: "Any" },
  { id: "east-asian", label: "East Asian" },
  { id: "south-asian", label: "South Asian" },
  { id: "southeast-asian", label: "SE Asian" },
  { id: "black", label: "Black" },
  { id: "white", label: "White" },
  { id: "hispanic-latino", label: "Hispanic" },
  { id: "middle-eastern", label: "Middle Eastern" },
  { id: "mixed", label: "Mixed" },
];

const NARRATOR_GENDERS = [
  { id: "female", label: "Female" },
  { id: "male", label: "Male" },
];

const NARRATOR_STYLES = [
  { id: "calm", label: "Calm", icon: "🌊" },
  { id: "warm", label: "Warm", icon: "☀️" },
  { id: "dramatic", label: "Dramatic", icon: "🎭" },
  { id: "youthful", label: "Youthful", icon: "✨" },
];

function ChipGroup({
  options,
  value,
  onChange,
  disabled,
  color = "violet",
}: {
  options: { id: string; label: string; icon?: string }[];
  value: string;
  onChange: (id: string) => void;
  disabled?: boolean;
  color?: "violet" | "indigo" | "rose";
}) {
  const colorMap = {
    violet: {
      active: "bg-violet-600/80 text-white border-violet-400/50 shadow-violet-500/20",
      inactive: "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white/70",
    },
    indigo: {
      active: "bg-indigo-600/80 text-white border-indigo-400/50 shadow-indigo-500/20",
      inactive: "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white/70",
    },
    rose: {
      active: "bg-rose-600/80 text-white border-rose-400/50 shadow-rose-500/20",
      inactive: "bg-white/5 text-white/50 border-white/10 hover:bg-white/10 hover:text-white/70",
    },
  };
  const colors = colorMap[color];

  return (
    <div className="flex flex-wrap gap-1.5">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onChange(opt.id)}
          disabled={disabled}
          className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all border ${
            value === opt.id
              ? `${colors.active} shadow-lg`
              : colors.inactive
          }`}
        >
          {opt.icon && <span className="mr-1">{opt.icon}</span>}
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default function DreamInput({ onSubmit, isSubmitting }: DreamInputProps) {
  const [text, setText] = useState("");
  const [artStyle, setArtStyle] = useState("anime");
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [dreamerGender, setDreamerGender] = useState("unspecified");
  const [dreamerAge, setDreamerAge] = useState("unspecified");
  const [dreamerEthnicity, setDreamerEthnicity] = useState("unspecified");

  const [narratorGender, setNarratorGender] = useState("female");
  const [narratorStyle, setNarratorStyle] = useState("calm");

  const [placeholder] = useState(
    () => PLACEHOLDERS[Math.floor(Math.random() * PLACEHOLDERS.length)]
  );

  const handleSubmit = () => {
    if (text.trim().length > 10) {
      onSubmit(
        text.trim(),
        artStyle,
        { gender: dreamerGender, age_range: dreamerAge, ethnicity: dreamerEthnicity },
        { gender: narratorGender, style: narratorStyle }
      );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="relative z-10 max-w-3xl mx-auto px-6"
    >
      <div className="text-center mb-10">
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
            rows={5}
            className="w-full bg-transparent text-white/90 placeholder-white/20 text-lg leading-relaxed px-6 py-5 rounded-xl resize-none focus:outline-none"
          />

          {/* Visual Style */}
          <div className="px-4 py-2.5 border-t border-white/5">
            <p className="text-xs text-white/40 mb-1.5 uppercase tracking-wider font-medium">Visual Style</p>
            <ChipGroup options={ART_STYLES} value={artStyle} onChange={setArtStyle} disabled={isSubmitting} />
          </div>

          {/* Advanced Config Toggle */}
          <div className="px-4 py-2 border-t border-white/5">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs text-white/30 hover:text-white/60 transition-colors uppercase tracking-wider font-medium flex items-center gap-1.5"
            >
              <span className={`transition-transform inline-block ${showAdvanced ? "rotate-90" : ""}`}>
                &#9654;
              </span>
              Customize Dreamer & Narrator
            </button>
          </div>

          {/* Advanced Config Panels */}
          <AnimatePresence>
            {showAdvanced && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="overflow-hidden"
              >
                <div className="px-4 py-3 border-t border-white/5 space-y-3">
                  {/* Dreamer Profile */}
                  <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3">
                    <p className="text-xs text-violet-400/80 mb-2.5 uppercase tracking-wider font-semibold">
                      Dreamer Profile
                    </p>
                    <div className="space-y-2">
                      <div>
                        <p className="text-[10px] text-white/30 mb-1 uppercase tracking-wider">Gender</p>
                        <ChipGroup options={GENDERS} value={dreamerGender} onChange={setDreamerGender} disabled={isSubmitting} />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/30 mb-1 uppercase tracking-wider">Age</p>
                        <ChipGroup options={AGE_RANGES} value={dreamerAge} onChange={setDreamerAge} disabled={isSubmitting} />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/30 mb-1 uppercase tracking-wider">Ethnicity</p>
                        <ChipGroup options={ETHNICITIES} value={dreamerEthnicity} onChange={setDreamerEthnicity} disabled={isSubmitting} />
                      </div>
                    </div>
                  </div>

                  {/* Narrator Config */}
                  <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3">
                    <p className="text-xs text-indigo-400/80 mb-2.5 uppercase tracking-wider font-semibold">
                      Narrator Voice
                    </p>
                    <div className="space-y-2">
                      <div>
                        <p className="text-[10px] text-white/30 mb-1 uppercase tracking-wider">Gender</p>
                        <ChipGroup options={NARRATOR_GENDERS} value={narratorGender} onChange={setNarratorGender} disabled={isSubmitting} color="indigo" />
                      </div>
                      <div>
                        <p className="text-[10px] text-white/30 mb-1 uppercase tracking-wider">Style</p>
                        <ChipGroup options={NARRATOR_STYLES} value={narratorStyle} onChange={setNarratorStyle} disabled={isSubmitting} color="indigo" />
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit bar */}
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
        className="mt-6 text-center"
      >
        <p className="text-sm text-white/25">
          Powered by Gemini 2.5 Flash + Interleaved Image Generation
        </p>
      </motion.div>
    </motion.div>
  );
}
