import React from 'react';
import { Link } from "react-router-dom";
import { DashboardLayout } from '../../layout/DashboardLayout';
import { ProjectCard } from './components/ProjectCard';
import { TaskRow } from './components/TaskRow';

// 1. Import your data hook
import { useProjectsList } from '../../hooks/useProjectList';

export default function DashboardPage() {
  // 2. Fetch real projects
  const { projects, loading } = useProjectsList();

  // Helper to assign random colors to projects (visual flair)
  const getIconColor = (index: number) => {
    const colors = ['bg-blue-500', 'bg-indigo-600', 'bg-purple-600', 'bg-emerald-500', 'bg-orange-500'];
    return colors[index % colors.length];
  };

  return (
    <DashboardLayout>
      <div className="flex min-h-[calc(100vh-64px)]">
        <div className="flex-1 bg-[#F3F6FD] p-8 border-r border-slate-200">
          <h1 className="text-2xl font-bold text-slate-900 mb-6">For you</h1>

          <div className="mb-8">
            <div className="flex justify-between items-end mb-4">
              <h2 className="text-base font-bold text-slate-800">Recent projects</h2>
              <Link to="/projects" className="text-sm text-blue-600 font-medium hover:underline">See all</Link>
            </div>

            <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
              {/* 3. Render Loading State or Real Data */}
              {loading ? (
                <div className="text-sm text-slate-400 p-4">Loading projects...</div>
              ) : projects.length > 0 ? (
                projects.map((project, index) => (
                  <Link key={project.id} to={`/project/${project.key}`}>
                    <ProjectCard
                      title={project.name}
                      subtitle={`${project.key} software project`}
                      myTasks={0} // You can connect this to real task counts later
                      iconColor={getIconColor(index)}
                    />
                  </Link>
                ))
              ) : (
                <div className="text-sm text-slate-500 bg-white p-4 rounded-lg border border-slate-200">
                  No projects yet. Create one!
                </div>
              )}
            </div>
          </div>

          <div className="mt-8">
            <div className="flex items-center gap-6 border-b border-slate-200 mb-6">
              {['Working on', 'Seen', 'Assigned to me', 'Marked', 'Boards'].map(
                (tab, i) => (
                  <button
                    key={tab}
                    className={`pb-2 text-sm font-medium transition-all ${
                      i === 0
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    {tab}{' '}
                    {tab === 'Assigned to me' && (
                      <span className="bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded-full text-[10px] ml-1">
                        0
                      </span>
                    )}
                  </button>
                ),
              )}
            </div>
            
            <div className="mb-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase mb-2">
                Last Month
              </h3>
              <div className="space-y-1">
                 {/* Optional: If you want these tasks to be dynamic too, 
                     you'll need a similar 'useRecentTasks' hook. 
                     For now, they are static placeholders.
                 */}
                <TaskRow
                  title="Build Vendor Creation/Edit Form"
                  id="ECS-19"
                  project="AYIST_ERP"
                />
                <TaskRow
                  title="Discovery - Vendors Module Flow"
                  id="ECS-18"
                  project="AYIST_ERP"
                />
              </div>
            </div>
          </div>
        </div>
        <div className="hidden xl:block w-[350px] bg-[#DDE9FC]"></div>
      </div>
    </DashboardLayout>
  )
}