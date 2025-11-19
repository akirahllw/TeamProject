import React from 'react';
import { LoginHero } from './components/LoginHero';
import { LoginForm } from './components/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen w-full bg-blue-50 flex items-center justify-center p-4 font-sans">
      {/* Main Layout Grid */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        
        {/* Left Side Component */}
        <LoginHero />

        {/* Right Side Component */}
        <LoginForm />
        
      </div>
    </div>
  );
}