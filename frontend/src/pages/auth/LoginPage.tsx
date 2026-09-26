import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../lib/authContext";
import { extractErrorMessage } from "../../lib/api";
import { ShieldCheck, Mail, Lock, ArrowRight, Sparkles, User, Briefcase, GraduationCap, AlertCircle, CheckCircle2 } from "lucide-react";

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, switchRole } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(location.state?.message || null);


  const redirectByRole = (role: string) => {
    if (role === "recruiter") {
      navigate("/recruiter/dashboard");
    } else if (role === "college_admin") {
      navigate("/college/dashboard");
    } else if (role === "platform_admin") {
      navigate("/admin/dashboard");
    } else {
      navigate("/student/dashboard");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail || !password) {
      setError("Please provide both email and password.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const userRole = await login(trimmedEmail, password);
      redirectByRole(userRole);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Invalid credentials. Please check your email and password."));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoPreset = async (demoRole: "student" | "recruiter" | "college_admin") => {
    setError(null);
    setLoading(true);
    try {
      await switchRole(demoRole);
      redirectByRole(demoRole);
    } catch (err: any) {
      setError("Failed to activate demo persona.");
    } finally {
      setLoading(false);
    }
  };

  const handleAdminPreset = async () => {
    setError(null);
    setLoading(true);
    try {
      await switchRole("platform_admin");
      redirectByRole("platform_admin");
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to authenticate as Platform Admin."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[350px] bg-indigo-500/10 blur-[130px] rounded-full pointer-events-none -z-10" />

      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/25">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Sign In to Career<span className="text-indigo-400">Lens</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            AI-Powered Verified Career and Internship Matching Platform
          </p>
        </div>

        {/* Demo Fast-Access Card */}
        <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <Sparkles size={14} className="text-amber-400 fill-amber-400" />
              <span>1-Click Evaluation Presets</span>
            </div>
            <span className="text-[10px] font-mono uppercase bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">
              Judge Demo
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoPreset("student")}
              className="p-2.5 rounded-xl bg-slate-800/90 border border-amber-500/30 hover:border-amber-400 text-left transition-colors flex flex-col justify-between group"
            >
              <div className="text-sm mb-1">👨‍🎓</div>
              <div className="text-[11px] font-bold text-white group-hover:text-amber-300 truncate">
                Aarav
              </div>
              <div className="text-[9px] text-slate-400 uppercase font-mono">Student</div>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoPreset("recruiter")}
              className="p-2.5 rounded-xl bg-slate-800/90 border border-indigo-500/30 hover:border-indigo-400 text-left transition-colors flex flex-col justify-between group"
            >
              <div className="text-sm mb-1">💼</div>
              <div className="text-[11px] font-bold text-white group-hover:text-indigo-300 truncate">
                Sneha
              </div>
              <div className="text-[9px] text-slate-400 uppercase font-mono">Recruiter</div>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleDemoPreset("college_admin")}
              className="p-2.5 rounded-xl bg-slate-800/90 border border-emerald-500/30 hover:border-emerald-400 text-left transition-colors flex flex-col justify-between group"
            >
              <div className="text-sm mb-1">🏛️</div>
              <div className="text-[11px] font-bold text-white group-hover:text-emerald-300 truncate">
                Dr. Kapoor
              </div>
              <div className="text-[9px] text-slate-400 uppercase font-mono">College TPO</div>
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={handleAdminPreset}
              className="p-2.5 rounded-xl bg-slate-800/90 border border-purple-500/30 hover:border-purple-400 text-left transition-colors flex flex-col justify-between group"
            >
              <div className="text-sm mb-1">🛡️</div>
              <div className="text-[11px] font-bold text-white group-hover:text-purple-300 truncate">
                Admin
              </div>
              <div className="text-[9px] text-slate-400 uppercase font-mono">Admin</div>
            </button>
          </div>
        </div>

        {/* Login Form */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/50 border border-slate-700/80 shadow-2xl space-y-5">
          {notice && (
            <div className="p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                <span>{notice}</span>
              </div>
              <button type="button" onClick={() => setNotice(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
            </div>
          )}

          {error && (

            <div
              className={`p-3.5 rounded-xl border text-xs flex items-start gap-2.5 ${
                error.toLowerCase().includes("pending")
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-200"
                  : error.toLowerCase().includes("rejected")
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-200"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-300"
              }`}
            >
              <AlertCircle
                size={16}
                className={`shrink-0 mt-0.5 ${
                  error.toLowerCase().includes("pending") ? "text-amber-400" : "text-rose-400"
                }`}
              />
              <div className="space-y-0.5">
                <div className="font-semibold">
                  {error.toLowerCase().includes("pending")
                    ? "Approval Pending"
                    : error.toLowerCase().includes("rejected")
                    ? "Account Rejected"
                    : "Sign In Failed"}
                </div>
                <div className="leading-relaxed">{error}</div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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
              <span>{loading ? "Authenticating..." : "Sign In"}</span>
              <ArrowRight size={15} />
            </button>
          </form>

          <div className="pt-4 border-t border-slate-700/60 text-center text-xs text-slate-400">
            Don't have an account?{" "}
            <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2">
              Create an account
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
};
