import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  User, Clock, Star, Grid, Layout, BookOpen, Menu, Filter, 
  LayoutDashboard, Users, Settings, Flag, Plus, ChevronRight 
} from 'lucide-react';

// IMPORT YOUR NEW HOOK HERE
import { useProjectsList } from '../hooks/useProjectList'; 

interface SidebarProps {
  onCreateProject?: () => void;
}

const NavItem = ({ icon: Icon, label, active, hasSubmenu, onClick }: any) => (
  <div 
    onClick={onClick} 
    className={`
      flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors group 
      ${active ? 'bg-blue-100 text-blue-700' : 'text-slate-700 hover:bg-slate-100'}
    `}
  >
    <div className="flex items-center gap-3">
      <Icon size={20} className={active ? 'text-blue-700' : 'text-slate-600'} />
      <span className={`text-sm font-medium ${active ? 'text-blue-900' : 'text-slate-700'}`}>
        {label}
      </span>
    </div>
    {hasSubmenu && <ChevronRight size={16} className="text-slate-400 group-hover:text-slate-600" />}
  </div>
);

export const Sidebar: React.FC<SidebarProps> = ({ onCreateProject }) => {
  const location = useLocation();

  // 1. Fetch the real projects from the database
  const { projects, loading } = useProjectsList();

  // Helper to check if a route is active
  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <aside className="w-64 bg-white border-r border-slate-200 h-screen fixed left-0 top-0 flex flex-col z-20 overflow-y-auto pb-4">
      {/* Sidebar Header / Logo Area */}
      <div className="h-16 flex items-center px-5 mb-2">
         <div className="p-2 -ml-2 hover:bg-slate-100 rounded-md cursor-pointer transition-colors">
            <Menu className="text-slate-600" size={24} />
         </div>
      </div>

      <div className="px-3 space-y-6">
        
        {/* Main Navigation */}
        <div className="space-y-1">
          <Link to="/dashboard">
             <NavItem icon={User} label="For you" active={isActive('/dashboard')} hasSubmenu />
          </Link>
          <NavItem icon={Clock} label="Recent" hasSubmenu />
          <NavItem icon={Star} label="Marked" />
        </div>

        <div className="space-y-1">
          <NavItem icon={Grid} label="Apps" />
        </div>

        {/* --- DYNAMIC PROJECTS SECTION --- */}
        <div className="space-y-1">
          <div className="flex items-center justify-between px-3 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider group cursor-pointer hover:bg-slate-50 rounded">
            <span>Sections</span>
            <div 
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onCreateProject?.();
              }}
              className="p-1 hover:bg-slate-200 rounded transition-colors text-slate-500 hover:text-blue-600"
            >
               <Plus size={16} />
            </div>
          </div>
          
          {/* 2. Render List or Loading State */}
          {loading ? (
             <div className="px-3 py-2 text-xs text-slate-400 animate-pulse">Loading projects...</div>
          ) : (
             projects.map((project) => (
               <Link key={project.id} to={`/project/${project.key}`}>
                 <NavItem 
                   icon={Layout} 
                   label={project.name} 
                   active={isActive(`/project/${project.key}`)} 
                 />
               </Link>
             ))
          )}

          {/* Static "Learn" Section */}
          <Link to="/project/Learn">
             <NavItem icon={BookOpen} label="Learn" active={isActive('/project/Learn')} />
          </Link>
        </div>

        {/* Footer Navigation */}
        <div className="space-y-1">
           <NavItem icon={Menu} label="Other sections" hasSubmenu />
        </div>
        <hr className="border-slate-100 mx-2" />
        <div className="space-y-1">
          <NavItem icon={Filter} label="Filters" />
          <NavItem icon={LayoutDashboard} label="Dashboards" />
          <NavItem icon={Users} label="Teams" />
          <NavItem icon={Settings} label="Setting" />
        </div>
      </div>

      <div className="mt-auto px-4 py-6">
        <div className="flex items-center gap-3 text-slate-600 cursor-pointer hover:text-slate-900 group">
            <Flag size={20} className="group-hover:text-blue-600 transition-colors" />
            <span className="text-sm font-medium">Leave a review</span>
        </div>
      </div>
    </aside>
  );
};