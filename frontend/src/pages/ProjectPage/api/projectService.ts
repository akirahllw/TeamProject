import { Project, ProjectSchema } from "../types";
import { z } from "zod";
import { api } from "../../../services/api";

export const getProjects = async (): Promise<Project[]> => {
  const response = await api.get("/projects");
  return z.array(ProjectSchema).parse(response.data);
};

export const createProject = async (data: { name: string; description?: string }) => {
  const response = await api.post("/projects", data);
  return ProjectSchema.parse(response.data);
};
