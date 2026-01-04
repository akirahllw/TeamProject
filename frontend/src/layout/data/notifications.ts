export interface Notification {
  id: string;
  type: 'Direct' | 'Watching';
  title: string;
  description: string;
  time: string;
  isRead: boolean;
  avatar?: string; 
  author: string;
}

export const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: '1',
    type: 'Direct',
    author: 'Sarah Connor',
    title: 'mentioned you in',
    description: 'AYIST-12: Backend Architecture Review',
    time: '2 hours ago',
    isRead: false,
  },
  {
    id: '2',
    type: 'Watching',
    author: 'Jira Bot',
    title: 'updated status to Done',
    description: 'ECS-19: Build Vendor Creation Form',
    time: '5 hours ago',
    isRead: true,
  },
  {
    id: '3',
    type: 'Direct',
    author: 'Alex Smith',
    title: 'assigned to you',
    description: 'Bug-404: Login page crash on mobile',
    time: '1 day ago',
    isRead: false,
  },
  {
    id: '4',
    type: 'Watching',
    author: 'System',
    title: 'deployment successful',
    description: 'Release v2.0.1 is now live',
    time: '2 days ago',
    isRead: true,
  },
  {
    id: '5',
    type: 'Direct',
    author: 'Team Lead',
    title: 'requested changes',
    description: 'PR #892: Update notification styles',
    time: '3 days ago',
    isRead: true,
  }
];