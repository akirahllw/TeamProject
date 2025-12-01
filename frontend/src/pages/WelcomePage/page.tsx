import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { OrgCard, Organization } from '../../components/OrgCard';
import { UserAvatar } from '../../components/UserAvatar';
import { Button } from '../../components/Button';

// --- MOCK DATA (useEffect will come soon.....) ---
const mockUser = {
  id: 'u1',
  name: 'Test Test',
};

const mockOrgs: Organization[] = [
  {
    id: 'org_123',
    name: 'testing-tested7583632',
    members: [
      { name: 'Test Test' },
      { name: 'Alice Developer' },
      { name: 'Bob Manager' },
      { name: 'Charlie Designer' },
      { name: 'Dave QA' },
    ],
  },
  {
    id: 'org_456',
    name: 'University Project Team',
    members: [{ name: 'Test Test' }, { name: 'Sarah Croft' }],
  },
];

export default function WelcomePage() {
  const navigate = useNavigate();

  const handleGoToOrg = (orgId: string) => {
    console.log(`Navigating to organization dashboard for ID: ${orgId}`);
    navigate('/dashboard'); 
  };
  const handleGlobalNav = () => {
    navigate('/dashboard');
};

  return (
    <div className="min-h-screen bg-[#EEF4FF] font-sans">
      
      <header className="bg-white py-3 px-6 md:px-10 flex items-center justify-between border-b border-slate-100 sticky top-0 z-50">
        <div className="text-2xl font-extrabold text-slate-900">Scrumly</div>
        <div className="flex items-center gap-4 md:gap-6">
          <div className="hidden md:block">
             <Button variant="primary" size="sm" onClick={handleGlobalNav}>
                Go to Scrumly
             </Button>
          </div>
          <div className="flex items-center gap-3 pl-4 md:pl-6 border-l border-slate-200">
            <UserAvatar name={mockUser.name} className="w-9 h-9 text-sm bg-slate-100 text-slate-600" />
            <span className="font-bold text-slate-800 hidden sm:block">{mockUser.name}</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto py-12 px-4 md:py-20">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900">
              Welcome back, {mockUser.name.split(' ')[0]}
            </h1>
            <p className="text-slate-500 font-medium mt-2">
              Pick up where you left in Scrumly
            </p>
          </div>
          <Link
            to="/create-org"
            className="text-blue-600 font-bold hover:text-blue-700 hover:underline transition-all whitespace-nowrap"
          >
            Create a new organisation
          </Link>
        </div>
        <div className="space-y-4">
          {mockOrgs.length > 0 ? (
            mockOrgs.map((org) => (
              <OrgCard key={org.id} org={org} onGoToOrg={handleGoToOrg} />
            ))
          ) : (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-slate-100 text-slate-500">
              You aren't part of any organizations yet.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}