import type {
  User,
  LoginCredentials,
  OnboardingData,
} from "../types/auth";

const API_BASE_URL = "http://localhost:8000";

interface BackendUser {
  id: string;
  name: string;
  email: string;
  profile_picture?: string | null;
  profession?: string | null;
}

function mapUser(user: BackendUser): User {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    avatarUrl: user.profile_picture || undefined,
    role: (user.profession as User["role"]) || undefined,
    isOnboarded: Boolean(user.profession),
    createdAt: new Date().toISOString(),
  };
}

export const authService = {
  async getCurrentUser(): Promise<User | null> {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/me`,
      {
        method: "GET",
        credentials: "include",
      }
    );

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      throw new Error(
        `Failed to load session: ${response.status}`
      );
    }

    const data: BackendUser = await response.json();

    return mapUser(data);
  },

  async login(
    credentials: LoginCredentials
  ): Promise<User> {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/login`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Invalid email or password"
      );
    }

    return mapUser(data.user);
  },

  async register(
    name: string,
    email: string,
    password: string
  ): Promise<User> {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/register`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Registration failed"
      );
    }

    return mapUser(data.user);
  },

  async loginWithGoogle(): Promise<void> {
    window.location.href =
      `${API_BASE_URL}/api/auth/google/login`;
  },

 async logout(): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/auth/logout`,
    {
      method: "POST",
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Logout failed: ${response.status}`
    );
  }
},

  async updateOnboarding(
    data: OnboardingData
  ): Promise<User> {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/onboarding`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          role: data.role,
        }),
      }
    );

    const resData = await response.json();

    if (!response.ok) {
      throw new Error(
        resData.detail || "Failed to update onboarding role"
      );
    }

    return mapUser(resData);
  },
};