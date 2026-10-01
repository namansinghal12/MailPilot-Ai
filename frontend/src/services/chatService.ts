import type { ChatMessage, QuickPrompt } from '../types/chat';
import { PRESET_QUICK_PROMPTS } from '../constants/config';

const API_BASE_URL = "http://localhost:8000";

export const chatService = {
  async getQuickPrompts(): Promise<QuickPrompt[]> {
    return PRESET_QUICK_PROMPTS;
  },

  async getChatHistory(): Promise<ChatMessage[]> {
    return [];
  },

  async sendMessage(promptText: string): Promise<ChatMessage> {
    const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: promptText,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`AI Chat request failed: ${response.status} ${errorText}`);
    }

    return await response.json();
  },
};
