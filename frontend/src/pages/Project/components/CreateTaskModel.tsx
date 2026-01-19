import React, { useState } from 'react';
import { X, ChevronDown, Flag } from 'lucide-react';
import { TaskStatus } from '../data/useProjectData';

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (title: string, status: TaskStatus, assignee: string, type: 'Task' | 'Bug' | 'Story', priority: 'High' | 'Medium' | 'Low' | 'None') => void;
  columns: TaskStatus[];
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({ isOpen, onClose, onSubmit, columns }) => {
  const [summary, setSummary] = useState('');
  const [status, setStatus] = useState<TaskStatus>('TO DO');
  const [assignee, setAssignee] = useState('');
  const [type, setType] = useState<'Task' | 'Bug' | 'Story'>('Task');
  const [priority, setPriority] = useState<'High' | 'Medium' | 'Low' | 'None'>('None');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!summary.trim()) return;
    
    onSubmit(summary, status, assignee, type, priority);
    
    setSummary('');
    setStatus('TO DO');
    setAssignee('');
    setPriority('None');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px]" onClick={onClose}></div>

      <div className="relative w-full max-w-lg bg-white rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-white">
          <h2 className="text-lg font-semibold text-slate-800">Create Issue</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-slate-700">Summary <span className="text-red-500">*</span></label>
            <input 
              type="text" 
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="What needs to be done?"
              autoFocus
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none text-sm transition-shadow"
            />
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Type</label>
              <div className="relative">
                <select value={type} onChange={(e) => setType(e.target.value as any)} className="w-full appearance-none px-3 py-2 bg-slate-50 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none text-sm text-slate-700 cursor-pointer">
                  <option value="Task">Task</option>
                  <option value="Bug">Bug</option>
                  <option value="Story">Story</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
              </div>
            </div>
            
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Status</label>
              <div className="relative">
                <select value={status} onChange={(e) => setStatus(e.target.value as TaskStatus)} className="w-full appearance-none px-3 py-2 bg-slate-50 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none text-sm text-slate-700 cursor-pointer">
                  {columns.map(col => <option key={col} value={col}>{col}</option>)}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-5">
             <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Assignee</label>
              <div className="relative">
                <select value={assignee} onChange={(e) => setAssignee(e.target.value)} className="w-full appearance-none px-3 py-2 bg-slate-50 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none text-sm text-slate-700 cursor-pointer">
                  <option value="">Unassigned</option>
                  <option value="Artem Ratushnyi">Artem Ratushnyi</option>
                  <option value="Sarah Connor">Sarah Connor</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-slate-700">Priority</label>
              <div className="relative">
                <select value={priority} onChange={(e) => setPriority(e.target.value as any)} className="w-full appearance-none px-3 py-2 bg-slate-50 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 outline-none text-sm text-slate-700 cursor-pointer">
                  <option value="High">High 🔴</option>
                  <option value="Medium">Medium 🟠</option>
                  <option value="Low">Low 🔵</option>
                  <option value="None">None ⚪</option>
                </select>
                <Flag className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" size={16} />
              </div>
            </div>
          </div>

        </form>

        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 rounded-md transition-colors">Cancel</button>
          <button onClick={handleSubmit} disabled={!summary.trim()} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50">Create</button>
        </div>
      </div>
    </div>
  );
};