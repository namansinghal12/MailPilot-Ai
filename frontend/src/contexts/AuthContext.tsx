import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import type {
  User,
  UserRole,
  OnboardingData,
} from "../types/auth";

import { authService } from "../services/authService";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (
    email: string,
    password: string
  ) => Promise<void>;

  loginWithGoogle: () => void;

  register: (
    name: string,
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => Promise<void>;

  completeOnboarding: (
    role: UserRole
  ) => Promise<void>;
}

const AuthContext =
  createContext<AuthContextType | undefined>(
    undefined
  );

export const AuthProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [user, setUser] =
    useState<User | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  // --------------------------------------------------
  // Restore existing authenticated session
  // --------------------------------------------------
  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser =
          await authService.getCurrentUser();

        setUser(currentUser);
        setError(null);
      } catch (err) {
        console.error(
          "Failed to restore authentication session:",
          err
        );

        setUser(null);
        setError(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // --------------------------------------------------
  // Email + Password Login
  // --------------------------------------------------
  const login = async (
    email: string,
    password: string
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const loggedUser =
        await authService.login({
          email,
          password,
        });

      setUser(loggedUser);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Login failed";

      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // --------------------------------------------------
  // Google Login
  // --------------------------------------------------
  const loginWithGoogle = () => {
    setError(null);

    authService.loginWithGoogle();
  };

  // --------------------------------------------------
  // Registration
  // --------------------------------------------------
  const register = async (
    name: string,
    email: string,
    password: string
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const registeredUser =
        await authService.register(
          name,
          email,
          password
        );

      setUser(registeredUser);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Registration failed";

      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // --------------------------------------------------
  // Logout
  // --------------------------------------------------
  const logout = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await authService.logout();
    } catch (err) {
      console.error(
        "Logout request failed:",
        err
      );
    } finally {
      // Always clear frontend authentication state,
      // even if the backend request fails.
      setUser(null);
      setIsLoading(false);
      setError(null);
    }
  };

  // --------------------------------------------------
  // Complete Onboarding
  // --------------------------------------------------
  const completeOnboarding = async (
    role: UserRole
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const onboardingPayload: OnboardingData = {
        role,
        primaryGoals: [
          "Email productivity",
          "AI Summarization",
          "Task Extraction",
        ],
        inboxSyncFrequency: "realtime",
        aiTonePreference: "concise",
      };

      const updatedUser =
        await authService.updateOnboarding(
          onboardingPayload
        );

      setUser(updatedUser);
    } catch (err) {
      console.error(
        "Failed to complete onboarding:",
        err
      );

      setError(
        "Failed to complete onboarding"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        loginWithGoogle,
        register,
        logout,
        completeOnboarding,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// --------------------------------------------------
// Auth Hook
// --------------------------------------------------
export const useAuthContext = () => {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuthContext must be used within an AuthProvider"
    );
  }

  return context;
};