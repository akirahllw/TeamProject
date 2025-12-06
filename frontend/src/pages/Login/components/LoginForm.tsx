import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, AlertCircle } from 'lucide-react';

import { Input } from '../../../components/Input';
import { Button } from '../../../components/Button';
import { FormWrapper } from '../../../components/Form';
import { loginSchema, LoginFormData } from '../schemas/login';

export const LoginForm = () => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' }
  });

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      if (data.email === 'error@test.com') throw new Error("Invalid credentials.");
      navigate('/welcome');
    } catch (err) {
      setServerError((err as Error).message);
    }
  };

  return (
    <FormWrapper 
      title="Welcome back" 
      subtitle="Please enter your details to sign in."
      onSubmit={handleSubmit(onSubmit)} 
    >
      {serverError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm mb-4">
          <AlertCircle size={16} />
          <span>{serverError}</span>
        </div>
      )}
      <Controller
        name="email"
        control={control}
        render={({ field: { ref, ...field } }) => (
          <Input
            {...field}
            label="Email Address"
            placeholder="student@university.edu"
            type="email"
            error={errors.email?.message}
          />
        )}
      />

      <div className="space-y-1">
        <div className="flex justify-between items-center">
            <label className="block text-sm font-semibold text-slate-700">Password</label>
            <a href="#" className="text-xs font-medium text-blue-600 hover:text-blue-700">Forgot password?</a>
        </div>
        
        <Controller
          name="password"
          control={control}
          render={({ field: { ref, ...field } }) => (
            <Input
              {...field}
              label=""
              placeholder="••••••••"
              type="password"
              className="mt-0" 
              error={errors.password?.message}
            />
          )}
        />
      </div>

      <Button 
        type="submit" 
        fullWidth 
        isLoading={isSubmitting} 
        icon={<ArrowRight size={18} />}
      >
        Log in
      </Button>

      <div className="text-center pt-4 border-t border-slate-100 mt-4">
        <p className="text-sm text-slate-500">
          Don't have an account?{' '}
          <Link to="/create" className="font-semibold text-blue-600 hover:text-blue-700 hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </FormWrapper>
  );
};