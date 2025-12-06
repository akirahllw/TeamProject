import React from 'react';

interface TaskRowProps {
  id: string;
  project: string;
  title: string;
  isChecked?: boolean;
}

export const TaskRow: React.FC<TaskRowProps> = ({ id, project, title, isChecked }) => {
  return (
    <div className="flex items-center gap-4 py-3 border-b border-slate-100 hover:bg-slate-50 px-2 -mx-2 transition-colors group cursor-pointer">
      <input type="checkbox" defaultChecked={isChecked} className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-4 w-4 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-slate-800 font-medium group-hover:text-blue-600">{title}</p>
        <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
           <span className="uppercase">{id}</span>
           <span>•</span>
           <span className="uppercase">{project}</span>
        </div>
      </div>
      
      <div className="text-xs text-slate-500 font-medium">
        Updated
      </div>
    </div>
  );
};