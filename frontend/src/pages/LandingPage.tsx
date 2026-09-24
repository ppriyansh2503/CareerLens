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

          {/* Quick Demo CTA */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/student/dashboard"
              className="flex items-center gap-2 px-7 py-3 rounded-2xl bg-indigo-600 text-white font-semibold text-sm shadow-xl shadow-indigo-500/25 hover:bg-indigo-500 transition-all hover:scale-105"
            >
              <span>Explore Student Portal</span>
              <ArrowRight size={16} />
            </Link>

            <Link
              to="/recruiter/dashboard"
              onClick={() => switchRole('recruiter')}
              className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-slate-800/90 text-slate-200 border border-slate-700 font-semibold text-sm hover:bg-slate-700 transition-all"
            >
              <span>Recruiter Discovery</span>
            </Link>

            <Link
              to="/college/dashboard"
              onClick={() => switchRole('college_admin')}
              className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-slate-800/90 text-slate-200 border border-slate-700 font-semibold text-sm hover:bg-slate-700 transition-all"
            >
              <span>College TPO Analytics</span>
            </Link>
          </div>

          <div className="mt-6 text-xs text-slate-500 flex items-center justify-center gap-4">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 size={13} className="text-emerald-400" />
              100% Pre-Seeded Hackathon Demo
            </span>
            <span className="flex items-center gap-1.5">
              <Globe2 size={13} className="text-indigo-400" />
              English + Hindi + Hinglish
            </span>
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
