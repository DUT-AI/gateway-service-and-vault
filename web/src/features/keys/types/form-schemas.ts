import { z } from "zod";

export const generateKeySchema = z.object({
  client_id: z.string().min(1, "Vui lòng chọn thiết bị Client được cấp phép"),
  project_id: z.string().min(1, "Thiếu thông tin dự án"),
});

export type GenerateKeyFormData = z.infer<typeof generateKeySchema>;
