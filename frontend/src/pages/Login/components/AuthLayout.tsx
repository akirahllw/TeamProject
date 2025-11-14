import React from 'react';

interface AuthLayoutProps {
  title: string;
  children: React.ReactNode; 
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ title, children }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-50 via-white to-purple-50 text-gray-900 min-h-screen relative p-8 sm:p-12">
      <header className="absolute top-8 left-8 sm:top-12 sm:left-12">
        <h1 className="font-bold text-2xl text-gray-800">Scrumly</h1>
      </header>
      <main className="min-h-[calc(100vh-6rem)] w-full flex items-center justify-center lg:justify-start">
        <div className="max-w-md w-full lg:ml-[8vw]">
          <h2 className="text-4xl sm:text-5xl font-bold leading-tight mb-8">
            {title}
          </h2>
          {children}
        </div>
      </main>
    </div>
  );
};

export default AuthLayout;