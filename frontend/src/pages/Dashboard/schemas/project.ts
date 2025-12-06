import { z } from 'zod';


export const createProjectSchema = z.object({
  name: z.string().min(1, "Project name is required").max(50, "Name is too long"),
  key: z.string()
    .min(2, "Key must be 2-5 chars")
    .max(5, "Key must be 2-5 chars")
    .regex(/^[A-Za-z]+$/, "Key must be letters only")
    .transform(val => val.toUpperCase()),
  category: z.string().min(1, "Please select a category"),
  description: z.string().optional(),
});


export type CreateProjectFormData = z.infer<typeof createProjectSchema>;