import type { UserSettings } from '../types/settings';

const API_BASE_URL = "http://localhost:8000";

export const settingsService = {
  async getSettings(): Promise<UserSettings> {
    const response = await fetch(`${API_BASE_URL}/api/settings/`, {
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
      throw new Error(`Failed to fetch settings: ${response.status}`);
    }

    return await response.json();
  },

  async updateSettings(newSettings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await fetch(`${API_BASE_URL}/api/settings/`, {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newSettings),
    });

    if (!response.ok) {
      throw new Error(`Failed to update settings: ${response.status}`);
    }

    return await response.json();
  },
};
