import type { components } from "@/types/api.generated";

export type AuditEvent = components["schemas"]["AuditEventResponse"];
export type AuditEventList = components["schemas"]["AuditEventListResponse"];
export type SecurityAlert = components["schemas"]["SecurityAlertItemResponse"];
export type SecurityAlerts = components["schemas"]["SecurityAlertsResponse"];

export interface AuditFilterParams {
  project_id?: string;
  client_type?: string;
  decision?: string;
  action?: string;
  error_code?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}
