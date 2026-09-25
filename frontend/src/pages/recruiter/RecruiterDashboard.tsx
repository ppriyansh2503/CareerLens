import React, { useEffect, useState } from 'react';
import { useAuth } from '../../lib/authContext';
import { recruiterAPI } from '../../lib/api';
import { Candidate } from '../../lib/types';
import { TrustBadge } from '../../components/verification/TrustBadge';
import { 
  Users, 
  Search, 
  Filter, 
  ShieldCheck, 
  CheckCircle2, 
  ExternalLink,
  Award, 
  Building2, 
  Briefcase,
  Sparkles,
  ArrowUpRight,
  AlertTriangle
} from 'lucide-react';

export const RecruiterDashboard: React.FC = () => {
  const { user } = useAuth();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState<any | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [badgeFilter, setBadgeFilter] = useState('ALL');
  const [skillFilter, setSkillFilter] = useState('');

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const data = await recruiterAPI.discoverCandidates({
        badge: badgeFilter !== 'ALL' ? badgeFilter : undefined,
        skill: skillFilter || undefined
      });
      setCandidates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [badgeFilter, skillFilter]);

  const viewCandidateCard = async (studentId: number) => {
    try {
      const card = await recruiterAPI.getCandidateCard(studentId);
      setSelectedCandidate(card);
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = candidates.filter(c => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      c.full_name.toLowerCase().includes(q) ||
      c.college_name.toLowerCase().includes(q) ||
      c.headline.toLowerCase().includes(q) ||
      c.verified_skills.some(s => s.toLowerCase().includes(q))
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Building2 className="text-indigo-400" size={26} />
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              Company Portal: Verified Talent Discovery
            </h1>
          </div>
          <p className="text-sm text-slate-400">
            TechCorp Global Labs • Zero-fraud recruiting powered by 4-tier cryptographic credential audits.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-800/80 px-4 py-2 rounded-2xl border border-slate-700">
          <ShieldCheck size={18} className="text-emerald-400" />
          <span className="text-xs text-slate-300">
            <strong>Fraud Filter:</strong> Active (Unverified claims deprioritized)
          </span>
        </div>
      </div>

      {/* Pending Approval Banner */}
      {user?.approval_status === 'PENDING' && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs sm:text-sm flex items-center gap-3 animate-pulse">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <span className="font-bold">Organization Verification Pending: </span>
            Your recruiter account is awaiting platform admin approval. Job posting and direct candidate contact are in preview mode until verified.
          </div>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60 flex flex-wrap items-center justify-between gap-4">
        
        <div className="relative flex-1 min-w-[260px]">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search verified talent by name, college, or skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Badge Filter */}
        <div className="flex items-center gap-2 text-xs">
          <Award size={14} className="text-amber-400" />
          <span className="text-slate-400 font-medium">Badge Tier:</span>
          {['ALL', 'GOLD', 'SILVER'].map((b) => (
            <button
              key={b}
              onClick={() => setBadgeFilter(b)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                badgeFilter === b 
                  ? (b === 'GOLD' ? 'bg-amber-500 text-slate-950' : 'bg-indigo-600 text-white')
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {b === 'GOLD' ? '🥇 GOLD ONLY' : b}
            </button>
          ))}
        </div>

      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mb-3" />
          <p className="text-slate-400 text-xs">Querying verified candidate registry...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((cand) => (
            <div
              key={cand.student_id}
              className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 hover:border-indigo-500/50 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <TrustBadge tier={cand.highest_badge} size="sm" showDetails />
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    {cand.placement_readiness_score}% Readiness
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white mb-0.5">
                  {cand.full_name}
                </h3>
                <p className="text-xs text-slate-400 mb-2 leading-relaxed">
                  {cand.headline}
                </p>

                <div className="text-[11px] text-slate-400 space-y-1 mb-4">
                  <div>🏛️ {cand.college_name}</div>
                  <div>🎓 {cand.department} ({cand.graduation_year}) • CGPA: <strong className="text-slate-200">{cand.cgpa}</strong></div>
                </div>

                {/* Verified Skills */}
                <div className="space-y-1.5 mb-4">
                  <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 size={12} />
                    <span>Verified Skills ({cand.verified_skills.length}):</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {cand.verified_skills.map((sk, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700/60 flex items-center justify-between">
                <span className="text-xs text-slate-400">
                  {cand.certificates_count} verified certs
                </span>

                <button
                  onClick={() => viewCandidateCard(cand.student_id)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-md shadow-indigo-600/20"
                >
                  <span>Credibility Card</span>
                  <ArrowUpRight size={13} />
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Candidate Credibility Card Modal */}
      {selectedCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-slate-900 border border-slate-700 p-6 sm:p-8 space-y-6">
            
            <div className="flex items-start justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                  RECRUITER CREDIBILITY CARD
                </span>
                <h2 className="text-2xl font-bold text-white mt-1">
                  {selectedCandidate.candidate.full_name}
                </h2>
                <p className="text-xs text-slate-400">
                  {selectedCandidate.candidate.college_name} • {selectedCandidate.candidate.department}
                </p>
              </div>

              <button
                onClick={() => setSelectedCandidate(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-xs">
              <div className="font-semibold text-white mb-1">Credibility Multiplier:</div>
              <p className="text-indigo-300">{selectedCandidate.credibility_multiplier}</p>
            </div>

            {/* Verified Credentials */}
            <div>
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <ShieldCheck className="text-emerald-400" size={16} />
                <span>Audited Institutional Certificates ({selectedCandidate.verified_credentials.length}):</span>
              </h3>
              
              <div className="space-y-2.5">
                {selectedCandidate.verified_credentials.map((c: any) => (
                  <div key={c.id} className="p-3.5 rounded-2xl bg-slate-800/40 border border-slate-700 flex items-center justify-between">
                    <div>
                      <div className="text-xs font-bold text-white">{c.title}</div>
                      <div className="text-[11px] text-slate-400">{c.issuing_org}</div>
                      <div className="text-[10px] font-mono text-slate-500 mt-1 truncate">
                        SHA-256: {c.file_hash_sha256}
                      </div>
                    </div>
                    <div className="text-right">
                      <TrustBadge tier={c.badge_tier} size="sm" />
                      <div className="text-[10px] text-emerald-400 font-mono mt-1">
                        {c.verification_score}% Confirmed
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Candidate Links */}
            <div className="flex flex-wrap gap-3 pt-2">
              {selectedCandidate.candidate.github_url && (
                <a
                  href={selectedCandidate.candidate.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-1.5"
                >
                  <span>GitHub Profile</span>
                  <ExternalLink size={12} />
                </a>
              )}
              {selectedCandidate.candidate.linkedin_url && (
                <a
                  href={selectedCandidate.candidate.linkedin_url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors flex items-center gap-1.5"
                >
                  <span>LinkedIn Profile</span>
                  <ExternalLink size={12} />
                </a>
              )}
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-800">
              <button
                onClick={() => {
                  alert(`Interview invitation dispatched to ${selectedCandidate.candidate.email}!`);
                  setSelectedCandidate(null);
                }}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-600/20"
              >
                1-Click Shortlist & Invite
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
