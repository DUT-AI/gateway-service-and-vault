import { useQuery } from "@tanstack/react-query";
import { auditService } from "../services/audit-service";
import type {
  AuditEventList,
  AuditFilterParams,
  SecurityAlerts,
} from "../types";

export const AUDIT_EVENTS_QUERY_KEY = ["gateway", "audit-events"] as const;
export const SECURITY_ALERTS_QUERY_KEY = ["gateway", "security-alerts"] as const;

export function useAuditEventsQuery(params?: AuditFilterParams) {
  return useQuery<AuditEventList, Error>({
    queryKey: [...AUDIT_EVENTS_QUERY_KEY, params],
    queryFn: () => auditService.getAuditEvents(params),
    staleTime: 1000 * 10, // 10 seconds
    refetchInterval: 1000 * 15, // poll every 15s for live audit feed
  });
}

export function useSecurityAlertsQuery(
  windowMinutes: number = 5,
  threshold: number = 3
) {
  return useQuery<SecurityAlerts, Error>({
    queryKey: [...SECURITY_ALERTS_QUERY_KEY, windowMinutes, threshold],
    queryFn: () => auditService.getSecurityAlerts(windowMinutes, threshold),
    staleTime: 1000 * 10,
    refetchInterval: 1000 * 15, // poll for alerts
  });
}
