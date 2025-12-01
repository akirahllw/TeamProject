import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  variant?: 'primary' | 'secondary' | 'orange'; 
  size?: 'sm' | 'md' | 'lg';              
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  isLoading = false,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = "w-full py-3 px-4 rounded-lg font-bold transition-all transform flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-offset-1";
  const widthClass = fullWidth ? "w-full" : "w-auto";
  const sizes = {
    sm: "py-2 px-4 text-sm",
    md: "py-3 px-6 text-base", 
    lg: "py-4 px-8 text-lg"    
  };
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 focus:ring-blue-500 hover:scale-[1.01]",
    secondary: "bg-slate-100 hover:bg-slate-200 text-slate-700 focus:ring-slate-400",
    orange: "bg-[#E87B35] hover:bg-[#d66a2a] text-white shadow-sm focus:ring-orange-500 hover:scale-[1.02]"
  };

 return (
    <button
      disabled={isLoading || disabled}
      className={`${baseStyles} ${widthClass} ${sizes[size]} ${variants[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        <>
          {children}
          {icon && <span>{icon}</span>}
        </>
      )}
    </button>
  );
};