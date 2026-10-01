import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import {
  Sparkles,
  Mail,
  Lock,
  User,
  ArrowRight,
  Home,
  Eye,
  EyeOff,
  ShieldCheck,
} from "lucide-react";
import { Button } from "../../components/common/Button";
import { motion } from "framer-motion";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const {
    login,
    loginWithGoogle,
    register,
    isLoading,
    error,
  } = useAuth();

  const [mode, setMode] = useState<"login" | "register">("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setLocalError(null);

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        if (password.length < 8) {
          setLocalError(
            "Password must be at least 8 characters."
          );
          return;
        }

        await register(
          name,
          email,
          password
        );
      }

      navigate("/dashboard");
    } catch (err) {
      setLocalError(
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again."
      );
    }
  };

  const switchMode = () => {
    setMode(
      mode === "login"
        ? "register"
        : "login"
    );

    setLocalError(null);
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface flex items-center justify-center p-6 relative overflow-hidden">

      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[160px] pointer-events-none" />

      <div className="absolute bottom-0 right-0 w-[350px] h-[350px] bg-cyan-500/5 rounded-full blur-[140px] pointer-events-none" />

      <motion.div
        initial={{
          opacity: 0,
          scale: 0.96,
          y: 15,
        }}
        animate={{
          opacity: 1,
          scale: 1,
          y: 0,
        }}
        transition={{
          duration: 0.4,
        }}
        className="w-full max-w-md glass-panel p-8 sm:p-10 rounded-[28px] border border-white/10 shadow-2xl z-10"
      >

        {/* Logo */}
        <div className="text-center mb-7">

          <div className="w-14 h-14 rounded-2xl bg-primary/15 border border-primary/30 flex items-center justify-center text-primary mx-auto mb-5 shadow-lg shadow-primary/10">
            <Sparkles className="w-7 h-7" />
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-on-surface">
            {mode === "login"
              ? "Welcome back"
              : "Create your workspace"}
          </h1>

          <p className="text-sm text-on-surface-variant mt-2">
            {mode === "login"
              ? "Sign in to continue to your intelligent workspace."
              : "Start turning your inbox into an intelligent workspace."}
          </p>
        </div>

        {/* Google Button */}
        <button
          type="button"
          onClick={loginWithGoogle}
          disabled={isLoading}
          className="w-full h-12 rounded-2xl bg-white text-gray-900 font-semibold flex items-center justify-center gap-3 hover:bg-gray-100 transition-all disabled:opacity-60 disabled:cursor-not-allowed shadow-lg"
        >
          <Home className="w-5 h-5" />

          <span>
            Continue with Google
          </span>
        </button>

        {/* Divider */}
        <div className="flex items-center gap-4 my-6">
          <div className="h-px flex-1 bg-white/10" />

          <span className="text-[11px] uppercase tracking-wider text-on-surface-variant">
            or
          </span>

          <div className="h-px flex-1 bg-white/10" />
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >

          {/* Name — Registration only */}
          {mode === "register" && (
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-2">
                Full Name
              </label>

              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant/50" />

                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                  placeholder="Your name"
                  className="w-full bg-surface-container-lowest border border-white/10 rounded-2xl pl-10 pr-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary/40 focus:outline-none transition"
                />
              </div>
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-2">
              Email Address
            </label>

            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant/50" />

              <input
                type="email"
                required
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                className="w-full bg-surface-container-lowest border border-white/10 rounded-2xl pl-10 pr-4 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary/40 focus:outline-none transition"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-semibold text-on-surface-variant mb-2">
              Password
            </label>

            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant/50" />

              <input
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                required
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                placeholder={
                  mode === "register"
                    ? "Minimum 8 characters"
                    : "Enter your password"
                }
                autoComplete={
                  mode === "login"
                    ? "current-password"
                    : "new-password"
                }
                className="w-full bg-surface-container-lowest border border-white/10 rounded-2xl pl-10 pr-11 py-3 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary/40 focus:outline-none transition"
              />

              <button
                type="button"
                onClick={() =>
                  setShowPassword(
                    !showPassword
                  )
                }
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant/60 hover:text-on-surface transition"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Error */}
          {(localError || error) && (
            <div className="rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-xs text-red-300">
              {localError || error}
            </div>
          )}

          {/* Submit */}
          <Button
            type="submit"
            size="lg"
            isLoading={isLoading}
            className="w-full font-bold mt-5"
            rightIcon={
              <ArrowRight className="w-4 h-4" />
            }
          >
            {mode === "login"
              ? "Sign In"
              : "Create Account"}
          </Button>
        </form>

        {/* Security message */}
        <div className="flex items-center justify-center gap-2 mt-6 text-[11px] text-on-surface-variant">
          <ShieldCheck className="w-3.5 h-3.5" />

          <span>
            Your account is securely protected.
          </span>
        </div>

        {/* Switch mode */}
        <div className="mt-7 pt-6 border-t border-white/10 text-center">

          <p className="text-xs text-on-surface-variant">
            {mode === "login"
              ? "New to MailPilot?"
              : "Already have a MailPilot account?"}
          </p>

          <button
            type="button"
            onClick={switchMode}
            className="mt-2 text-sm font-semibold text-primary hover:text-primary/80 transition"
          >
            {mode === "login"
              ? "Create an account"
              : "Sign in instead"}
          </button>

        </div>

      </motion.div>
    </div>
  );
};