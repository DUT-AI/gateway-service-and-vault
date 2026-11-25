"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/contexts/auth-context";
import { VAULT_KEYS } from "./use-vault-queries";
import type {
  SseConnectedEvent,
  SseConnectionStatus,
  SseSecretUpdateEvent,
  VaultSseState,
} from "../types/stream-types";

export interface UseVaultSseOptions {
  scope?: string;
  enabled?: boolean;
  onSecretUpdate?: (event: SseSecretUpdateEvent) => void;
}

export function useVaultSse(
  projectId: string,
  options: UseVaultSseOptions = {}
): VaultSseState {
  const { scope, enabled = true, onSecretUpdate } = options;
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [status, setStatus] = useState<SseConnectionStatus>("connecting");
  const [lastPing, setLastPing] = useState<Date | null>(null);
  const [events, setEvents] = useState<SseSecretUpdateEvent[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [highlightedKeys, setHighlightedKeys] = useState<Set<string>>(
    new Set()
  );

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptRef = useRef<number>(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const watchdogTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastMessageTimeRef = useRef<number>(Date.now());
  const isPausedRef = useRef<boolean>(isPaused);

  isPausedRef.current = isPaused;

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const clearWatchdogTimer = () => {
    if (watchdogTimerRef.current) {
      clearInterval(watchdogTimerRef.current);
      watchdogTimerRef.current = null;
    }
  };

  const triggerHighlight = useCallback((keys: string[]) => {
    setHighlightedKeys((prev) => {
      const next = new Set(prev);
      keys.forEach((k) => next.add(k));
      return next;
    });

    setTimeout(() => {
      setHighlightedKeys((prev) => {
        const next = new Set(prev);
        keys.forEach((k) => next.delete(k));
        return next;
      });
    }, 2500);
  }, []);

  const connect = useCallback(() => {
    if (!enabled || !projectId || !user || typeof window === "undefined") return;

    // Teardown any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    clearReconnectTimer();

    setStatus("connecting");
    lastMessageTimeRef.current = Date.now();

    const baseUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
    const callerId = String(user.id);

    const params = new URLSearchParams();
    params.set("identity_id", callerId);
    if (scope && scope !== "ALL") {
      params.set("scope", scope);
    }

    const streamUrl = `${baseUrl}/vault/projects/${projectId}/stream?${params.toString()}`;

    try {
      const es = new EventSource(streamUrl, { withCredentials: true });
      eventSourceRef.current = es;

      es.addEventListener("connected", (e: MessageEvent) => {
        try {
          const data: SseConnectedEvent = JSON.parse(e.data);
          setStatus("connected");
          reconnectAttemptRef.current = 0;
          lastMessageTimeRef.current = Date.now();
        } catch {
          // ignore parse error
        }
      });

      es.addEventListener("ping", () => {
        setLastPing(new Date());
        setStatus("connected");
        lastMessageTimeRef.current = Date.now();
      });

      es.addEventListener("secret_update", (e: MessageEvent) => {
        lastMessageTimeRef.current = Date.now();
        try {
          const updateEvent: SseSecretUpdateEvent = JSON.parse(e.data);

          if (isPausedRef.current) return;

          // 1. Invalidate TanStack Query caches for real-time hot-reload
          queryClient.invalidateQueries({
            queryKey: [...VAULT_KEYS.all, "secrets", projectId],
          });
          queryClient.invalidateQueries({
            queryKey: [...VAULT_KEYS.all, "scopes", projectId],
          });

          // 2. Trigger row highlight glow
          if (updateEvent.changed_keys?.length) {
            triggerHighlight(updateEvent.changed_keys);
          }

          // 3. Save to live audit history (up to 20 events)
          setEvents((prev) => [updateEvent, ...prev.slice(0, 19)]);

          // 4. Toast notification
          const keysStr = updateEvent.changed_keys.join(", ");
          toast.info(
            `${updateEvent.actor || "Người dùng"} vừa cập nhật biến ${keysStr} (Scope: ${updateEvent.scope_name})`,
            {
              duration: 4000,
            }
          );

          onSecretUpdate?.(updateEvent);
        } catch (err) {
          console.error("Error processing SSE secret_update:", err);
        }
      });

      es.onerror = () => {
        setStatus("connecting");
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }

        // Exponential backoff with jitter
        const attempt = reconnectAttemptRef.current;
        const delay = Math.min(
          1000 * Math.pow(2, attempt) + Math.random() * 500,
          10000
        );
        reconnectAttemptRef.current += 1;

        clearReconnectTimer();
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, delay);
      };
    } catch {
      setStatus("error");
    }
  }, [enabled, projectId, scope, user, queryClient, triggerHighlight, onSecretUpdate]);

  // Watchdog: detect silent connection drop (heartbeat timeout > 35s)
  useEffect(() => {
    if (!enabled || !projectId) return;

    clearWatchdogTimer();
    watchdogTimerRef.current = setInterval(() => {
      const elapsed = Date.now() - lastMessageTimeRef.current;
      if (status === "connected" && elapsed > 35_000) {
        // Force reconnect
        setStatus("connecting");
        connect();
      }
    }, 10_000);

    return () => clearWatchdogTimer();
  }, [enabled, projectId, status, connect]);

  // Visibility change listener: auto-reconnect when tab becomes active again
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (
        document.visibilityState === "visible" &&
        (!eventSourceRef.current || status !== "connected")
      ) {
        connect();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [connect, status]);

  // Connect on mount / options change
  useEffect(() => {
    connect();

    return () => {
      clearReconnectTimer();
      clearWatchdogTimer();
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setStatus("disconnected");
    };
  }, [connect]);

  const reconnect = useCallback(() => {
    reconnectAttemptRef.current = 0;
    connect();
  }, [connect]);

  const togglePause = useCallback(() => {
    setIsPaused((prev) => {
      const next = !prev;
      if (next) {
        toast.info("Đã tạm dừng nhận luồng sự kiện Live Sync");
      } else {
        toast.success("Đã tiếp tục đồng bộ Live Sync");
      }
      return next;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setEvents([]);
  }, []);

  return {
    status,
    lastPing,
    events,
    isPaused,
    highlightedKeys,
    reconnect,
    togglePause,
    clearHistory,
  };
}
