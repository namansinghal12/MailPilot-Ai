import type { TaskItem, TaskStatus } from '../types/task';

const API_BASE_URL = "http://localhost:8000";

interface BackendTask {
  id: string;
  user_id: string;
  email_id?: string | null;
  title: string;
  description?: string | null;
  priority: TaskItem['priority'];
  status: TaskStatus;
  deadline?: string | null;
  completed: boolean;
  created_at: string;
}

function mapTask(t: BackendTask): TaskItem {
  return {
    id: t.id,
    sourceEmailId: t.email_id || undefined,
    title: t.title,
    description: t.description || '',
    priority: t.priority,
    status: t.status,
    dueDate: t.deadline ? new Date(t.deadline).toLocaleDateString() : 'No deadline',
    createdAt: t.created_at,
    tags: ['Inbox', t.priority],
  };
}

export const taskService = {
  async getTasks(): Promise<TaskItem[]> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("AUTH_REQUIRED");
      }
      throw new Error(`Failed to fetch tasks: ${response.status}`);
    }

    const data: BackendTask[] = await response.json();
    return data.map(mapTask);
  },

  async updateTaskStatus(id: string, status: TaskStatus): Promise<TaskItem | null> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        status,
        completed: status === 'completed',
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update task status: ${response.status}`);
    }

    const data: BackendTask = await response.json();
    return mapTask(data);
  },

  async deleteTask(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
      method: "DELETE",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Failed to delete task: ${response.status}`);
    }
  },
};
