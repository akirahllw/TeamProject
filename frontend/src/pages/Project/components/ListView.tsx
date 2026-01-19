import React, { useState, useEffect, useRef } from 'react';
import { Task, TaskStatus } from '../data/useProjectData';
import { User, ArrowUpDown, ChevronDown, Square } from 'lucide-react';

interface ListViewProps {
  tasks: Task[];
  columns: TaskStatus[];
  onStatusChange: (id: string, status: TaskStatus) => void;
  onCreate: () => void;
}

export const ListView: React.FC<ListViewProps> = ({ tasks, columns, onStatusChange, onCreate }) => {
  const [sortField, setSortField] = useState<keyof Task>('created');
  const [openDropdownId, setOpenDropdownId] = useState<string | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if ((event.target as HTMLElement).closest('.status-dropdown-container')) return;
      setOpenDropdownId(null);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sortedTasks = [...tasks].sort((a, b) => {
    return (a[sortField] || '') > (b[sortField] || '') ? 1 : -1;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'TO DO': return 'bg-slate-200 text-slate-700 hover:bg-slate-300';
      case 'IN PROGRESS': return 'bg-blue-100 text-blue-700 hover:bg-blue-200';
      case 'IN REVIEW': return 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200';
      case 'DONE': return 'bg-green-100 text-green-700 hover:bg-green-200';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="p-6">
      <div className="border rounded-lg border-slate-200 overflow-visible bg-white shadow-sm min-h-[400px]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-xs text-slate-500 font-semibold border-b border-slate-200">
              <th className="p-3 w-8"><Square size={16} className="text-slate-300" /></th>
              <th className="p-3 cursor-pointer hover:bg-slate-100 group" onClick={() => setSortField('key')}>
                <div className="flex items-center gap-1">Key <ArrowUpDown size={12} className="opacity-0 group-hover:opacity-100"/></div>
              </th>
              <th className="p-3 w-1/3 cursor-pointer hover:bg-slate-100 group" onClick={() => setSortField('title')}>
                 <div className="flex items-center gap-1">Summary <ArrowUpDown size={12} className="opacity-0 group-hover:opacity-100"/></div>
              </th>
              <th className="p-3">Assignee</th>
              <th className="p-3 cursor-pointer hover:bg-slate-100" onClick={() => setSortField('status')}>Status</th>
              <th className="p-3 text-right">Created</th>
            </tr>
          </thead>
          <tbody className="relative"> 
            {sortedTasks.map((task) => (
              <tr key={task.id} className="border-b border-slate-100 hover:bg-slate-50 text-sm group transition-colors">
                <td className="p-3"><Square size={16} className="text-slate-300 hover:text-blue-500 cursor-pointer" /></td>
                <td className="p-3 text-slate-500 font-medium">{task.key}</td>
                <td className="p-3 font-medium text-slate-700 hover:text-blue-600 cursor-pointer">{task.title}</td>
                <td className="p-3">
                  <div className="flex items-center gap-2 text-slate-500">
                    <div className="w-6 h-6 bg-slate-200 rounded-full flex items-center justify-center"><User size={12}/></div>
                    {task.assignee || 'Unassigned'}
                  </div>
                </td>
                
                <td className="p-3 relative status-dropdown-container"> 
                   
                   {/* 1. The Trigger Button */}
                   <button 
                     onClick={() => setOpenDropdownId(openDropdownId === task.id ? null : task.id)}
                     className={`
                       flex items-center gap-2 px-3 py-1.5 rounded text-[11px] font-bold uppercase tracking-wide transition-all whitespace-nowrap
                       ${getStatusColor(task.status)}
                     `}
                   >
                     {task.status} <ChevronDown size={12} strokeWidth={3} />
                   </button>

                   {openDropdownId === task.id && (
                     <div className="absolute top-[calc(100%+4px)] left-0 w-48 bg-white rounded-md shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-75 origin-top-left">
                       
                       <div className="px-4 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                         Transitions
                       </div>
                       
                       <div className="flex flex-col gap-1 px-2">
                         {columns.map((statusOption) => (
                           <button
                             key={statusOption}
                             onClick={() => {
                               onStatusChange(task.id, statusOption);
                               setOpenDropdownId(null);
                             }}
                             className={`
                               w-full text-left px-2 py-1.5 rounded flex items-center transition-colors
                               ${task.status === statusOption ? 'bg-blue-50 border border-blue-100 cursor-default' : 'hover:bg-slate-100'}
                             `}
                           >
                             <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${getStatusColor(statusOption)}`}>
                               {statusOption}
                             </span>
                           </button>
                         ))}
                       </div>
                       
                       <div className="h-px bg-slate-100 my-2 mx-2"></div>
                       <button className="w-full text-left px-4 py-1 text-xs text-slate-600 hover:bg-slate-50 transition-colors">
                         View workflow
                       </button>
                     </div>
                   )}
                </td>

                <td className="p-3 text-right text-slate-400 text-xs">{task.created}</td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div 
          onClick={onCreate}
          className="p-3 border-t border-slate-200 bg-slate-50 text-center hover:bg-slate-100 cursor-pointer text-sm font-medium text-slate-600 transition-colors"
        >
           + Create
        </div>
      </div>
    </div>
  );
};