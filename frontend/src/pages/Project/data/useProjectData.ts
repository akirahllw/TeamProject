import { useState } from 'react';

export type TaskStatus = 'TO DO' | 'IN PROGRESS' | 'IN REVIEW' | 'DONE';
export type TaskType = 'Task' | 'Bug' | 'Story' | 'Epic'; 

export interface Task {
  id: string;
  key: string;
  title: string;
  type: TaskType; 
  status: TaskStatus;
  assignee: string;
  reporter: string;
  dueDate?: string;
  priority: 'High' | 'Medium' | 'Low' | 'None';
  created: string;
}

const INITIAL_TASKS: Task[] = [
  {
    id: '1',
    key: 'KAN-1',
    title: 'Research Competitors',
    type: 'Story', 
    status: 'TO DO',
    assignee: 'Unassigned',
    reporter: 'Artem Ratushnyi',
    priority: 'High',
    created: 'Jan 04, 2026'
  },
  {
    id: '2',
    key: 'KAN-2',
    title: 'Fix Login Crash',
    type: 'Bug', 
    status: 'IN PROGRESS',
    assignee: 'Artem Ratushnyi',
    reporter: 'Artem Ratushnyi',
    priority: 'High',
    created: 'Jan 05, 2026'
  }
];

export const useProjectData = () => {
  const [tasks, setTasks] = useState<Task[]>(INITIAL_TASKS);
  const [columns, setColumns] = useState<TaskStatus[]>(['TO DO', 'IN PROGRESS', 'IN REVIEW', 'DONE']);


const createTask = (
  title: string, 
  status: TaskStatus, 
  assignee: string, 
  type: TaskType = 'Task',
  priority: 'High' | 'Medium' | 'Low' | 'None' = 'None'
) => {
  const newTask: Task = {
    id: Date.now().toString(),
    key: `KAN-${tasks.length + 1}`,
    title,
    type,
    status,
    assignee: assignee || 'Unassigned',
    reporter: 'You',
    priority: priority, 
    created: new Date().toLocaleDateString()
  };
  setTasks([...tasks, newTask]);
};

  const updateStatus = (taskId: string, newStatus: TaskStatus) => {
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
  };

  const deleteTask = (taskId: string) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
  };

  const addColumn = (name: string) => {
    setColumns([...columns, name as TaskStatus]);
  };

  return { 
    tasks, 
    columns, 
    createTask, 
    updateStatus, 
    deleteTask, 
    addColumn 
  };
};