const API_BASE = "/api";

export interface DreamerProfile {
  gender: string;
  age_range: string;
  ethnicity: string;
}

export interface NarratorConfig {
  gender: string;
  style: string;
}

export interface DreamCreateResponse {
  dream_id: string;
  status: string;
  message: string;
}

export interface DreamProgress {
  event: string;
  data: Record<string, unknown>;
}

export interface DreamStatusResponse {
  dream_id: string;
  status: string;
  progress: DreamProgress[];
}

export interface DreamerInsight {
  trait: string;
  description: string;
}

export interface DreamResult {
  id: string;
  raw_text: string;
  status: string;
  dream_schema?: {
    title: string;
    scenes: Array<{
      description: string;
      emotion: string;
      visual_style: string;
      narration_text?: string;
      image_url?: string;
    }>;
    overall_mood: string;
    symbols: Array<{ name: string; possible_meaning: string }>;
    narrative_arc: string;
    color_palette: string[];
  };
  generated_assets?: {
    scene_images: string[];
    narration_audio?: string;
    final_video?: string;
  };
  analysis?: {
    emotions: string[];
    symbols: string[];
    title: string;
    mood: string;
    dreamer_insights: DreamerInsight[];
    attitude_summary: string;
  };
  created_at: string;
}

export async function submitDream(
  text: string,
  userId = "anonymous",
  artStyle = "anime",
  dreamerProfile?: DreamerProfile,
  narratorConfig?: NarratorConfig
): Promise<DreamCreateResponse> {
  const res = await fetch(`${API_BASE}/dreams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      user_id: userId,
      art_style: artStyle,
      dreamer_profile: dreamerProfile ?? { gender: "unspecified", age_range: "adult", ethnicity: "unspecified" },
      narrator_config: narratorConfig ?? { gender: "female", style: "calm" },
    }),
  });
  if (!res.ok) throw new Error(`Failed to submit dream: ${res.statusText}`);
  return res.json();
}

export async function getDreamStatus(
  dreamId: string
): Promise<DreamStatusResponse> {
  const res = await fetch(`${API_BASE}/dreams/${dreamId}/status`);
  if (!res.ok) throw new Error(`Failed to get status: ${res.statusText}`);
  return res.json();
}

export async function getDream(dreamId: string): Promise<DreamResult> {
  const res = await fetch(`${API_BASE}/dreams/${dreamId}`);
  if (!res.ok) throw new Error(`Failed to get dream: ${res.statusText}`);
  return res.json();
}

export async function listDreams(
  userId = "anonymous"
): Promise<{ dreams: DreamResult[] }> {
  const res = await fetch(`${API_BASE}/dreams?user_id=${userId}`);
  if (!res.ok) throw new Error(`Failed to list dreams: ${res.statusText}`);
  return res.json();
}

export async function deleteDream(dreamId: string): Promise<void> {
  await fetch(`${API_BASE}/dreams/${dreamId}`, { method: "DELETE" });
}

export async function getAnalysis(userId = "anonymous") {
  const res = await fetch(`${API_BASE}/analysis?user_id=${userId}`);
  if (!res.ok) throw new Error(`Failed to get analysis: ${res.statusText}`);
  return res.json();
}

export async function refreshAnalysis(userId = "anonymous") {
  const res = await fetch(`${API_BASE}/analysis/refresh?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to refresh analysis: ${res.statusText}`);
  return res.json();
}

export function createDreamWebSocket(
  dreamId: string,
  onMessage: (event: DreamProgress) => void,
  onComplete?: () => void,
  onError?: (error: Event) => void
): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(
    `${protocol}//${window.location.host}/api/dreams/${dreamId}/stream`
  );

  ws.onmessage = (evt) => {
    const data = JSON.parse(evt.data) as DreamProgress;
    onMessage(data);
    if (
      data.event === "pipeline_complete" ||
      data.event === "pipeline_error"
    ) {
      onComplete?.();
    }
  };

  ws.onerror = (evt) => onError?.(evt);

  return ws;
}
