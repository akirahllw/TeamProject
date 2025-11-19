import React, { useState } from 'react';
import { ArrowRight, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Input } from '../../../components/Input'; 
import { Button } from '../../../components/Button';
import { FormWrapper } from '../../../components/Form';

export const LoginForm = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validate = () => {
    const newErrors: { [key: string]: string } = {};
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setErrors({});

    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      if (formData.email === 'fail@test.com') {
        throw new Error('Invalid credentials. Try again.');
      }

      setIsSuccess(true);
      console.log('Success', formData);
    } catch (err) {
      setErrors({ general: (err as Error).message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <FormWrapper 
      title="Welcome back" 
      subtitle="Please enter your details to sign in."
      onSubmit={handleSubmit}
    >
      {errors.general && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{errors.general}</span>
        </div>
      )}
      
      {isSuccess && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700 text-sm">
          <CheckCircle2 size={16} />
          <span>Success!</span>
        </div>
      )}

      <Input
        label="Email Address"
        placeholder="student@university.edu"
        type="email"
        value={formData.email}
        error={errors.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
      />

      <Input
        label="Password"
        placeholder="••••••••"
        type="password"
        value={formData.password}
        error={errors.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
      />

      <div className="flex justify-end">
        <a href="#" className="text-xs font-medium text-blue-600 hover:text-blue-700">
          Forgot password?
        </a>
      </div>

      <Button type="submit" isLoading={isLoading} icon={<ArrowRight size={18} />}>
        Log in
      </Button>

      <div className="text-center pt-4 border-t border-slate-100 mt-4">
        <p className="text-sm text-slate-500">
          Don't have an account?{' '}
          <a href="#" className="font-semibold text-blue-600 hover:text-blue-700">
            Sign up
          </a>
        </p>
      </div>
    </FormWrapper>
  );
};