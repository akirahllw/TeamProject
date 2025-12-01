import React from 'react';

interface UserAvatarProps {
  name: string;
  className?: string;
  bgColor?: string; 
}

export const UserAvatar: React.FC<UserAvatarProps> = ({ name, className = '', bgColor }) => {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const colors = [
    'bg-red-100 text-red-600',
    'bg-green-100 text-green-600',
    'bg-blue-100 text-blue-600',
    'bg-yellow-100 text-yellow-700',
    'bg-purple-100 text-purple-600',
  ];
  const colorClass = bgColor || colors[name.length % colors.length];

  return (
    <div
      className={`flex items-center justify-center font-bold rounded-full leading-none ${colorClass} ${className}`}
    >
      {initials}
    </div>
  );
};