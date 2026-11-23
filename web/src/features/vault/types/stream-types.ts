export type SseConnectionStatus =
  | "connected"
  | "connecting"
  | "disconnected"
  | "error";

export interface SseConnectedEvent {
  project_id: string;
  status: "active";
  timestamp: string;
}

export interface SseSecretUpdateEvent {
  event_id: string;
  project_id: string;
  scope_name: string;
  changed_keys: string[];
  new_version: number;
  actor: string;
  timestamp: string;
}

export interface SsePingEvent {
  timestamp: string;
}

export interface VaultSseState {
  status: SseConnectionStatus;
  lastPing: Date | null;
  events: SseSecretUpdateEvent[];
  isPaused: boolean;
  highlightedKeys: Set<string>;
  reconnect: () => void;
  togglePause: () => void;
  clearHistory: () => void;
}
