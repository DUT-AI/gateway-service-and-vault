import { z } from "zod";

export const secretKeyRegex = /^[A-Z0-9_]+$/;

export const createSecretSchema = z.object({
  scope_name: z
    .string()
    .min(1, "Vui lòng chọn hoặc nhập tên nhóm Scope")
    .max(50, "Tên scope tối đa 50 ký tự")
    .regex(/^[a-zA-Z0-9_\s-]+$/, "Tên scope không được chứa ký tự đặc biệt"),
  key: z
    .string()
    .min(2, "Tên key tối thiểu 2 ký tự")
    .max(100, "Tên key tối đa 100 ký tự")
    .regex(
      secretKeyRegex,
      "Tên key phải viết hoa (ví dụ: DATABASE_URL, STRIPE_KEY)"
    ),
  value: z.string().min(1, "Vui lòng nhập giá trị biến môi trường"),
});

export type CreateSecretInput = z.infer<typeof createSecretSchema>;
