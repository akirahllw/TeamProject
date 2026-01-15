import { Project } from "../types";

type ProjectCardProps = {
  project: Project;
};

export const ProjectCard = ({ project }: ProjectCardProps) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg text-gray-800">{project.name}</h3>
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
          project.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
        }`}>
          {project.status}
        </span>
      </div>

      <p className="text-gray-500 text-sm mb-4 line-clamp-2 h-10">
        {project.description || "No description provided."}
      </p>

      <div className="flex items-center justify-between text-xs text-gray-400 border-t pt-3">
        <span>Created: {new Date(project.createdAt).toLocaleDateString()}</span>
        {project.memberCount && (
          <span className="flex items-center">
             👥 {project.memberCount} members
          </span>
        )}
      </div>
    </div>
  );
};
