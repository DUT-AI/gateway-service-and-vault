import { z } from "zod";
export { generateSlug } from "@/features/projects";

export const createServiceSchema = z.object({
  name: z
    .string()
    .min(2, "Tên dịch vụ phải có ít nhất 2 ký tự")
    .max(100, "Tên dịch vụ không vượt quá 100 ký tự"),
  slug: z
    .string()
    .min(2, "Slug phải có ít nhất 2 ký tự")
    .max(100, "Slug không vượt quá 100 ký tự")
    .regex(
      /^[a-z0-9-]+$/,
      "Slug chỉ được chứa chữ thường, số và dấu gạch ngang (-)"
    ),
  base_url: z
    .string()
    .min(1, "Vui lòng nhập Base URL")
    .regex(/^https?:\/\/.+/, "Base URL phải bắt đầu bằng http:// hoặc https://")
    .refine((url) => {
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    }, "Base URL không đúng định dạng URL hợp lệ")
    .transform((url) => url.replace(/\/+$/, "")),
  auth_type: z.enum(["BEARER_TOKEN", "API_KEY", "BASIC_AUTH", "NO_AUTH"], {
    message: "Vui lòng chọn phương thức xác thực hợp lệ",
  }),
  credential: z.string(),
  timeout_seconds: z
    .number()
    .int("Timeout phải là số nguyên")
    .min(1, "Timeout tối thiểu 1 giây")
    .max(300, "Timeout tối đa 300 giây"),
}).superRefine((data, ctx) => {
  if (data.auth_type !== "NO_AUTH" && data.credential.trim().length === 0) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Vui lòng nhập Token hoặc Credential đối tác",
      path: ["credential"],
    });
  }
});

export type CreateServiceFormData = z.infer<typeof createServiceSchema>;
