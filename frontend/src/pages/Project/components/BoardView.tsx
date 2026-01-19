import React from 'react';
import { Plus, MoreHorizontal, X } from 'lucide-react';
import { Task, TaskStatus } from '../data/useProjectData';

interface BoardViewProps {
  tasks: Task[];
  columns: TaskStatus[];
  onStatusChange: (id: string, status: TaskStatus) => void;
  onCreate: (title: string, status: TaskStatus) => void;
  onDelete: (id: string) => void;
  onAddColumn: (name: string) => void;
}

export const BoardView: React.FC<BoardViewProps> = ({ 
  tasks, columns, onStatusChange, onCreate, onDelete, onAddColumn 
}) => {
  
  const handleCreateInColumn = (status: TaskStatus) => {
    const title = window.prompt(`New task for ${status}:`);
    if (title) onCreate(title, status);
  };

  const handleAddColumn = () => {
    const name = window.prompt("Column Name:");
    if (name) onAddColumn(name);
  };

  return (
    <div className="p-6 flex gap-4 overflow-x-auto min-h-[calc(100vh-200px)] items-start">
      {columns.map((col) => {
        const colTasks = tasks.filter((t) => t.status === col);
        
        return (
          <div key={col} className="w-72 flex-shrink-0 bg-slate-50 rounded-lg p-3 min-h-[150px] group/col">
            <div className="flex justify-between items-center mb-4 px-1">
              <h3 className="text-xs font-bold text-slate-500 uppercase">
                {col} <span className="ml-1 bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded-full text-[10px]">{colTasks.length}</span>
              </h3>
              <div className="flex gap-1 opacity-0 group-hover/col:opacity-100 transition-opacity">
                 <button onClick={() => handleCreateInColumn(col)} className="hover:bg-slate-200 p-1 rounded"><Plus size={14} /></button>
              </div>
            </div>

            <div className="space-y-2">
              {colTasks.map((task) => (
                <div key={task.id} className="bg-white p-3 rounded shadow-sm border border-slate-200 hover:shadow-md transition-shadow group relative">
                  
                  <button 
                    onClick={(e) => { e.stopPropagation(); onDelete(task.id); }}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded"
                  >
                    <X size={14} />
                  </button>

                  <p className="text-sm text-slate-800 font-medium mb-3 pr-4">{task.title}</p>
                  
                  <div className="flex justify-between items-end">
                    <div className="flex gap-2 items-center">
                       <button 
                         onClick={() => {
                           const next = columns[(columns.indexOf(col) + 1) % columns.length];
                           onStatusChange(task.id, next);
                         }}
                         className={`w-4 h-4 border-2 rounded-sm flex items-center justify-center ${col === 'DONE' ? 'bg-blue-600 border-blue-600' : 'border-slate-300 hover:border-blue-500'}`}
                         title="Move to next status"
                       >
                          {col === 'DONE' && <div className="w-2 h-2 bg-white rounded-[1px]" />}
                       </button>
                       <span className="text-xs text-slate-500 font-medium hover:underline cursor-pointer">{task.key}</span>
                    </div>

                    {task.priority !== 'None' && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                         {task.priority}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <button onClick={() => handleCreateInColumn(col)} className="w-full mt-3 py-2 flex items-center gap-2 text-slate-600 hover:bg-slate-200 rounded px-2 transition-colors">
               <Plus size={16} /> <span className="text-sm">Create</span>
            </button>
          </div>
        );
      })}
       
      <button onClick={handleAddColumn} className="w-72 flex-shrink-0 h-12 border-2 border-dashed border-slate-300 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:border-slate-400 font-medium text-sm transition-colors">
         <Plus size={16} className="mr-2" /> Add column
      </button>
    </div>
  );
};