import { api } from "@/lib/api";
import type {
  AuditEventList,
  AuditFilterParams,
  SecurityAlerts,
} from "../types";

export const auditService = {
  async getAuditEvents(params?: AuditFilterParams): Promise<AuditEventList> {
    const { data } = await api.get<AuditEventList>("/gateway/audit-events", {
      params,
    });
    return data;
  },

  async getSecurityAlerts(
    windowMinutes: number = 5,
    threshold: number = 3
  ): Promise<SecurityAlerts> {
    const { data } = await api.get<SecurityAlerts>("/gateway/security-alerts", {
      params: {
        window_minutes: windowMinutes,
        threshold,
      },
    });
    return data;
  },
};
