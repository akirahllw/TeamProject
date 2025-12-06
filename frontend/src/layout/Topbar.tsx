import React from 'react';
import { Search, Bell, HelpCircle, Settings } from 'lucide-react';
import { Button } from '../components/Button';
import { UserAvatar } from '../components/UserAvatar';

export const Topbar = () => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 fixed top-0 right-0 left-64 z-10 flex items-center justify-between px-6">
      <div className="flex items-center gap-3 w-full max-w-xl">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Search" 
            className="w-full bg-slate-100 border-none rounded-md py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div className="w-24">
             <Button variant="primary" size="sm" icon={<span className="text-lg leading-none">+</span>}>
                Create
             </Button>
        </div>
      </div>
      <div className="flex items-center gap-5">
        <Bell className="text-slate-600 cursor-pointer hover:text-blue-600" size={20} />
        <HelpCircle className="text-slate-600 cursor-pointer hover:text-blue-600" size={20} />
        <Settings className="text-slate-600 cursor-pointer hover:text-blue-600" size={20} />
        <UserAvatar name="Test User" className="w-8 h-8 text-xs bg-blue-600 text-white" />
      </div>
    </header>
  );
};