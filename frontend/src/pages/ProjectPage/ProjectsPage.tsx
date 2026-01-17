import { useEffect, useState } from "react";
import { Project } from "./types";
import { getProjects } from "./api/projectService";
import { ProjectCard } from "./components/ProjectCard";

export const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getProjects()
      .then((data) => setProjects(data))
      .catch((err) => console.error(err)) // Ideally use a toast notification here
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 text-sm mt-1">Manage your team workspaces</p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">
          + New Project
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      )}

      {/* Project Grid */}
      {!isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && projects.length === 0 && (
         <div className="text-center py-20 text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <p>No projects found. Create one to get started.</p>
         </div>
      )}
    </div>
  );
};
export default ProjectsPage;
