import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
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
  GraduationCap,
  LogIn,
  UserPlus,
  LogOut,
  User as UserIcon
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, role, isAuthenticated, switchRole, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const studentLinks = [
    { name: 'Dashboard', path: '/student/dashboard', icon: BarChart3 },
    { name: 'Profile', path: '/student/profile', icon: UserIcon },
    { name: 'Resume', path: '/student/resume', icon: FileText },
    { name: 'Verify Certificate', path: '/student/certificates', icon: Award, highlight: true },
    { name: 'Internships', path: '/student/jobs', icon: Briefcase },
    { name: 'AI Counselor', path: '/student/chat', icon: MessageSquare },
  ];

  const recruiterLinks = [
    { name: 'Candidate Discovery', path: '/recruiter/dashboard', icon: Users },
    { name: 'Internship Listings', path: '/student/jobs', icon: Briefcase },
  ];

  const collegeLinks = [
    { name: 'Placement Analytics', path: '/college/dashboard', icon: BarChart3 },
  ];

  const adminLinks = [
    { name: 'Admin Console', path: '/admin/dashboard', icon: ShieldCheck, highlight: true },
  ];

  const currentLinks = role === 'platform_admin'
    ? adminLinks
    : (role === 'recruiter' 
      ? recruiterLinks 
      : (role === 'college_admin' ? collegeLinks : (role === 'student' ? studentLinks : [])));

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    navigate('/login');
  };

  const handleDemoSwitch = async (demoRole: 'student' | 'recruiter' | 'college_admin') => {
    await switchRole(demoRole);
    setDropdownOpen(false);
    if (demoRole === 'recruiter') navigate('/recruiter/dashboard');
    else if (demoRole === 'college_admin') navigate('/college/dashboard');
    else navigate('/student/dashboard');
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

          {/* Navigation Links (When Authenticated) */}
          {isAuthenticated && (
            <nav className="hidden lg:flex items-center gap-1">
              {currentLinks.map((item: any) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                      item.highlight && !isActive
                        ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30 hover:bg-amber-500/25'
                        : isActive 
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20' 
                          : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <Icon size={14} className={item.highlight ? 'text-amber-400' : ''} />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          )}

          {/* Right Action: Auth Buttons or User Persona Dropdown */}
          <div className="flex items-center gap-2">
            {!isAuthenticated ? (
              <div className="flex items-center gap-2">
                {/* 1-Click Demo Quick Presets */}
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/20 transition-colors"
                  >
                    <Sparkles size={13} className="text-amber-400 fill-amber-400" />
                    <span className="hidden sm:inline">Demo Presets</span>
                    <ChevronDown size={13} />
                  </button>

                  {dropdownOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-72 rounded-2xl bg-slate-900 border border-slate-700/80 shadow-2xl p-2 z-50 animate-in fade-in"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <div className="px-3 py-1.5 border-b border-slate-800 text-[11px] font-bold text-slate-400">
                        1-Click Hackathon Evaluator Login:
                      </div>
                      <div className="space-y-1 mt-1">
                        <button
                          onClick={() => handleDemoSwitch('student')}
                          className="w-full flex items-center gap-2.5 p-2 rounded-xl text-left hover:bg-slate-800 transition-colors text-xs"
                        >
                          <span className="text-base">👨‍🎓</span>
                          <div>
                            <div className="font-bold text-white">Student: Aarav Sharma</div>
                            <div className="text-[10px] text-amber-400">AWS Gold Badges • 100% Ready</div>
                          </div>
                        </button>

                        <button
                          onClick={() => handleDemoSwitch('recruiter')}
                          className="w-full flex items-center gap-2.5 p-2 rounded-xl text-left hover:bg-slate-800 transition-colors text-xs"
                        >
                          <span className="text-base">💼</span>
                          <div>
                            <div className="font-bold text-white">Recruiter: Sneha Rao</div>
                            <div className="text-[10px] text-indigo-400">TechCorp • Verified Talent Search</div>
                          </div>
                        </button>

                        <button
                          onClick={() => handleDemoSwitch('college_admin')}
                          className="w-full flex items-center gap-2.5 p-2 rounded-xl text-left hover:bg-slate-800 transition-colors text-xs"
                        >
                          <span className="text-base">🏛️</span>
                          <div>
                            <div className="font-bold text-white">College TPO: Dr. Kapoor</div>
                            <div className="text-[10px] text-emerald-400">IIIT Delhi • Batch Readiness</div>
                          </div>
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                <Link
                  to="/login"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors"
                >
                  <LogIn size={13} />
                  <span>Sign In</span>
                </Link>

                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-md shadow-indigo-600/20"
                >
                  <UserPlus size={13} />
                  <span>Register</span>
                </Link>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-700/80 text-left transition-all"
                >
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
                    {user?.full_name ? user.full_name.charAt(0) : 'U'}
                  </div>
                  <div className="hidden sm:block">
                    <div className="text-xs font-bold text-white leading-tight">
                      {user?.full_name}
                    </div>
                    <div className="text-[10px] text-slate-400 capitalize">
                      {role === 'college_admin' ? 'College TPO' : (role === 'platform_admin' ? 'Platform Admin' : role)}
                    </div>
                  </div>
                  <ChevronDown size={13} className="text-slate-400" />
                </button>

                {/* User Dropdown Menu */}
                {dropdownOpen && (
                  <div 
                    className="absolute right-0 mt-2 w-64 rounded-2xl bg-slate-900 border border-slate-700/80 shadow-2xl p-2 z-50 animate-in fade-in"
                  >
                    <div className="px-3 py-2 border-b border-slate-800 text-xs">
                      <div className="font-bold text-white">{user?.full_name}</div>
                      <div className="text-[11px] text-slate-400 truncate">{user?.email}</div>
                      <div className="text-[10px] text-indigo-400 font-mono mt-0.5 uppercase tracking-wider">
                        Role: {role}
                      </div>
                    </div>

                    <div className="py-1 space-y-0.5 border-b border-slate-800 text-xs">
                      {role === 'platform_admin' && (
                        <Link
                          to="/admin/dashboard"
                          onClick={() => setDropdownOpen(false)}
                          className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-indigo-300 hover:text-white hover:bg-indigo-500/10 transition-colors font-medium"
                        >
                          <ShieldCheck size={14} />
                          <span>Admin Console</span>
                        </Link>
                      )}

                      {role === 'student' && (
                        <>
                          <Link
                            to="/student/profile"
                            onClick={() => setDropdownOpen(false)}
                            className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                          >
                            <UserIcon size={14} />
                            <span>My Profile</span>
                          </Link>
                          <Link
                            to="/student/certificates"
                            onClick={() => setDropdownOpen(false)}
                            className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-amber-300 hover:text-white hover:bg-amber-500/10 transition-colors font-medium"
                          >
                            <Award size={14} />
                            <span>Verify Certificates</span>
                          </Link>
                        </>
                      )}

                      {/* Demo Quick Persona Switcher */}
                      <div className="pt-1.5 px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                        Switch Persona (Judge Demo):
                      </div>
                      <button
                        onClick={() => handleDemoSwitch('student')}
                        className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                      >
                        <span>👨‍🎓</span>
                        <span>Student (Aarav Sharma)</span>
                      </button>
                      <button
                        onClick={() => handleDemoSwitch('recruiter')}
                        className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                      >
                        <span>💼</span>
                        <span>Recruiter (Sneha Rao)</span>
                      </button>
                      <button
                        onClick={() => handleDemoSwitch('college_admin')}
                        className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                      >
                        <span>🏛️</span>
                        <span>College TPO (Dr. Kapoor)</span>
                      </button>
                    </div>

                    <div className="pt-1">
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition-colors"
                      >
                        <LogOut size={14} />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};

