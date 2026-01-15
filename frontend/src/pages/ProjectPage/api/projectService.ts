import { Project, ProjectSchema } from "../types";
import { z } from "zod";
import {api} from "../../../services/api.ts";

export const getProjects = async (): Promise<Project[]> => {
  const response = await api.get("/projects");
  return z.array(ProjectSchema).parse(response.data);

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: "1", name: "Alpha App", description: "Internal dashboard", status: "ACTIVE", createdAt: new Date().toISOString(), memberCount: 5 },
        { id: "2", name: "Beta Web", description: "Customer landing page", status: "COMPLETED", createdAt: new Date().toISOString(), memberCount: 2 },
      ]);
    }, 1000);
  });
};
