import React, { useState, useEffect, useMemo } from 'react';
import { ExternalLink, MoreVertical, CheckCheck } from 'lucide-react';
import { useNotifications } from '../../hooks/use-notification';
import { NotificationItem } from './NotificationItem';
import { ShortcutsMenu } from './ShortcutsMenu';

interface NotificationPopoverProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationPopover: React.FC<NotificationPopoverProps> = ({ isOpen, onClose }) => {
  const { notifications, isLoading, markAsRead, toggleReadStatus, markAllRead } = useNotifications();
  
  const [activeTab, setActiveTab] = useState<'Direct' | 'Watching'>('Direct');
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [keyboardIndex, setKeyboardIndex] = useState(-1);
  const [showShortcuts, setShowShortcuts] = useState(false);

  const filteredNotifications = useMemo(() => {
    return notifications.filter(n => {
      const matchesTab = n.type === activeTab;
      const matchesUnread = showUnreadOnly ? !n.isRead : true;
      return matchesTab && matchesUnread;
    });
  }, [notifications, activeTab, showUnreadOnly]);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (e.shiftKey) {
          setKeyboardIndex(filteredNotifications.length - 1);
        } else {
          setKeyboardIndex(prev => (prev < filteredNotifications.length - 1 ? prev + 1 : prev));
        }
      }

      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (e.shiftKey) {
           setKeyboardIndex(0);
        } else {
           setKeyboardIndex(prev => (prev > 0 ? prev - 1 : 0));
        }
      }

      if (keyboardIndex >= 0 && keyboardIndex < filteredNotifications.length) {
        const item = filteredNotifications[keyboardIndex];

        if (e.key === 'Enter') {
          markAsRead(item.id);
          console.log("Navigating to:", item.description);
        }

        if (e.key === 'r' || e.key === 'R') {
          toggleReadStatus(item.id);
        }

        if (e.key === 'e' || e.key === 'E') {
           console.log("Expand details for:", item.title);
           markAsRead(item.id);
        }
      }

      if (e.key === 'Escape') {
        if (showShortcuts) setShowShortcuts(false);
        else onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredNotifications, keyboardIndex, markAsRead, toggleReadStatus, showShortcuts, onClose]);

  useEffect(() => {
    setKeyboardIndex(-1);
  }, [activeTab, showUnreadOnly]);

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      
      <div className="absolute top-14 right-0 mt-2 w-[420px] bg-white rounded-lg shadow-2xl border border-slate-200 z-50 flex flex-col origin-top-right animate-in fade-in zoom-in-95 duration-200 overflow-hidden">
        
        <div className="px-5 py-4 flex items-center justify-between bg-white z-10">
          <h2 className="text-xl font-bold text-slate-900">Notifications</h2>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-slate-600">Only show unread</span>
            <button 
              onClick={() => setShowUnreadOnly(!showUnreadOnly)}
              className={`relative w-9 h-5 rounded-full transition-colors duration-200 ${showUnreadOnly ? 'bg-blue-600' : 'bg-slate-300'}`}
            >
              <span className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transform transition-transform duration-200 ${showUnreadOnly ? 'translate-x-4' : 'translate-x-0'}`} />
            </button>
            <div className="h-5 w-[1px] bg-slate-200 mx-1"></div>
            <button onClick={markAllRead} className="text-slate-500 hover:text-blue-600">
               <CheckCheck size={18} />
            </button>
            <button className="text-slate-500 hover:text-slate-700">
               <MoreVertical size={18} />
            </button>
          </div>
        </div>

        <div className="px-5 flex gap-6 border-b border-slate-200 bg-white">
          {['Direct', 'Watching'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto max-h-[500px] min-h-[300px] bg-white relative">
          
          {showShortcuts && <ShortcutsMenu />}

          {isLoading ? (
            <div className="flex items-center justify-center h-40 text-slate-400">Loading...</div>
          ) : filteredNotifications.length > 0 ? (
            <div>
              {filteredNotifications.map((notif, idx) => (
                <NotificationItem 
                  key={notif.id} 
                  notification={notif} 
                  isActive={idx === keyboardIndex}
                  onClick={() => markAsRead(notif.id)}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 px-8 text-center">
              <div className="mb-6 relative w-24 h-24">
                 <svg viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-sm">
                   <rect x="25" y="10" width="6" height="80" rx="2" fill="#FCD34D" /> 
                   <path d="M30 15H85C88 15 88 45 85 45H30V15Z" fill="#2563EB" />
                   <path d="M30 45H85C88 45 88 75 80 75H50L30 60V45Z" fill="#1D4ED8" />
                   <path d="M45 28L55 38H35L45 28Z" fill="#93C5FD" opacity="0.8" />
                   <circle cx="28" cy="10" r="4" fill="#F59E0B" />
                 </svg>
              </div>
              <h3 className="text-slate-900 font-medium">No notifications.</h3>
            </div>
          )}
        </div>

        <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
           <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Press</span>
              <div className="flex gap-1">
                 <kbd className="bg-white border border-slate-300 rounded px-1.5 py-0.5 font-sans shadow-sm">↓</kbd>
                 <kbd className="bg-white border border-slate-300 rounded px-1.5 py-0.5 font-sans shadow-sm">↑</kbd>
              </div>
              <span>to navigate</span>
           </div>
           
           <button 
             onClick={() => setShowShortcuts(!showShortcuts)}
             className={`text-xs font-semibold border border-slate-300 px-3 py-1 rounded transition-colors ${showShortcuts ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
           >
              {showShortcuts ? 'Hide shortcuts' : 'See all shortcuts'}
           </button>
        </div>
      </div>
    </>
  );
};