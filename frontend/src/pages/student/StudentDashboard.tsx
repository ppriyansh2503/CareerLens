import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { profileAPI, jobsAPI } from '../../lib/api';
import { StudentProfile, Job } from '../../lib/types';
import { TrustBadge } from '../../components/verification/TrustBadge';
import { VerificationModal } from '../../components/verification/VerificationModal';
import { ExplainableMatchModal } from '../../components/matching/ExplainableMatchModal';
import { 
  Award, 
  Briefcase, 
  FileText, 
  CheckCircle2, 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  GraduationCap,
  ShieldCheck,
  Search
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCertId, setSelectedCertId] = useState<number | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<any | null>(null);

  useEffect(() => {
    Promise.all([
      profileAPI.getStudentProfile(),
      jobsAPI.getJobs()
    ]).then(([pData, jData]) => {
      setProfile(pData);
      setJobs(jData);
    }).catch(err => console.error(err))
    .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin mb-4" />
        <p className="text-slate-400 text-sm">Loading verified profile...</p>
      </div>
    );
  }

  if (!profile) return null;

  const verifiedSkills = profile.skills.filter(s => s.is_verified);
  const unverifiedSkills = profile.skills.filter(s => !s.is_verified);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Banner / Hero Profile Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950/40 border border-slate-700/80 shadow-2xl relative overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-6 relative z-10">
          
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-3xl font-extrabold text-white shadow-xl shadow-indigo-500/20">
              {profile.full_name ? profile.full_name.charAt(0) : 'A'}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-2xl sm:text-3xl font-bold text-white">
                  {profile.full_name}
                </h1>
                <TrustBadge tier="GOLD" size="sm" />
              </div>
              <p className="text-sm text-slate-300 font-medium">
                {profile.headline || 'Cloud Software Engineer Aspirant'}
              </p>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <GraduationCap size={14} className="text-indigo-400" />
                  {profile.department} ({profile.graduation_year})
                </span>
                <span>•</span>
                <span>CGPA: <strong className="text-slate-200">{profile.cgpa}</strong></span>
                <span>•</span>
                <span className="text-slate-300">{profile.college_name}</span>
              </div>
            </div>
          </div>

          {/* Placement Readiness Gauge */}
          <div className="flex items-center gap-4 bg-slate-800/80 px-6 py-4 rounded-2xl border border-slate-700">
            <div>
              <div className="text-[11px] text-slate-400 font-mono uppercase tracking-wider">
                Placement Readiness
              </div>
              <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1 mt-0.5">
                <TrendingUp size={13} />
                <span>Ready to Place</span>
              </div>
            </div>
            <div className="text-3xl sm:text-4xl font-black bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
              {profile.placement_readiness_score}%
            </div>
          </div>

        </div>
      </div>

      {/* Grid: Verified Credentials & Skills */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Verified Certificates */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Award className="text-amber-400" size={20} />
              <h2 className="text-lg font-bold text-white">Verified Credentials & Badges</h2>
            </div>
            <Link
              to="/student/certificates"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              <span>Upload / Verify</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {profile.certificates.map((cert) => (
              <div 
                key={cert.id}
                className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-indigo-500/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <TrustBadge tier={cert.badge_tier} size="sm" showDetails />
                    <span className="text-[11px] font-mono text-slate-400">
                      Score: <strong className="text-indigo-400">{cert.verification_score}%</strong>
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white mb-1 leading-snug">
                    {cert.title}
                  </h3>
                  <p className="text-xs text-slate-400">
                    Authority: <span className="text-slate-200">{cert.issuing_org}</span>
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between">
                  <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 size={12} />
                    <span>OCR & QR Validated</span>
                  </span>
                  <button
                    onClick={() => setSelectedCertId(cert.id)}
                    className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline underline-offset-2"
                  >
                    Forensic Audit
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Top Internship Matches */}
          <div className="pt-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Briefcase className="text-indigo-400" size={20} />
                <h2 className="text-lg font-bold text-white">Recommended Internships (Explainable Matches)</h2>
              </div>
              <Link
                to="/student/jobs"
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
              >
                <span>View All Jobs</span>
                <ArrowRight size={13} />
              </Link>
            </div>

            <div className="space-y-3">
              {jobs.slice(0, 3).map((job) => (
                <div
                  key={job.id}
                  className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-slate-600 transition-all flex flex-wrap items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-bold text-white">{job.title}</h3>
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {job.job_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      <strong className="text-slate-200">{job.company_name}</strong> • {job.location} • {job.stipend_or_salary}
                    </p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {job.skills.slice(0, 4).map((sk) => (
                        <span key={sk.id} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {sk.name}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-2xl font-black bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
                        {job.match_score || 80}%
                      </div>
                      <div className="text-[10px] text-slate-400 font-medium">{job.match_tier || 'Strong Fit'}</div>
                    </div>

                    <Link
                      to={`/student/jobs`}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-600 hover:text-white transition-colors"
                    >
                      Explain Score
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Extracted Skills & Actions */}
        <div className="space-y-6">
          
          {/* Quick Actions */}
          <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-3">
            <h3 className="text-sm font-bold text-white">Quick Actions</h3>
            
            <Link
              to="/student/resume"
              className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800 hover:bg-slate-700/70 border border-slate-700 transition-colors text-xs font-medium text-slate-200"
            >
              <span className="flex items-center gap-2">
                <FileText size={16} className="text-indigo-400" />
                Upload & Parse Resume
              </span>
              <ArrowRight size={14} className="text-slate-500" />
            </Link>

            <Link
              to="/student/certificates"
              className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-800 hover:bg-slate-700/70 border border-slate-700 transition-colors text-xs font-medium text-slate-200"
            >
              <span className="flex items-center gap-2">
                <Award size={16} className="text-amber-400" />
                Verify New Certificate
              </span>
              <ArrowRight size={14} className="text-slate-500" />
            </Link>

            <Link
              to="/student/chat"
              className="w-full flex items-center justify-between p-3 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 transition-colors text-xs font-medium text-indigo-200"
            >
              <span className="flex items-center gap-2">
                <Sparkles size={16} className="text-indigo-400" />
                Ask AI Career Counselor
              </span>
              <ArrowRight size={14} className="text-indigo-400" />
            </Link>
          </div>

          {/* Extracted & Verified Skills Cloud */}
          <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Candidate Skill Matrix</h3>
              <span className="text-xs text-emerald-400 font-mono">
                {verifiedSkills.length} Verified
              </span>
            </div>

            {/* Verified Skills */}
            <div>
              <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                <ShieldCheck size={13} />
                <span>Verified by Credentials (High Trust):</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {verifiedSkills.map((sk) => (
                  <span
                    key={sk.id}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40"
                  >
                    <CheckCircle2 size={12} className="text-emerald-400" />
                    {sk.name}
                  </span>
                ))}
              </div>
            </div>

            {/* Self-reported / Resume Skills */}
            {unverifiedSkills.length > 0 && (
              <div className="pt-2 border-t border-slate-700/50">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Extracted from Resume (Self-Claimed):
                </div>
                <div className="flex flex-wrap gap-2">
                  {unverifiedSkills.map((sk) => (
                    <span
                      key={sk.id}
                      className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {sk.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

        </div>

      </div>

      {/* Forensic Audit Modal */}
      {selectedCertId && (
        <VerificationModal
          certId={selectedCertId}
          onClose={() => setSelectedCertId(null)}
        />
      )}

      {/* Explainable Match Modal */}
      {selectedMatch && (
        <ExplainableMatchModal
          match={selectedMatch}
          onClose={() => setSelectedMatch(null)}
        />
      )}

    </div>
  );
};
