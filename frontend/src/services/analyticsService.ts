import type { EmailAnalytics } from '../types/analytics';

const API_BASE_URL = "http://localhost:8000";

export const analyticsService = {
  async getAnalytics(): Promise<EmailAnalytics> {
    const response = await fetch(`${API_BASE_URL}/api/analytics/`, {
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
      throw new Error(`Failed to fetch analytics: ${response.status}`);
    }

    return await response.json();
  },
};
