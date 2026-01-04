import React from 'react';
import { UserAvatar } from '../../components/UserAvatar'; 
import { Notification } from '../data/notifications';

interface NotificationItemProps {
  notification: Notification;
  isActive: boolean;
  onClick: () => void;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({ 
  notification, 
  isActive,
  onClick 
}) => {
  return (
    <div 
      onClick={onClick}
      className={`
        group flex items-start gap-4 p-4 border-b border-slate-100 cursor-pointer transition-all
        ${isActive ? 'bg-blue-50' : 'hover:bg-slate-50'}
        ${!notification.isRead ? 'bg-blue-50/30' : 'bg-white'}
      `}
    >
      <div className="relative">
        <UserAvatar name={notification.author} className="w-10 h-10 text-xs bg-slate-200 text-slate-600" />
        {!notification.isRead && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 border-2 border-white rounded-full"></span>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-900 leading-snug">
          <span className="font-bold">{notification.author}</span>{' '}
          <span className="text-slate-600">{notification.title}</span>
        </p>
        <p className="text-sm font-medium text-blue-600 mt-0.5 truncate group-hover:underline">
          {notification.description}
        </p>
        <p className="text-xs text-slate-400 mt-1">{notification.time}</p>
      </div>

      <div className={`w-2 h-2 rounded-full mt-2 ${!notification.isRead ? 'bg-blue-600' : 'bg-transparent'}`} />
    </div>
  );
};