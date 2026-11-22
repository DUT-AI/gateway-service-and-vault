import { z } from "zod";

/**
 * Converts Vietnamese diacritics and arbitrary text into a URL-safe kebab-case slug.
 * E.g. "Hệ Thống Thanh Toán Core" -> "he-thong-thanh-toan-core"
 */
export function generateSlug(input: string): string {
  return input
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove diacritics
    .replace(/[đĐ]/g, "d")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "") // remove invalid characters
    .replace(/[\s_]+/g, "-") // replace spaces and underscores with hyphen
    .replace(/-+/g, "-") // collapse multiple hyphens
    .replace(/^-|-$/g, "") // trim leading/trailing hyphens
    .slice(0, 100);
}

export const createProjectSchema = z.object({
  name: z
    .string()
    .min(2, "Tên dự án tối thiểu 2 ký tự")
    .max(100, "Tên dự án tối đa 100 ký tự"),
  slug: z
    .string()
    .min(2, "Mã slug tối thiểu 2 ký tự")
    .max(100, "Mã slug tối đa 100 ký tự")
    .regex(
      /^[a-z0-9-]+$/,
      "Slug chỉ được chứa chữ thường, số và dấu gạch ngang (-)"
    ),
  description: z.string().max(500, "Mô tả tối đa 500 ký tự").optional(),
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>;
