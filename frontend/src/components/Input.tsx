import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ 
  label, 
  error, 
  type = "text", 
  className = "", 
  ...props 
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  return (
    <div className="space-y-1 w-full">
      <label className="block text-sm font-semibold text-slate-700">
        {label}
      </label>
      
      <div className="relative">
        <input
          type={inputType}
          className={`w-full px-4 py-3 rounded-lg border transition-all
            ${error 
              ? 'border-red-300 focus:ring-2 focus:ring-red-100 focus:border-red-500 bg-red-50/30' 
              : 'border-slate-200 focus:ring-2 focus:ring-blue-100 focus:border-blue-500 bg-white'
            } ${className} ${isPassword ? 'pr-10' : ''}`}
          {...props}
        />
        
        {/* Password Toggle Icon */}
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none"
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>

      {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
  );
};