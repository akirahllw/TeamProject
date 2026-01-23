import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../../../api/api';

export type TaskStatus = 'TO DO' | 'IN PROGRESS' | 'IN REVIEW' | 'DONE';

export interface Task {
  id: string; // Python might return int, but string is safer for frontend keys
  key: string;
  title: string;
  type: 'Task' | 'Bug' | 'Story';
  status: TaskStatus;
  assignee: string;
  priority: string;
  created: string;
}

export const useProjectData = () => {
  const { projectId } = useParams(); // This will be the Project KEY (e.g., "AYIST")
  const [tasks, setTasks] = useState<Task[]>([]);
  const [columns] = useState<TaskStatus[]>(['TO DO', 'IN PROGRESS', 'IN REVIEW', 'DONE']);
  const [isLoading, setIsLoading] = useState(true);

  // 1. FETCH TASKS FROM API
  useEffect(() => {
    if (!projectId) return;

    const fetchTasks = async () => {
      setIsLoading(true);
      try {
        // Backend should define: GET /api/projects/{key}/issues
        const response = await api.get<Task[]>(`/projects/${projectId}/issues`);
        setTasks(response.data);
      } catch (err) {
        console.error("Failed to load tasks", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [projectId]);

  // 2. CREATE TASK
  const createTask = async (title: string, status: TaskStatus, assignee: string, type: any, priority: any) => {
    // Optimistic Update (Show it immediately)
    const tempId = Date.now().toString();
    const newTask: Task = {
      id: tempId,
      key: `${projectId}-...`, 
      title,
      status,
      assignee: assignee || 'Unassigned',
      type,
      priority,
      created: new Date().toLocaleDateString()
    };
    
    setTasks(prev => [...prev, newTask]);

    try {
      // Send to Backend
      const response = await api.post(`/projects/${projectId}/issues`, {
        title, status, assignee, type, priority
      });
      
      // Replace temp task with real data from server
      setTasks(prev => prev.map(t => t.id === tempId ? response.data : t));
    } catch (error) {
      console.error("Failed to create task", error);
      // Rollback on error
      setTasks(prev => prev.filter(t => t.id !== tempId));
    }
  };

  // 3. UPDATE STATUS (Drag and Drop / Dropdown)
  const updateStatus = async (taskId: string, newStatus: TaskStatus) => {
    // Optimistic Update
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));

    try {
      await api.patch(`/issues/${taskId}`, { status: newStatus });
    } catch (error) {
      console.error("Failed to update status", error);
    }
  };

  return { 
    tasks, 
    columns, 
    isLoading,
    createTask, 
    updateStatus, 
    // ... export other functions
  };
};