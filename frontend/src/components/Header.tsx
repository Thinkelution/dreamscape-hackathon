"use client";

import { useAuth } from "@/hooks/useAuth";

interface HeaderProps {
  onNavigate: (page: "home" | "journal" | "analysis") => void;
  currentPage: string;
}

export default function Header({ onNavigate, currentPage }: HeaderProps) {
  const { user, signIn, signOut } = useAuth();

  return (
    <header className="relative z-10 border-b border-white/10 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <button
          onClick={() => onNavigate("home")}
          className="flex items-center gap-3 group"
        >
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </div>
          <span className="text-xl font-semibold tracking-tight group-hover:text-violet-300 transition-colors">
            Dreamscape
          </span>
        </button>

        <nav className="hidden md:flex items-center gap-6">
          {[
            { key: "home", label: "New Dream" },
            { key: "journal", label: "Journal" },
            { key: "analysis", label: "Analysis" },
          ].map((item) => (
            <button
              key={item.key}
              onClick={() =>
                onNavigate(item.key as "home" | "journal" | "analysis")
              }
              className={`text-sm font-medium transition-colors ${
                currentPage === item.key
                  ? "text-violet-400"
                  : "text-white/60 hover:text-white/90"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              {user.photoURL && (
                <img
                  src={user.photoURL}
                  alt=""
                  className="w-8 h-8 rounded-full border border-white/20"
                />
              )}
              <span className="text-sm text-white/70 hidden sm:inline">
                {user.displayName?.split(" ")[0]}
              </span>
              <button
                onClick={signOut}
                className="text-xs text-white/40 hover:text-white/70 transition-colors"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              onClick={signIn}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-white/10 hover:bg-white/20 border border-white/10 transition-all"
            >
              Sign in with Google
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
