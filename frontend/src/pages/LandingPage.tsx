import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../lib/authContext';
import { 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  Award, 
  FileSearch, 
  Fingerprint, 
  CheckCircle2, 
  Users, 
  BarChart3, 
  Globe2 
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { switchRole } = useAuth();

  return (
    <div className="relative overflow-hidden pt-8 pb-20">
      
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-indigo-500/15 blur-[120px] rounded-full pointer-events-none -z-10" />
      <div className="absolute top-1/3 right-10 w-[300px] h-[300px] bg-purple-500/10 blur-[100px] rounded-full pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto pt-8 pb-12">
          
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-6">
            <Sparkles size={14} className="text-indigo-400" />
            <span>AI-Powered Verified Career & Internship Matching</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.15]">
            Bridging the Trust Gap in{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Campus Hiring
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-300 leading-relaxed">
            CareerLens eliminates resume fraud with a 4-tier forensic verification engine (OCR, QR, Hash checks & ELA tamper detection), pairing students with internships through explainable match scoring and bilingual AI mentorship.
          </p>

          {/* Primary Action Buttons */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/login"
              className="flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-indigo-600 text-white font-semibold text-sm shadow-xl shadow-indigo-500/25 hover:bg-indigo-500 transition-all hover:scale-105"
            >
              <span>Sign In to Your Portal</span>
              <ArrowRight size={16} />
            </Link>

            <Link
              to="/register"
              className="flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-slate-800/90 text-slate-200 border border-slate-700 font-semibold text-sm hover:bg-slate-700 transition-all"
            >
              <span>Create Free Account</span>
            </Link>

            <button
              onClick={async () => {
                await switchRole('student');
                window.location.href = '/student/dashboard';
              }}
              className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-amber-500/10 text-amber-300 border border-amber-500/30 font-semibold text-sm hover:bg-amber-500/20 transition-all"
            >
              <Sparkles size={16} />
              <span>Instant Judge Demo (Aarav)</span>
            </button>
          </div>

          <div className="mt-6 text-xs text-slate-500 flex items-center justify-center gap-4 flex-wrap">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 size={13} className="text-emerald-400" />
              Real Multi-Role Auth & Registration
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 size={13} className="text-indigo-400" />
              100% Pre-Seeded Hackathon Demo
            </span>
            <span className="flex items-center gap-1.5">
              <Globe2 size={13} className="text-purple-400" />
              English + Hindi + Hinglish
            </span>
          </div>

        </div>

        {/* Role Portal Cards */}
        <div className="mt-4 mb-16">
          <div className="text-center max-w-xl mx-auto mb-8">
            <span className="text-xs font-mono font-semibold text-indigo-400 tracking-wider uppercase">
              Select Your Access Portal
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
              Engineered for Students, Recruiter Teams, and Colleges
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Student Card */}
            <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 hover:border-indigo-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-4">
                  <ShieldCheck size={24} />
                </div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">Student Portal</h3>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">Candidate</span>
                </div>
                <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                  Upload resumes, extract skills automatically, verify credentials via 4-tier checks, inspect match scores, and chat with AI mentor.
                </p>
                <ul className="space-y-2 mb-6 text-xs text-slate-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Resume parsing & skill extraction</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Upload & verify PDF/image credentials</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Explainable match breakdown & roadmap</span>
                  </li>
                </ul>
              </div>
              <div className="space-y-2 pt-4 border-t border-slate-800">
                <Link
                  to="/login?role=student"
                  className="w-full block py-2.5 px-4 text-center rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors"
                >
                  Student Login
                </Link>
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to="/register?role=student"
                    className="py-2 px-3 text-center rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition-colors"
                  >
                    Register
                  </Link>
                  <button
                    onClick={async () => {
                      await switchRole('student');
                      window.location.href = '/student/dashboard';
                    }}
                    className="py-2 px-3 text-center rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-xs border border-amber-500/30 transition-colors"
                  >
                    Aarav (Demo)
                  </button>
                </div>
              </div>
            </div>

            {/* Recruiter Card */}
            <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 hover:border-purple-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-400 flex items-center justify-center mb-4">
                  <Users size={24} />
                </div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">Recruiter Portal</h3>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">Employer</span>
                </div>
                <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                  Discover verified talent with tamper-audit trails, post jobs, inspect match scores, and eliminate fraudulent applications.
                </p>
                <ul className="space-y-2 mb-6 text-xs text-slate-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Candidate search with verification filters</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Direct credential proof inspection</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Manage job listings & applicants</span>
                  </li>
                </ul>
              </div>
              <div className="space-y-2 pt-4 border-t border-slate-800">
                <Link
                  to="/login?role=recruiter"
                  className="w-full block py-2.5 px-4 text-center rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs transition-colors"
                >
                  Recruiter Login
                </Link>
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to="/register?role=recruiter"
                    className="py-2 px-3 text-center rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition-colors"
                  >
                    Register
                  </Link>
                  <button
                    onClick={async () => {
                      await switchRole('recruiter');
                      window.location.href = '/recruiter/dashboard';
                    }}
                    className="py-2 px-3 text-center rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 text-xs border border-purple-500/30 transition-colors"
                  >
                    Sneha (Demo)
                  </button>
                </div>
              </div>
            </div>

            {/* College TPO Card */}
            <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 hover:border-cyan-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-4">
                  <BarChart3 size={24} />
                </div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">College / TPO Portal</h3>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">Institution</span>
                </div>
                <p className="text-xs text-slate-400 mb-6 leading-relaxed">
                  Monitor cohort verification status, identify departmental skill gaps, track placement readiness, and audit campus credentials.
                </p>
                <ul className="space-y-2 mb-6 text-xs text-slate-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Real-time cohort placement metrics</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Departmental skill deficit heatmaps</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                    <span>Verification log & tamper audit report</span>
                  </li>
                </ul>
              </div>
              <div className="space-y-2 pt-4 border-t border-slate-800">
                <Link
                  to="/login?role=college_admin"
                  className="w-full block py-2.5 px-4 text-center rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors"
                >
                  TPO Login
                </Link>
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to="/register?role=college_admin"
                    className="py-2 px-3 text-center rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 transition-colors"
                  >
                    Register
                  </Link>
                  <button
                    onClick={async () => {
                      await switchRole('college_admin');
                      window.location.href = '/college/dashboard';
                    }}
                    className="py-2 px-3 text-center rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs border border-cyan-500/30 transition-colors"
                  >
                    Dr. Kapoor (Demo)
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* 4-Tier Verification Engine Highlight */}
        <div className="mt-12 p-8 rounded-3xl bg-slate-800/40 border border-slate-700/60 backdrop-blur-xl">
          <div className="text-center max-w-xl mx-auto mb-10">
            <span className="text-xs font-mono font-semibold text-amber-400 tracking-wider uppercase">
              Core Innovation
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">
              4-Tier Multi-Modal Credential Verification
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Detects forged certificates, edited recipient names, and duplicate submissions in under 2 seconds.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-3">
                <ShieldCheck size={20} />
              </div>
              <h3 className="text-sm font-bold text-white mb-1">1. SHA-256 Hash Integrity</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Cryptographic document hashing prevents duplicate submissions across student accounts and cross-college plagiarism.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
                <Award size={20} />
              </div>
              <h3 className="text-sm font-bold text-white mb-1">2. QR Authority Decoding</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Automatically extracts and validates embedded verification QR codes against recognized institutional domains (AWS, Coursera, NPTEL).
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-3">
                <FileSearch size={20} />
              </div>
              <h3 className="text-sm font-bold text-white mb-1">3. OCR & Name Match</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Parses recipient entities, dates, and credential IDs. Employs fuzzy string distance to ensure certificate matches registered profile.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center mb-3">
                <Fingerprint size={20} />
              </div>
              <h3 className="text-sm font-bold text-white mb-1">4. Forensic ELA & Tamper</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Error Level Analysis (ELA) detects compression discontinuities when names are pasted over existing certs. Checks PDF authoring metadata.
              </p>
            </div>

          </div>
        </div>

        {/* Demo Flow Checklist */}
        <div className="mt-12 text-center">
          <p className="text-xs text-slate-400 font-mono">
            Hackathon Judge Demo Flow: Student → Parse Resume → Verify Certificate → View Gold Badge → Explainable Match Score → 4-Week Roadmap → Hinglish AI Bot
          </p>
        </div>

      </div>
    </div>
  );
};
