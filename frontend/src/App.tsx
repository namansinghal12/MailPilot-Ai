import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import {
  AuthProvider,
  useAuthContext,
} from "./contexts/AuthContext";

import { NotificationProvider } from "./contexts/NotificationContext";
import { MainLayout } from "./layout/MainLayout";

import { LandingPage } from "./pages/Landing/LandingPage";
import { LoginPage } from "./pages/Authentication/LoginPage";
import { OnboardingPage } from "./pages/Onboarding/OnboardingPage";
import { InitializationPage } from "./pages/Onboarding/InitializationPage";
import { DashboardPage } from "./pages/Dashboard/DashboardPage";
import { InboxPage } from "./pages/Inbox/InboxPage";
import { EmailDetailPage } from "./pages/Email/EmailDetailPage";
import { AnalyticsPage } from "./pages/Analytics/AnalyticsPage";
import { TasksPage } from "./pages/Tasks/TasksPage";
import { AIChatPage } from "./pages/AIChat/AIChatPage";
import { SettingsPage } from "./pages/Settings/SettingsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/* -------------------------------------------------------
   Protected Route
------------------------------------------------------- */

const ProtectedRoute: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const {
    isAuthenticated,
    isLoading,
  } = useAuthContext();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 rounded-2xl bg-primary/15 border border-primary/30 flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-primary text-lg">
              ✦
            </span>
          </div>

          <p className="text-sm text-on-surface-variant">
            Loading your workspace...
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

/* -------------------------------------------------------
   Authenticated Layout
------------------------------------------------------- */

const WorkspaceRoute: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  return (
    <ProtectedRoute>
      <MainLayout>
        {children}
      </MainLayout>
    </ProtectedRoute>
  );
};

/* -------------------------------------------------------
   App
------------------------------------------------------- */

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <NotificationProvider>
        <BrowserRouter>
          <Routes>

            {/* ================================
                Public Routes
            ================================= */}

            <Route
              path="/"
              element={<LandingPage />}
            />

            <Route
              path="/login"
              element={<LoginPage />}
            />

            {/* ================================
                Authentication / Onboarding
            ================================= */}

            <Route
              path="/onboarding"
              element={
                <ProtectedRoute>
                  <OnboardingPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/initialization"
              element={
                <ProtectedRoute>
                  <InitializationPage />
                </ProtectedRoute>
              }
            />

            {/* ================================
                Main Workspace
            ================================= */}

            <Route
              path="/dashboard"
              element={
                <WorkspaceRoute>
                  <DashboardPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/inbox"
              element={
                <WorkspaceRoute>
                  <InboxPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/inbox/:id"
              element={
                <WorkspaceRoute>
                  <EmailDetailPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/analytics"
              element={
                <WorkspaceRoute>
                  <AnalyticsPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/tasks"
              element={
                <WorkspaceRoute>
                  <TasksPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/ai-chat"
              element={
                <WorkspaceRoute>
                  <AIChatPage />
                </WorkspaceRoute>
              }
            />

            <Route
              path="/settings"
              element={
                <WorkspaceRoute>
                  <SettingsPage />
                </WorkspaceRoute>
              }
            />

            {/* ================================
                404
            ================================= */}

            <Route
              path="*"
              element={<NotFoundPage />}
            />

          </Routes>
        </BrowserRouter>
      </NotificationProvider>
    </AuthProvider>
  );
};

export default App;