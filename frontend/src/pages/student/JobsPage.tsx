import React, { useEffect, useState } from 'react';
import { jobsAPI, matchingAPI } from '../../lib/api';
import { Job, ExplainableMatch } from '../../lib/types';
import { ExplainableMatchModal } from '../../components/matching/ExplainableMatchModal';
import { 
  Briefcase, 
  MapPin, 
  Banknote, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Search,
  Filter
} from 'lucide-react';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState<ExplainableMatch | null>(null);
  const [matchLoading, setMatchLoading] = useState<number | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [tierFilter, setTierFilter] = useState('ALL');

  useEffect(() => {
    jobsAPI.getJobs()
      .then(data => {
        setJobs(data);
        setFilteredJobs(data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let result = jobs;
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(j => 
        j.title.toLowerCase().includes(q) || 
        j.company_name.toLowerCase().includes(q) ||
        j.skills.some(s => s.name.toLowerCase().includes(q))
      );
    }
    if (tierFilter !== 'ALL') {
      result = result.filter(j => (j.match_tier || '').toUpperCase() === tierFilter.toUpperCase());
    }
    setFilteredJobs(result);
  }, [search, tierFilter, jobs]);

  const handleOpenMatch = async (jobId: number) => {
    setMatchLoading(jobId);
    try {
      const matchData = await matchingAPI.getExplainableMatch(jobId);
      setSelectedMatch(matchData);
    } catch (err) {
      console.error(err);
    } finally {
      setMatchLoading(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Briefcase className="text-indigo-400" size={24} />
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            Internship Matches & Explainable Fit
          </h1>
        </div>
        <p className="text-sm text-slate-400">
          Ranked dynamically for your profile. High scores reward verified credentials with proof of competence.
        </p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-800/40 border border-slate-700/60">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by role, company, or skill (e.g. AWS, Python, React)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <Filter size={14} className="text-slate-400" />
          <span className="text-slate-400 font-medium">Match Fit:</span>
          {['ALL', 'Strong Fit', 'Moderate Fit'].map((tier) => (
            <button
              key={tier}
              onClick={() => setTierFilter(tier)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                tierFilter === tier 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Jobs Feed */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mb-3" />
          <p className="text-slate-400 text-xs">Calculating match scores against verified profile...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <div
              key={job.id}
              className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 hover:border-indigo-500/40 transition-all flex flex-wrap items-center justify-between gap-6"
            >
              <div className="space-y-2 flex-1 min-w-[280px]">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-white">{job.title}</h3>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-medium">
                    {job.job_type}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
                  <span className="text-indigo-300 font-semibold">{job.company_name}</span>
                  <span className="flex items-center gap-1">
                    <MapPin size={13} className="text-slate-500" />
                    {job.location}
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <Banknote size={13} />
                    {job.stipend_or_salary}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed pt-1">
                  {job.description}
                </p>

                {/* Skill Pills */}
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {job.skills.map((sk) => (
                    <span
                      key={sk.id}
                      className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800/90 text-slate-300 border border-slate-700"
                    >
                      {sk.name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Match Score & CTA */}
              <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-3 border-t sm:border-t-0 sm:border-l border-slate-700/60 pt-4 sm:pt-0 sm:pl-6 w-full sm:w-auto">
                <div className="text-left sm:text-right">
                  <div className="text-3xl font-black bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
                    {job.match_score || 80}%
                  </div>
                  <div className="text-[11px] font-semibold text-indigo-300">
                    {job.match_tier || 'Strong Fit'}
                  </div>
                </div>

                <button
                  onClick={() => handleOpenMatch(job.id)}
                  disabled={matchLoading === job.id}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors shadow-md shadow-indigo-600/20"
                >
                  <Sparkles size={14} />
                  <span>{matchLoading === job.id ? 'Analyzing...' : 'Explain Score & Gap'}</span>
                </button>
              </div>

            </div>
          ))}

          {filteredJobs.length === 0 && (
            <div className="py-16 text-center text-slate-400 text-xs">
              No matching internship roles found for this query.
            </div>
          )}
        </div>
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
