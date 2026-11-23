import { z } from "zod";

export const registerClientSchema = z.object({
  name: z
    .string()
    .min(2, "Tên thiết bị phải có ít nhất 2 ký tự")
    .max(64, "Tên thiết bị không vượt quá 64 ký tự")
    .regex(
      /^[a-zA-Z0-9\s._-]+$/,
      "Tên thiết bị chỉ chứa chữ cái, số, dấu cách, gạch nối và dấu gạch dưới"
    ),
  client_type: z.enum(["USER_DEVICE", "APP_SERVER"], {
    message: "Vui lòng chọn loại client hợp lệ",
  }),
  validity_days: z.number().refine((val) => [30, 90, 365].includes(val), {
    message: "Thời hạn hợp lệ phải là 30, 90 hoặc 365 ngày",
  }),
});

export type RegisterClientFormData = z.infer<typeof registerClientSchema>;
