import React, { useState } from 'react';
import { Search, Bell, HelpCircle, Settings } from 'lucide-react';
import { Button } from '../components/Button';
import { UserAvatar } from '../components/UserAvatar';
import { NotificationPopover } from './components/NotificationPopover';
import { useNotifications } from '../hooks/use-notification';

export const Topbar = () => {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const { unreadCount } = useNotifications();

  return (
    <header className="h-16 bg-white border-b border-slate-200 fixed top-0 right-0 left-64 z-30 flex items-center justify-between px-6">
      
      <div className="flex items-center gap-3 w-full max-w-xl">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Search" 
            className="w-full bg-slate-100 border-none rounded-md py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
          />
        </div>
        
        <div className="w-24">
             <Button variant="primary" size="sm" icon={<span className="text-lg leading-none">+</span>}>
                Create
             </Button>
        </div>
      </div>

      <div className="flex items-center gap-5 relative">
        <button 
          onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
          className={`relative p-2 rounded-full transition-colors duration-200 
            ${isNotificationsOpen ? 'bg-blue-50 text-blue-600' : 'text-slate-600 hover:text-blue-600 hover:bg-slate-50'}
          `}
          aria-label="Notifications"
        >
           <Bell size={20} />
           {unreadCount > 0 && (
             <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full animate-in zoom-in duration-300"></span>
           )}
        </button>
        <button className="text-slate-600 hover:text-blue-600 transition-colors p-1 rounded-full hover:bg-slate-50">
          <HelpCircle size={20} />
        </button>
        <button className="text-slate-600 hover:text-blue-600 transition-colors p-1 rounded-full hover:bg-slate-50">
          <Settings size={20} />
        </button>
        <UserAvatar name="Test User" className="w-8 h-8 text-xs bg-blue-600 text-white cursor-pointer hover:ring-2 hover:ring-offset-1 hover:ring-blue-500 transition-all" />
        <NotificationPopover 
          isOpen={isNotificationsOpen} 
          onClose={() => setIsNotificationsOpen(false)} 
        />
      </div>

    </header>
  );
};