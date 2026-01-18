import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X } from 'lucide-react';
import { Button } from '../../../components/Button';
import { createProjectSchema, CreateProjectFormData } from "../../Dashboard/schemas/project.ts";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateProjectFormData) => void;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<CreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: { category: 'Software' }
  });

  const onFormSubmit = (data: CreateProjectFormData) => {
    onSubmit(data);
    reset();
  };
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
          <h3 className="font-bold text-lg text-slate-900">Create Project</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors"><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit(onFormSubmit)} className="p-6 space-y-5">
          <div className="space-y-1">
            <label className="block text-sm font-bold text-slate-700">Project Name</label>
            <input {...register('name')} placeholder="e.g. Mobile App Redesign" className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:outline-none ${errors.name ? 'border-red-300 bg-red-50' : 'border-slate-200'}`} />
            {errors.name && <p className="text-xs text-red-500">{errors.name.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="block text-sm font-bold text-slate-700">Key</label>
              <input {...register('key')} placeholder="APP" maxLength={5} className={`w-full px-3 py-2 border rounded-lg uppercase focus:ring-2 focus:outline-none ${errors.key ? 'border-red-300' : 'border-slate-200'}`} />
              {errors.key && <p className="text-xs text-red-500">{errors.key.message}</p>}
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-bold text-slate-700">Category</label>
              <select {...register('category')} className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:outline-none bg-white">
                <option value="Software">Software</option>
                <option value="Marketing">Marketing</option>
                <option value="Business">Business</option>
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-bold text-slate-700">Description <span className="font-normal text-slate-400">(Optional)</span></label>
            <textarea {...register('description')} rows={3} className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:outline-none resize-none" />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
            <div className="w-auto"><Button type="submit" size="sm" isLoading={isSubmitting}>Create Project</Button></div>
          </div>
        </form>
      </div>
    </div>
  );
};
