import React, { useState } from "react";
import { Link } from "react-router-dom";
import { authAPI, extractErrorMessage } from "../../lib/api";
import { ShieldCheck, Mail, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle, PhoneCall, Info } from "lucide-react";

export const ForgotPasswordPage: React.FC = () => {
  const [identifier, setIdentifier] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = identifier.trim();
    if (!trimmed) {
      setError("Please enter your registered email address or phone number.");
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const res = await authAPI.forgotPassword(trimmed);
      setSuccessMessage(
        res.message ||
        "If an account exists with these details, a password reset link has been sent to the registered email address."
      );
    } catch (err: any) {
      // Even on API error, display helpful message or fallback
      setError(extractErrorMessage(err, "Unable to process password reset request. Please try again."));
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
            Reset Your Password
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Enter your registered email address or phone number to receive a secure reset link.
          </p>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/50 border border-slate-700/80 shadow-2xl space-y-5">
          {successMessage ? (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-start gap-3">
                <CheckCircle2 size={18} className="text-emerald-400 shrink-0 mt-0.5" />
                <div className="space-y-1 leading-relaxed">
                  <div className="font-semibold text-white">Reset Link Dispatched</div>
                  <div>{successMessage}</div>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-700 text-xs text-slate-300 flex items-start gap-2.5">
                <Info size={16} className="text-indigo-400 shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <strong>Security notice:</strong> For your security, the password reset link is always delivered directly to your registered email inbox, even when requesting via phone number.
                </div>
              </div>

              <div className="pt-2 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  <ArrowLeft size={14} />
                  <span>Return to Sign In</span>
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

              {/* Informative Security Banner */}
              <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-200 flex items-start gap-2.5">
                <PhoneCall size={16} className="text-indigo-400 shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  If you enter a registered phone number, the password reset link is securely sent to your account's registered email address.
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Email or Phone Number
                  </label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      placeholder="you@example.com or 10-digit phone"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                      required
                      autoFocus
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
                >
                  <span>{loading ? "Sending Reset Link..." : "Continue"}</span>
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
