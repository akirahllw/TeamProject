import React from 'react';
import { UserAvatar } from './UserAvatar';
import { Button } from './Button';

export interface Organization {
  id: string;
  name: string;
  members: { name: string }[];
}

interface OrgCardProps {
  org: Organization;
  onGoToOrg: (orgId: string) => void;
}

export const OrgCard: React.FC<OrgCardProps> = ({ org, onGoToOrg }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div className="flex items-center gap-4">
        <UserAvatar name={org.name} className="w-12 h-12 text-lg bg-green-100 text-green-700" />
        
        <div>
          <h3 className="text-lg font-bold text-slate-900">{org.name}</h3>
          
          <div className="flex items-center mt-2">
            {org.members.slice(0, 3).map((member, index) => (
              <UserAvatar
                key={index}
                name={member.name}
                className="w-7 h-7 text-xs border-2 border-white -ml-2 first:ml-0"
              />
            ))}
            {org.members.length > 3 && (
              <div className="w-7 h-7 flex items-center justify-center rounded-full bg-slate-50 text-slate-500 text-xs font-medium border-2 border-white -ml-2 z-10">
                +{org.members.length - 3}
              </div>
            )}
          </div>
        </div>
      </div>
      <div className="w-full md:w-auto">
        <Button 
            variant="orange" 
            size="sm"
            onClick={() => onGoToOrg(org.id)}
            fullWidth
            className="md:w-auto"
        >
            Go to Scrumly
        </Button>
      </div>
    </div>
  );
};