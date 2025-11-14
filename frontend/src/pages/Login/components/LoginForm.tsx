import React, { useState } from 'react';

const LoginForm = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log('Logging in with:', { email, password });
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-semibold text-gray-800 mb-2">
            Work email
          </label>
          <input 
            type="email" 
            id="email" 
            name="email" 
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            required
          />
        </div>
        <div>
          <div className="flex justify-between items-baseline">
            <label htmlFor="password" className="block text-sm font-semibold text-gray-800 mb-2">
              Password
            </label>
            <a href="#" className="text-sm text-blue-600 hover:underline">Forgot password?</a>
          </div>
          <input 
            type="password" 
            id="password" 
            name="password" 
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            required
          />
        </div>
        <button 
          type="submit" 
          className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 ease-in-out"
        >
          Log in
        </button>
      </form>
      <div className="mt-8 flex items-center justify-center text-sm text-gray-500">
        <span className="flex-grow border-t border-gray-300"></span>
        <p className="mx-4 flex-shrink-0">
          Don't have an account? 
          <a href="#" className="text-blue-600 hover:underline font-medium">Sign up</a>
        </p>
        <span className="flex-grow border-t border-gray-300"></span>
      </div>
    </>
  );
};

export default LoginForm;