import type { DashboardMetric } from '../types/analytics';

const API_BASE_URL = "http://localhost:8000";

export interface SmartAdvice {
  id: string;
  title: string;
  description: string;
  sourceSender: string;
  deadline?: string;
  actionText: string;
  emailId: string;
}

export interface DashboardSummary {
  metrics: DashboardMetric[];
  smartAdvice: SmartAdvice;
}

export const dashboardService = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/`, {
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
      throw new Error(`Failed to fetch dashboard summary: ${response.status}`);
    }

    return await response.json();
  },
};
