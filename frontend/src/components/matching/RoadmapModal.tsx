import React, { useEffect, useState } from 'react';
import { matchingAPI } from '../../lib/api';
import { Roadmap } from '../../lib/types';
import { 
  X, 
  Sparkles, 
  Calendar, 
  CheckSquare, 
  BookOpen, 
  Trophy, 
  ArrowUpRight,
  TrendingUp
} from 'lucide-react';

interface RoadmapModalProps {
  jobId: number;
  jobTitle: string;
  onClose: () => void;
}

export const RoadmapModal: React.FC<RoadmapModalProps> = ({ jobId, jobTitle, onClose }) => {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    matchingAPI.getRoadmap(jobId)
      .then(data => setRoadmap(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [jobId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in">
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-3xl bg-slate-900 border border-indigo-500/40 shadow-2xl p-6 sm:p-8">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X size={20} />
        </button>

        {loading ? (
          <div className="py-24 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin mb-4" />
            <p className="text-slate-300 font-medium">Synthesizing personalized 4-week roadmap via Gemini AI...</p>
            <p className="text-slate-500 text-xs mt-1">Analyzing skill gaps and curating project milestones</p>
          </div>
        ) : roadmap ? (
          <div>
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
              <div>
                <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-full bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/30">
                  AI-GENERATED SKILL ROADMAP
                </span>
                <h2 className="text-2xl font-bold text-white mt-2">
                  4-Week Accelerated Sprint: {roadmap.target_role}
                </h2>
                <p className="text-sm text-slate-400 mt-0.5">{roadmap.summary}</p>
              </div>

              {/* Score Uplift Banner */}
              <div className="flex items-center gap-4 bg-slate-800/80 px-5 py-3 rounded-2xl border border-slate-700">
                <div>
                  <div className="text-[11px] text-slate-400 uppercase font-mono">Current</div>
                  <div className="text-xl font-bold text-slate-300">{roadmap.current_match_score}%</div>
                </div>
                <div className="flex items-center gap-1 text-emerald-400 font-bold text-sm">
                  <TrendingUp size={16} />
                  <span>+20%</span>
                </div>
                <div>
                  <div className="text-[11px] text-emerald-400 uppercase font-mono">Projected</div>
                  <div className="text-xl font-bold text-emerald-400">{roadmap.projected_match_score}%</div>
                </div>
              </div>
            </div>

            {/* Timeline Weeks */}
            <div className="space-y-6">
              {roadmap.weeks.map((week) => (
                <div 
                  key={week.week_number}
                  className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-indigo-500/40 transition-colors"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center justify-center text-sm font-bold font-mono">
                        W{week.week_number}
                      </div>
                      <div>
                        <h4 className="text-base font-bold text-white">{week.theme}</h4>
                        <p className="text-xs text-slate-400">{week.goal}</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-700/50">
                    
                    {/* Action Items */}
                    <div>
                      <div className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                        <CheckSquare size={13} className="text-indigo-400" />
                        <span>Actionable Tasks</span>
                      </div>
                      <ul className="space-y-1.5">
                        {week.action_items.map((item, idx) => (
                          <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                            <span className="text-indigo-400 mt-0.5">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Resources & Milestone Project */}
                    <div className="space-y-3">
                      <div>
                        <div className="text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
                          <BookOpen size={13} className="text-cyan-400" />
                          <span>Curated Resources</span>
                        </div>
                        <ul className="space-y-1">
                          {week.recommended_resources.map((res, idx) => (
                            <li key={idx} className="text-xs text-slate-400 flex items-center gap-1.5">
                              <ArrowUpRight size={12} className="text-cyan-400" />
                              <span>{res}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/25">
                        <div className="text-[11px] font-semibold text-amber-400 flex items-center gap-1.5">
                          <Trophy size={13} />
                          <span>Milestone Deliverable:</span>
                        </div>
                        <p className="text-xs text-white font-medium mt-0.5">
                          {week.milestone_project}
                        </p>
                      </div>
                    </div>

                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={onClose}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 transition-colors"
              >
                Close & Start Sprint
              </button>
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
};
