import React from 'react';
import { Share2, Zap, Maximize2, Star, MoreHorizontal } from 'lucide-react';

interface ProjectHeaderProps {
  title: string;
  activeTab: 'summary' | 'list' | 'board'; 
  onTabChange: (tab: 'summary' | 'list' | 'board') => void;
}

export const ProjectHeader: React.FC<ProjectHeaderProps> = ({ title, activeTab, onTabChange }) => {
  
  const initials = title
    .split(' ')
    .map(n => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  return (
    <div className="bg-white border-b border-slate-200 px-6 pt-6 pb-0">
      <div className="flex items-start justify-between mb-4">
        <div>
           <div className="text-xs text-slate-500 font-medium mb-1">Spaces</div>
           <div className="flex items-center gap-3">
             <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center text-white font-bold rounded-md">
                {initials}
             </div>
             <h1 className="text-xl font-semibold text-slate-800">{title}</h1>
             
             <button className="text-slate-400 hover:text-yellow-400 ml-2"><Star size={18} /></button>
             <button className="text-slate-400 hover:text-slate-600 ml-1"><MoreHorizontal size={18} /></button>
           </div>
        </div>
        
        <div className="flex gap-2">
           <button className="p-2 hover:bg-slate-100 rounded text-slate-600"><Share2 size={18} /></button>
           <button className="p-2 hover:bg-slate-100 rounded text-slate-600"><Zap size={18} /></button>
           <button className="p-2 hover:bg-slate-100 rounded text-slate-600"><Maximize2 size={18} /></button>
        </div>
      </div>

      <div className="flex gap-6 mt-6">
        {['Summary', 'List', 'Board'].map((tab) => {
          const tabKey = tab.toLowerCase();
          const isActive = activeTab === tabKey;
          
          return (
            <button
              key={tab}
              onClick={() => {
                 if (['summary', 'list', 'board'].includes(tabKey)) {
                   onTabChange(tabKey as 'summary' | 'list' | 'board');
                 }
              }}
              className={`
                pb-3 text-sm font-medium border-b-2 transition-colors
                ${isActive ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-600 hover:bg-slate-50 hover:text-slate-800'}
                ${!['summary', 'list', 'board'].includes(tabKey) ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {tab}
            </button>
          );
        })}
      </div>
    </div>
  );
};