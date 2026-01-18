import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from './Topbar';
import { CreateProjectModal } from '../pages/ProjectPage/components/CreateProjectModal';
import { CreateProjectFormData } from '../pages/Dashboard/schemas/project';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateProject = async (data: CreateProjectFormData) => {
    console.log("SENDING TO BACKEND:", data);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900">
      <Sidebar onCreateProject={() => setIsModalOpen(true)} />

      <Topbar />

      <main className="ml-64 pt-16 min-h-screen transition-all duration-200">
        {children}
      </main>
      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </div>
  );
};
