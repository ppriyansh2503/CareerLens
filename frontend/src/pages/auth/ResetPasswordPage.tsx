import React, { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { authAPI, extractErrorMessage } from "../../lib/api";
import { ShieldCheck, Lock, CheckCircle2, AlertCircle, ArrowRight, ArrowLeft } from "lucide-react";

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") || "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setError("Password reset token is missing. Please request a new reset link.");
      return;
    }

    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match. Please verify both fields.");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await authAPI.resetPassword(token, newPassword, confirmPassword);
      setSuccess(true);
      setTimeout(() => {
        navigate("/login", {
          state: { message: "Your password has been reset successfully. Please log in with your new password." }
        });
      }, 2500);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to reset password. The link may have expired or already been used."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[320px] bg-indigo-500/10 blur-[130px] rounded-full pointer-events-none -z-10" />

      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/25">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Create New Password
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Enter and confirm your new secure password below.
          </p>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/50 border border-slate-700/80 shadow-2xl space-y-5">
          {success ? (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-start gap-3">
                <CheckCircle2 size={18} className="text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1 leading-relaxed">
                  <div className="font-semibold text-white">Password Reset Successfully!</div>
                  <div>Your password has been updated. Redirecting you to sign in...</div>
                </div>
              </div>

              <div className="pt-2 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  <ArrowRight size={14} />
                  <span>Go to Sign In immediately</span>
                </Link>
              </div>
            </div>
          ) : !token ? (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-3">
                <AlertCircle size={18} className="text-rose-400 shrink-0 mt-0.5" />
                <div className="space-y-1 leading-relaxed">
                  <div className="font-semibold text-white">Invalid Reset Link</div>
                  <div>No reset token was found in the link. Please request a new password reset email.</div>
                </div>
              </div>

              <div className="pt-2 text-center">
                <Link
                  to="/forgot-password"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  <ArrowLeft size={14} />
                  <span>Request a New Reset Link</span>
                </Link>
              </div>
            </div>
          ) : (
            <>
              {error && (
                <div className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-start gap-2.5">
                  <AlertCircle size={16} className="text-rose-400 shrink-0 mt-0.5" />
                  <div className="leading-relaxed">{error}</div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="password"
                      placeholder="Minimum 6 characters"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                      required
                      autoFocus
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="password"
                      placeholder="Re-enter your new password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
                >
                  <span>{loading ? "Updating Password..." : "Reset Password"}</span>
                  <ArrowRight size={15} />
                </button>
              </form>

              <div className="pt-4 border-t border-slate-700/60 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
                >
                  <ArrowLeft size={14} />
                  <span>Back to Sign In</span>
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
