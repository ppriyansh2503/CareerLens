import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/authContext';
import { 
  ShieldCheck, 
  Briefcase, 
  FileText, 
  Award, 
  MessageSquare, 
  BarChart3, 
  Users, 
  ChevronDown,
  Sparkles,
  GraduationCap
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, role, switchRole } = useAuth();
  const location = useLocation();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const studentLinks = [
    { name: 'Dashboard', path: '/student/dashboard', icon: BarChart3 },
    { name: 'My Resume', path: '/student/resume', icon: FileText },
    { name: 'Verify Certs', path: '/student/certificates', icon: Award },
    { name: 'Internships', path: '/student/jobs', icon: Briefcase },
    { name: 'AI Counselor', path: '/student/chat', icon: MessageSquare },
  ];

  const recruiterLinks = [
    { name: 'Candidate Discovery', path: '/recruiter/dashboard', icon: Users },
  ];

  const collegeLinks = [
    { name: 'Placement Analytics', path: '/college/dashboard', icon: BarChart3 },
  ];

  const currentLinks = role === 'recruiter' 
    ? recruiterLinks 
    : (role === 'college_admin' ? collegeLinks : studentLinks);

  const roleLabels = {
    student: { title: 'Aarav Sharma', subtitle: 'IIIT Student (Gold Badge)', icon: GraduationCap, color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
    recruiter: { title: 'Sneha Rao', subtitle: 'Recruiter @ TechCorp', icon: Briefcase, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30' },
    college_admin: { title: 'Dr. Rajiv Kapoor', subtitle: 'TPO Director @ IIIT', icon: BarChart3, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' }
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
                <ShieldCheck className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  Career<span className="text-indigo-400">Lens</span>
                </span>
                <span className="hidden sm:inline-block ml-2 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider">
                  Verified AI
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {currentLinks.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive 
                      ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30' 
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon size={16} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Demo Role Switcher for Hackathon Judges */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className={`flex items-center gap-3 px-3 py-1.5 rounded-xl border text-left transition-all hover:bg-slate-800 ${roleLabels[role]?.color}`}
            >
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-sm font-bold">
                {role === 'student' ? '👨‍🎓' : (role === 'recruiter' ? '💼' : '🏛️')}
              </div>
              <div className="hidden sm:block">
                <div className="text-xs font-semibold leading-tight text-white flex items-center gap-1">
                  {roleLabels[role]?.title}
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 font-mono">DEMO</span>
                </div>
                <div className="text-[10px] text-slate-400 leading-tight">
                  {roleLabels[role]?.subtitle}
                </div>
              </div>
              <ChevronDown size={14} className="text-slate-400" />
            </button>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <div 
                className="absolute right-0 mt-2 w-72 rounded-2xl bg-slate-900 border border-slate-700/80 shadow-2xl p-2 z-50 animate-in fade-in slide-in-from-top-2"
                onClick={() => setDropdownOpen(false)}
              >
                <div className="px-3 py-2 border-b border-slate-800">
                  <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <Sparkles size={13} className="text-indigo-400" />
                    <span>Instant Demo Role Switcher</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">Switch perspective for hackathon evaluation</p>
                </div>

                <div className="space-y-1 mt-1">
                  <button
                    onClick={() => switchRole('student')}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                      role === 'student' ? 'bg-amber-500/15 border border-amber-500/30' : 'hover:bg-slate-800'
                    }`}
                  >
                    <span className="text-xl">👨‍🎓</span>
                    <div>
                      <div className="text-xs font-semibold text-white">Student View (Aarav Sharma)</div>
                      <div className="text-[11px] text-amber-300/80">AWS Gold Badge • Resume • Match Engine</div>
                    </div>
                  </button>

                  <button
                    onClick={() => switchRole('recruiter')}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                      role === 'recruiter' ? 'bg-indigo-500/15 border border-indigo-500/30' : 'hover:bg-slate-800'
                    }`}
                  >
                    <span className="text-xl">💼</span>
                    <div>
                      <div className="text-xs font-semibold text-white">Recruiter View (Sneha Rao)</div>
                      <div className="text-[11px] text-indigo-300/80">TechCorp • Verified Talent Discovery</div>
                    </div>
                  </button>

                  <button
                    onClick={() => switchRole('college_admin')}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                      role === 'college_admin' ? 'bg-emerald-500/15 border border-emerald-500/30' : 'hover:bg-slate-800'
                    }`}
                  >
                    <span className="text-xl">🏛️</span>
                    <div>
                      <div className="text-xs font-semibold text-white">College TPO View (Dr. Kapoor)</div>
                      <div className="text-[11px] text-emerald-300/80">Placement Readiness • Skill Gap Heatmaps</div>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};
