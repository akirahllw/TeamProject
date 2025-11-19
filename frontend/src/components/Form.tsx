import React from 'react';

interface FormWrapperProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  onSubmit?: (e: React.FormEvent) => void;
}

export const FormWrapper: React.FC<FormWrapperProps> = ({ 
  children, 
  title, 
  subtitle,
  onSubmit 
}) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 md:p-10 w-full max-w-md mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
        {subtitle && <p className="text-slate-500 text-sm mt-1">{subtitle}</p>}
      </div>
      
      <form onSubmit={onSubmit} className="space-y-5">
        {children}
      </form>
    </div>
  );
};