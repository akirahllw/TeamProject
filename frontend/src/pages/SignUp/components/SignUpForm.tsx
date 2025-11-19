import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle } from 'lucide-react';
import { Input } from '../../../components/Input'; 
import { Button } from '../../../components/Button';
import { FormWrapper } from '../../../components/Form';
// import { authService } from '../../../services/authService'; 

export const SignUpForm = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const newErrors: { [key: string]: string } = {};
    
    if (!formData.fullName) newErrors.fullName = 'Full name is required';
    if (!formData.email) newErrors.email = 'Email is required';
    
    if (!formData.password) {
        newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
        newErrors.password = 'Password must be at least 6 chars';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setErrors({});

   //Simulate API call
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      console.log('Account created', formData);
    } catch (err) {
      setErrors({ general: 'Failed to create account. Try again.' });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <FormWrapper 
      title="Create an account" 
      subtitle="Get started with your free account today."
      onSubmit={handleSubmit}
    >
      {errors.general && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{errors.general}</span>
        </div>
      )}

      <Input
        label="Full Name"
        placeholder="John Doe"
        value={formData.fullName}
        error={errors.fullName}
        onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
      />

      <Input
        label="Email Address"
        type="email"
        placeholder="student@university.edu"
        value={formData.email}
        error={errors.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
      />

      <Input
        label="Password"
        type="password"
        placeholder="••••••••"
        value={formData.password}
        error={errors.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
      />

      <Input
        label="Confirm Password"
        type="password"
        placeholder="••••••••"
        value={formData.confirmPassword}
        error={errors.confirmPassword}
        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
      />

      <Button type="submit" isLoading={isLoading} icon={<ArrowRight size={18} />}>
        Create Account
      </Button>

      <div className="text-center pt-4 border-t border-slate-100 mt-4">
        <p className="text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </FormWrapper>
  );
};