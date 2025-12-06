import React from 'react';
import { ChevronDown } from 'lucide-react';

interface ProjectCardProps {
  title: string;
  subtitle: string;
  myTasks: number;
  iconColor: string;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ title, subtitle, myTasks, iconColor }) => {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border border-slate-200 min-w-[280px] hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex gap-3 mb-4">
        <div className={`w-10 h-10 rounded-md flex items-center justify-center ${iconColor}`}>
           <div className="w-5 h-5 bg-white/50 rounded-sm"></div>
        </div>
        <div>
          <h3 className="font-bold text-slate-900 text-sm">{title}</h3>
          <p className="text-xs text-slate-500">{subtitle}</p>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex justify-between items-center text-xs font-medium text-slate-700">
          <span>My tasks</span>
          <span className="bg-slate-100 px-2 py-0.5 rounded-full">{myTasks}</span>
        </div>
        <div className="flex justify-between items-center text-xs text-slate-400">
          <span>Finished Tasks</span>
        </div>
        <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
           <div className="h-full bg-slate-300 w-0"></div>
        </div>
      </div>

      <div className="border-t border-slate-100 pt-3 flex items-center justify-between text-xs text-slate-500">
         <span>1 board</span>
         <ChevronDown size={14} />
      </div>
    </div>
  );
};