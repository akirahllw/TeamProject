export const LoginHero = () => {
  return (
    <div className="space-y-6 text-center md:text-left">
      <h2 className="text-sm font-bold text-blue-600 uppercase tracking-wider">
        Scrumly for Students
      </h2>
      <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight">
        Connect every team, task, and project together.
      </h1>
      <p className="text-lg text-slate-600 max-w-md mx-auto md:mx-0">
        Collaborate, manage projects, and reach new productivity peaks. 
        Log in to access your student dashboard.
      </p>
      
      <div className="hidden md:inline-flex items-center gap-2 bg-white py-2 px-4 rounded-full shadow-sm text-sm font-medium text-slate-700">
        <span>Used by 5,000+ students</span>
      </div>
    </div>
  );
};