import React from 'react';
import { SignUpHero } from './components/SignUpHero';
import { SignUpForm } from './components/SignUpForm';

export default function SignUpPage() {
  return (
    <div className="min-h-screen w-full bg-blue-50 flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <SignUpHero />
        <SignUpForm />
      </div>
    </div>
  );
}