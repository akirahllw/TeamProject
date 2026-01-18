import React from 'react';
import { DashboardLayout } from '../../layout/DashboardLayout';
import { ProjectCard } from './components/ProjectCard';
import { TaskRow } from './components/TaskRow';
import { Link } from "react-router-dom";
export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="flex min-h-[calc(100vh-64px)]">
        <div className="flex-1 bg-[#F3F6FD] p-8 border-r border-slate-200">
          <h1 className="text-2xl font-bold text-slate-900 mb-6">For you</h1>

          <div className="mb-8">
            <div className="flex justify-between items-end mb-4">
              <h2 className="text-base font-bold text-slate-800">Recent sections</h2>
              <Link to="/projects" className="text-sm text-blue-600 font-medium hover:underline">See all</Link>
            </div>

            <div className="flex gap-6 overflow-x-auto pb-2">
              <ProjectCard
                title="AYIST_ERP"
                subtitle="Software, ..."
                myTasks={0}
                iconColor="bg-blue-500"
              />
              <ProjectCard
                title="(Learn) Jira Premium be..."
                subtitle="Software, ..."
                myTasks={0}
                iconColor="bg-indigo-600"
              />
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
                <TaskRow
                  title="Build Vendor Creation/Edit Form"
                  id="ECS-19"
                  project="AYIST_ERP"
                />
                <TaskRow
                  title="Discovery - Vendors Module Flow and Architecture Planning_FE"
                  id="ECS-18"
                  project="AYIST_ERP"
                />
                <TaskRow
                  title="CRM Customer Profile Page (Overview and Contacts)"
                  id="ECS-17"
                  project="AYIST_ERP"
                />
                <TaskRow
                  title="Build CRM Creation Form"
                  id="ECS-15"
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
