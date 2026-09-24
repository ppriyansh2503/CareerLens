import React, { useState } from 'react';
import { ExplainableMatch } from '../../lib/types';
import { RoadmapModal } from './RoadmapModal';
import { 
  X, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  PlusCircle, 
  ArrowRight,
  ShieldCheck,
  GraduationCap,
  FolderGit2
} from 'lucide-react';

interface ExplainableMatchModalProps {
  match: ExplainableMatch | null;
  onClose: () => void;
}

export const ExplainableMatchModal: React.FC<ExplainableMatchModalProps> = ({ match, onClose }) => {
  const [showRoadmap, setShowRoadmap] = useState(false);

  if (!match) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
        <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-3xl bg-slate-900 border border-slate-700/80 shadow-2xl p-6 sm:p-8">
          
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-6 right-6 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X size={20} />
          </button>

          {/* Header */}
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
            <div>
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                EXPLAINABLE MATCH ENGINE
              </span>
              <h2 className="text-2xl font-bold text-white mt-1">
                {match.job_title}
              </h2>
              <p className="text-sm text-slate-400">
                Company: <span className="text-indigo-400 font-medium">{match.company_name}</span>
              </p>
            </div>

            <div className="flex items-center gap-3 bg-slate-800/80 px-4 py-2 rounded-2xl border border-slate-700">
              <div className="text-right">
                <div className="text-xs text-slate-400 font-medium">Match Fit</div>
                <div className="text-xs font-semibold text-indigo-300">{match.match_tier}</div>
              </div>
              <div className="text-3xl font-extrabold bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
                {match.overall_score}%
              </div>
            </div>
          </div>

          {/* Verdict Banner */}
          <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-200 mb-6">
            <div className="flex items-start gap-3">
              <Sparkles size={20} className="text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-semibold text-white">Why did you get this score?</div>
                <p className="text-xs mt-0.5 leading-relaxed text-slate-300">
                  {match.readiness_verdict}
                </p>
                <p className="text-xs mt-1.5 font-medium text-emerald-400">
                  💡 Recommendation: {match.recommended_action}
                </p>
              </div>
            </div>
          </div>

          {/* Transparent Score Breakdown (Mathematical Decomposition) */}
          <div className="mb-6">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-3">
              Transparent Score Breakdown
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              
              {/* Verified Skills */}
              <div className="p-3.5 rounded-2xl bg-slate-800/50 border border-emerald-500/20">
                <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold mb-1">
                  <ShieldCheck size={14} />
                  <span>Verified Skills</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {match.score_breakdown.verified_skills_component}
                  <span className="text-xs text-slate-400 font-normal"> / 45 pts</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Backed by certified proof</div>
              </div>

              {/* Unverified Skills */}
              <div className="p-3.5 rounded-2xl bg-slate-800/50 border border-slate-700/60">
                <div className="flex items-center gap-1.5 text-xs text-amber-400 font-semibold mb-1">
                  <FolderGit2 size={14} />
                  <span>Resume Skills</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {match.score_breakdown.unverified_skills_component}
                  <span className="text-xs text-slate-400 font-normal"> / 20 pts</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Self-claimed on resume</div>
              </div>

              {/* Academic Fit */}
              <div className="p-3.5 rounded-2xl bg-slate-800/50 border border-slate-700/60">
                <div className="flex items-center gap-1.5 text-xs text-cyan-400 font-semibold mb-1">
                  <GraduationCap size={14} />
                  <span>Academic Fit</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {match.score_breakdown.academic_fit_component}
                  <span className="text-xs text-slate-400 font-normal"> / 15 pts</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Degree, Department, CGPA</div>
              </div>

              {/* Project Depth */}
              <div className="p-3.5 rounded-2xl bg-slate-800/50 border border-slate-700/60">
                <div className="flex items-center gap-1.5 text-xs text-purple-400 font-semibold mb-1">
                  <Sparkles size={14} />
                  <span>Credential Depth</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {match.score_breakdown.project_fit_component}
                  <span className="text-xs text-slate-400 font-normal"> / 20 pts</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-1">Portfolio & verified badges</div>
              </div>

            </div>
          </div>

          {/* Skill Analysis Pills */}
          <div className="space-y-4 mb-6">
            
            {/* Matched Verified */}
            <div>
              <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 mb-2">
                <CheckCircle2 size={14} />
                <span>Verified Core Skills (High Credibility Multiplier):</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {match.skill_analysis.matched_verified_skills.length > 0 ? (
                  match.skill_analysis.matched_verified_skills.map((sk) => (
                    <span
                      key={sk}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40"
                    >
                      <ShieldCheck size={12} className="text-emerald-400" />
                      {sk} (Verified)
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">None verified yet</span>
                )}
              </div>
            </div>

            {/* Matched Unverified */}
            {match.skill_analysis.matched_unverified_skills.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-amber-400 flex items-center gap-1.5 mb-2">
                  <FolderGit2 size={14} />
                  <span>Matched from Resume (Unverified - lower weight):</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {match.skill_analysis.matched_unverified_skills.map((sk) => (
                    <span
                      key={sk}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30"
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Critical Skills */}
            <div>
              <div className="text-xs font-semibold text-rose-400 flex items-center gap-1.5 mb-2">
                <XCircle size={14} />
                <span>Missing Critical Skills (Target these to reach 90%+ match):</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {match.skill_analysis.missing_critical_skills.length > 0 ? (
                  match.skill_analysis.missing_critical_skills.map((sk) => (
                    <span
                      key={sk}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-rose-500/15 text-rose-300 border border-rose-500/40"
                    >
                      <XCircle size={12} className="text-rose-400" />
                      {sk}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-emerald-400 font-semibold">
                    Awesome! You have met all mandatory requirements!
                  </span>
                )}
              </div>
            </div>

            {/* Bonus Skills */}
            {match.skill_analysis.bonus_skills.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-cyan-400 flex items-center gap-1.5 mb-2">
                  <PlusCircle size={14} />
                  <span>Bonus Skills (Differentiators on your profile):</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {match.skill_analysis.bonus_skills.map((sk) => (
                    <span
                      key={sk}
                      className="px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30"
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Action Footer */}
          <div className="flex items-center justify-between border-t border-slate-800 pt-6">
            <button
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Close
            </button>

            <button
              onClick={() => setShowRoadmap(true)}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-600 hover:to-purple-700 transition-all hover:scale-[1.02]"
            >
              <span>Bridge Gap: 4-Week Roadmap</span>
              <ArrowRight size={16} />
            </button>
          </div>

        </div>
      </div>

      {showRoadmap && (
        <RoadmapModal
          jobId={match.job_id}
          jobTitle={match.job_title}
          onClose={() => setShowRoadmap(false)}
        />
      )}
    </>
  );
};
