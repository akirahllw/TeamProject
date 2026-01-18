import { useEffect, useState } from "react";
import { Plus } from "lucide-react";

import { DashboardLayout } from "../../layout/DashboardLayout";
import { Project } from "./types";
import { getProjects, createProject } from "./api/projectService";
import { ProjectCard } from "./components/ProjectCard";

// FIX 1: Import the EXISTING modal from the Dashboard feature
// (We go up to 'features', then down into 'dashboard')
import { CreateProjectModal } from "./components/CreateProjectModal.tsx";

export const ProjectsPage = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Note: We don't strictly need 'isCreating' for the UI anymore
  // because your existing modal doesn't have a loading spinner prop.

  // Fetch Projects
  const fetchProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (error) {
      console.error("Failed to fetch projects", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Handle Create
  const handleCreate = async (data: { name: string; description?: string }) => {
    try {
      await createProject(data);
      await fetchProjects(); // Refresh the list
      setIsModalOpen(false); // Close the modal
    } catch (error) {
      console.error("Failed to create project", error);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-8 min-h-[calc(100vh-64px)] bg-[#F3F6FD]">

        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
            <p className="text-slate-500 text-sm mt-1">Manage and track your team's work</p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors shadow-sm"
          >
            <Plus size={20} /> New Project
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
        {!isLoading && projects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && projects.length === 0 && (
           <div className="text-center py-20 text-slate-500 bg-white rounded-lg border border-dashed border-slate-300">
              <p>No projects found. Use the button above to create one.</p>
           </div>
        )}

        {/* FIX 2: Removed 'isSubmitting' prop because your existing modal doesn't support it */}
        {isModalOpen && (
          <CreateProjectModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onSubmit={handleCreate}
          />
        )}

      </div>
    </DashboardLayout>
  );
};

export default ProjectsPage;
