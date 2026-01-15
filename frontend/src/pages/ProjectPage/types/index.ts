import { z } from "zod";

export const ProjectSchema = z.object({
  id: z.string(),
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  status: z.enum(["ACTIVE", "COMPLETED", "ARCHIVED"]),
  createdAt: z.string(),
  memberCount: z.number().optional(),
});

export type Project = z.infer<typeof ProjectSchema>;
