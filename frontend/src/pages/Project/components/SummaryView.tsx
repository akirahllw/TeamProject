import React, { useEffect, useState } from 'react';
import { Task } from '../data/useProjectData';
import { CheckCircle2, Edit3, FilePlus, Calendar } from 'lucide-react';

interface SummaryViewProps {
  tasks: Task[];
}

export const SummaryView: React.FC<SummaryViewProps> = ({ tasks }) => {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // --- METRICS ---
  const total = tasks.length || 0;
  const doneCount = tasks.filter(t => t.status === 'DONE').length;
  const inProgressCount = tasks.filter(t => t.status === 'IN PROGRESS').length;
  const reviewCount = tasks.filter(t => t.status === 'IN REVIEW').length;
  const todoCount = tasks.filter(t => t.status === 'TO DO').length;

  const donePct = total ? (doneCount / total) * 100 : 0;
  const progressPct = total ? ((inProgressCount + reviewCount) / total) * 100 : 0;
  const todoPct = total ? (todoCount / total) * 100 : 0;

  const priorities = ['High', 'Medium', 'Low', 'None'];
  const priorityCounts = priorities.map(p => ({
    label: p,
    count: tasks.filter(t => t.priority === p).length
  }));
  const maxPriorityCount = Math.max(...priorityCounts.map(p => p.count), 1);

  const uniqueAssignees = Array.from(new Set(tasks.map(t => t.assignee)));
  const workload = uniqueAssignees.map(user => ({
    name: user,
    count: tasks.filter(t => t.assignee === user).length,
    percent: total ? Math.round((tasks.filter(t => t.assignee === user).length / total) * 100) : 0
  })).sort((a, b) => b.count - a.count);

  return (
    <div className="p-8 bg-slate-50 min-h-full font-sans text-slate-900">
      
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard icon={<CheckCircle2 className="text-green-600"/>} label="completed" count={doneCount} sub="Total completed" />
        <StatCard icon={<Edit3 className="text-blue-600"/>} label="in progress" count={inProgressCount + reviewCount} sub="Active work" />
        <StatCard icon={<FilePlus className="text-slate-600"/>} label="created" count={total} sub="Total tasks" />
        <StatCard icon={<Calendar className="text-red-600"/>} label="due soon" count={0} sub="In the next 7 days" />
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-base font-bold text-slate-800 mb-1">Status overview</h3>
          <p className="text-xs text-slate-500 mb-8">Get a snapshot of the status of your work items.</p>
          
          <div className="flex items-center gap-10 justify-center">
            <div className="relative w-48 h-48">
              <svg viewBox="0 0 36 36" className="w-full h-full rotate-[-90deg]">
                <path className="text-slate-100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                <circle r="15.9155" cx="18" cy="18" fill="none" stroke="#22c55e" strokeWidth="3" strokeDasharray={`${animate ? donePct : 0}, 100`} strokeLinecap="round" className="transition-all duration-[1500ms] ease-out" />
                <circle r="15.9155" cx="18" cy="18" fill="none" stroke="#3b82f6" strokeWidth="3" strokeDasharray={`${animate ? progressPct : 0}, 100`} strokeDashoffset={`-${donePct}`} strokeLinecap="round" className="transition-all duration-[1500ms] ease-out delay-100" />
                <circle r="15.9155" cx="18" cy="18" fill="none" stroke="#cbd5e1" strokeWidth="3" strokeDasharray={`${animate ? todoPct : 0}, 100`} strokeDashoffset={`-${donePct + progressPct}`} strokeLinecap="round" className="transition-all duration-[1500ms] ease-out delay-200" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center animate-in fade-in duration-1000">
                <span className="text-4xl font-extrabold text-slate-800">{total}</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide mt-1">Total Items</span>
              </div>
            </div>
            <div className="space-y-3 text-sm font-medium">
              <div className="flex items-center gap-3"><span className="w-3 h-3 bg-green-500 rounded-full shadow-sm"></span> <span className="text-slate-600">Done</span> <span className="ml-auto font-bold text-slate-800">{doneCount}</span></div>
              <div className="flex items-center gap-3"><span className="w-3 h-3 bg-blue-500 rounded-full shadow-sm"></span> <span className="text-slate-600">In Progress</span><span className="ml-auto font-bold text-slate-800">{inProgressCount + reviewCount}</span></div>
              <div className="flex items-center gap-3"><span className="w-3 h-3 bg-slate-300 rounded-full shadow-sm"></span> <span className="text-slate-600">To Do</span><span className="ml-auto font-bold text-slate-800">{todoCount}</span></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <div className="mb-6">
             <h3 className="text-base font-bold text-slate-800">Priority breakdown</h3>
             <p className="text-xs text-slate-500 mt-1">How work is being prioritized across the team.</p>
          </div>

          <div className="flex-1 flex items-end justify-between gap-6 px-4 pb-2 border-b border-slate-100 relative h-40">
             
             <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-50 z-0">
                <div className="border-t border-dashed border-slate-100 w-full h-0"></div>
                <div className="border-t border-dashed border-slate-100 w-full h-0"></div>
                <div className="border-t border-dashed border-slate-100 w-full h-0"></div>
                <div className="border-t border-dashed border-slate-100 w-full h-0"></div>
             </div>

             {priorityCounts.map((p) => {
               const heightPercent = (p.count / maxPriorityCount) * 100;
               const colorClass = 
                 p.label === 'High' ? 'bg-red-400' : 
                 p.label === 'Medium' ? 'bg-orange-300' : 
                 p.label === 'Low' ? 'bg-blue-300' : 'bg-slate-400';

               return (
                 <div key={p.label} className="flex-1 flex flex-col items-center justify-end group relative z-10 h-full">
                    
                    <div className="opacity-0 group-hover:opacity-100 absolute -top-8 transition-opacity bg-slate-800 text-white text-[10px] py-1 px-2 rounded pointer-events-none mb-2 z-20 whitespace-nowrap">
                       {p.count} tasks
                    </div>

                    <div className="w-full max-w-[48px] bg-slate-50 rounded-t-sm relative overflow-hidden h-full flex items-end">
                       <div 
                         className={`w-full rounded-t-sm transition-all duration-[1200ms] cubic-bezier(0.34, 1.56, 0.64, 1) ${colorClass}`}
                         style={{ 
                            height: animate ? `${heightPercent}%` : '0%', 
                            opacity: animate ? 1 : 0
                         }}
                       ></div>
                    </div>
                 </div>
               );
             })}
          </div>
          
          <div className="flex justify-between px-4 mt-3 text-xs font-semibold text-slate-500">
             {priorityCounts.map(p => (
                <div key={p.label} className="flex-1 text-center">{p.label}</div>
             ))}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-base font-bold text-slate-800 mb-1">Team workload</h3>
        <p className="text-xs text-slate-500 mb-6">Monitor the capacity of your team.</p>
        <table className="w-full text-left">
          <thead>
            <tr className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
              <th className="pb-3 w-1/3 pl-2">Assignee</th>
              <th className="pb-3">Work distribution</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {workload.map((user, idx) => (
              <tr key={user.name} className="group hover:bg-slate-50 transition-colors">
                <td className="py-3 pl-2 flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm ${['bg-blue-500','bg-purple-500','bg-pink-500'][idx % 3]}`}>
                    {user.name.charAt(0)}
                  </div>
                  <span className="text-slate-700 font-medium">{user.name}</span>
                </td>
                <td className="py-3">
                  <div className="w-full flex items-center gap-4">
                    <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden relative">
                       <div className="absolute top-0 left-0 h-full bg-slate-500 rounded-full transition-all duration-1000 ease-out" style={{ width: animate ? `${user.percent}%` : '0%' }}></div>
                    </div>
                    <span className="text-xs font-bold text-slate-500 w-8 text-right">{user.percent}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ icon, label, count, sub }: { icon: any, label: string, count: number, sub: string }) => (
  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
    <div className="flex items-center gap-3 mb-2">
      <div className="p-2.5 bg-slate-50 rounded-lg">{icon}</div>
      <div className="text-3xl font-bold text-slate-800">{count}</div>
    </div>
    <div className="text-sm font-bold text-slate-700 capitalize">{label}</div>
    <div className="text-xs text-slate-400 mt-1">{sub}</div>
  </div>
);