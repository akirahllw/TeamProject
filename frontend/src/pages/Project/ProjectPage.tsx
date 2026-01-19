import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { DashboardLayout } from '../../layout/DashboardLayout'; 
import { ProjectHeader } from './components/ProjectHeader';
import { BoardView } from './components/BoardView';
import { ListView } from './components/ListView';
import { SummaryView } from './components/SummaryView';
import { CreateTaskModal } from './components/CreateTaskModel';
import { useProjectData } from './data/useProjectData';
import { Search, ChevronDown, Filter, X } from 'lucide-react';

const FilterDropdown = ({ 
  label, 
  value, 
  options, 
  onChange 
}: { 
  label: string, 
  value: string | null, 
  options: string[], 
  onChange: (val: string) => void 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded transition-colors ${
          value ? 'bg-blue-100 text-blue-700' : 'text-slate-700 bg-slate-100 hover:bg-slate-200'
        }`}
      >
        {label}{value ? `: ${value}` : ''} <ChevronDown size={14} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 shadow-lg rounded-md z-50 py-1 animate-in fade-in zoom-in-95 duration-100">
          {options.map((option) => (
            <button
              key={option}
              onClick={() => { onChange(option); setIsOpen(false); }}
              className={`block w-full text-left px-4 py-2 text-sm hover:bg-slate-50 ${value === option ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-700'}`}
            >
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default function ProjectPage() {
  const [currentView, setCurrentView] = useState<'summary' | 'board' | 'list'>('board');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [assigneeFilter, setAssigneeFilter] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  const { tasks, columns, createTask, updateStatus, deleteTask, addColumn } = useProjectData();
  const { projectId } = useParams(); 
  const projectName = projectId?.replace(/-/g, ' ') || 'Project';

  const filteredTasks = tasks.filter(t => {
    const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          t.key.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAssignee = assigneeFilter ? t.assignee === assigneeFilter : true;
    const matchesType = typeFilter ? t.type === typeFilter : true;

    return matchesSearch && matchesAssignee && matchesType;
  });

  const clearFilters = () => {
    setSearchQuery('');
    setAssigneeFilter(null);
    setTypeFilter(null);
  };

  const uniqueAssignees = Array.from(new Set(tasks.map(t => t.assignee)));
  const uniqueTypes = ['Task', 'Bug', 'Story', 'Epic'];

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-64px)] bg-white relative">
        <ProjectHeader 
          title={projectName} 
          activeTab={currentView} 
          onTabChange={setCurrentView} 
        />

        {currentView !== 'summary' && (
          <div className="px-6 py-4 flex items-center justify-between border-b border-transparent">
            <div className="flex items-center gap-3 w-full">
              <div className="relative w-64">
                  <Search className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                  <input 
                    type="text" 
                    placeholder="Search work" 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 border border-slate-300 rounded hover:bg-slate-50 focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm transition-all"
                  />
              </div>
              
              <FilterDropdown 
                label="Assignee" 
                value={assigneeFilter} 
                options={uniqueAssignees} 
                onChange={setAssigneeFilter} 
              />

              <FilterDropdown 
                label="Type" 
                value={typeFilter} 
                options={uniqueTypes} 
                onChange={setTypeFilter} 
              />

              <span className="text-slate-300 mx-1">|</span>
              
              {(searchQuery || assigneeFilter || typeFilter) && (
                <button 
                  onClick={clearFilters} 
                  className="text-slate-500 hover:text-slate-800 text-sm font-medium flex items-center gap-1 transition-colors"
                >
                  Clear filters <X size={14} />
                </button>
              )}
            </div>
            
            <div className="flex gap-2">
              <button className="p-2 border border-slate-300 rounded hover:bg-slate-50 text-slate-500"><Filter size={16} /></button>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-auto bg-white">
          {currentView === 'board' ? (
             <BoardView 
               tasks={filteredTasks}
               columns={columns} 
               onStatusChange={updateStatus}
               onCreate={(title, status) => createTask(title, status, 'Unassigned', 'Task')} 
               onDelete={deleteTask}
               onAddColumn={addColumn}
             />
          ) : currentView === 'list' ? (
             <ListView 
               tasks={filteredTasks}
               columns={columns}
               onStatusChange={updateStatus}
               onCreate={() => setIsCreateModalOpen(true)}
             />
          ) : (
             <SummaryView tasks={tasks} />
          )}
        </div>

        <CreateTaskModal 
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={(title, status, assignee, type, priority) => createTask(title, status, assignee, type, priority)}
          columns={columns}
        />
      </div>
    </DashboardLayout>
  );
};