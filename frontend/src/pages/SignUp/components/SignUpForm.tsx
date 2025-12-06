import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowRight, AlertCircle } from 'lucide-react';

import { Input } from '../../../components/Input';
import { Button } from '../../../components/Button';
import { FormWrapper } from '../../../components/Form';
import { signUpSchema, SignUpFormData } from '../schemas/signup';

export const SignUpForm = () => {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    defaultValues: { fullName: '', email: '', password: '', confirmPassword: '' }
  });

  const onSubmit = async (data: SignUpFormData) => {
    setServerError(null);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      navigate('/');
    } catch (err) {
      setServerError((err as Error).message);
    }
  };

  return (
    <FormWrapper 
      title="Create an account" 
      subtitle="Get started with your free account today."
      onSubmit={handleSubmit(onSubmit)}
    >
      {serverError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm mb-4">
          <AlertCircle size={16} />
          <span>{serverError}</span>
        </div>
      )}
      <Controller
        name="fullName"
        control={control}
        render={({ field: { ref, ...field } }) => (
          <Input {...field} label="Full Name" placeholder="John Doe" error={errors.fullName?.message} />
        )}
      />

      <Controller
        name="email"
        control={control}
        render={({ field: { ref, ...field } }) => (
          <Input {...field} label="Email Address" type="email" placeholder="student@university.edu" error={errors.email?.message} />
        )}
      />

      <Controller
        name="password"
        control={control}
        render={({ field: { ref, ...field } }) => (
          <Input {...field} label="Password" type="password" placeholder="••••••••" error={errors.password?.message} />
        )}
      />

      <Controller
        name="confirmPassword"
        control={control}
        render={({ field: { ref, ...field } }) => (
          <Input {...field} label="Confirm Password" type="password" placeholder="••••••••" error={errors.confirmPassword?.message} />
        )}
      />

      <div className="pt-2">
        <Button type="submit" fullWidth isLoading={isSubmitting} icon={<ArrowRight size={18} />}>
          Create Account
        </Button>
      </div>

      <div className="text-center pt-4 border-t border-slate-100 mt-4">
        <p className="text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/" className="font-semibold text-blue-600 hover:text-blue-700 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </FormWrapper>
  );
};