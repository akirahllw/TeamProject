import { useState, useEffect } from 'react';
import { Notification, MOCK_NOTIFICATIONS } from '../layout/data/notifications';

let globalNotifications: Notification[] = [];
let globalIsLoading = true;
let isInitialized = false;
const listeners = new Set<() => void>();

const emitChange = () => {
  listeners.forEach((listener) => listener());
};

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>(globalNotifications);
  const [isLoading, setIsLoading] = useState(globalIsLoading);

  useEffect(() => {
    const listener = () => {
      setNotifications([...globalNotifications]);
      setIsLoading(globalIsLoading);
    };
    
    listeners.add(listener);

    if (!isInitialized) {
      isInitialized = true;
      const fetchNotifications = async () => {
        globalIsLoading = true;
        emitChange();
        
        await new Promise((resolve) => setTimeout(resolve, 800));
        
        globalNotifications = MOCK_NOTIFICATIONS;
        globalIsLoading = false;
        emitChange();
      };
      fetchNotifications();
    } else {
        setNotifications([...globalNotifications]);
        setIsLoading(globalIsLoading);
    }

    return () => {
      listeners.delete(listener);
    };
  }, []);

  const markAsRead = (id: string) => {
    globalNotifications = globalNotifications.map((n) =>
      n.id === id ? { ...n, isRead: true } : n
    );
    emitChange();
  };

  const toggleReadStatus = (id: string) => {
    globalNotifications = globalNotifications.map((n) =>
      n.id === id ? { ...n, isRead: !n.isRead } : n
    );
    emitChange();
  };

  const markAllRead = () => {
    globalNotifications = globalNotifications.map((n) => ({ ...n, isRead: true }));
    emitChange();
  };

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  return {
    notifications,
    isLoading,
    unreadCount,
    markAsRead,
    toggleReadStatus,
    markAllRead,
  };
};