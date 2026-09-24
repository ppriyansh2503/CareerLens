import React, { useEffect, useState } from 'react';
import { collegeAPI } from '../../lib/api';
import { CollegeAnalytics } from '../../lib/types';
import { TrustBadge } from '../../components/verification/TrustBadge';
import { 
  BarChart3, 
  ShieldCheck, 
  GraduationCap, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle2, 
  Users, 
  Award,
  Layers,
  FileSpreadsheet
} from 'lucide-react';

export const CollegeDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<CollegeAnalytics | null>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      collegeAPI.getAnalytics(),
      collegeAPI.getStudents()
    ]).then(([aData, sData]) => {
      setAnalytics(aData);
      setStudents(sData);
    }).catch(err => console.error(err))
    .finally(() => setLoading(false));
  }, []);

  if (loading || !analytics) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center">
        <div className="w-10 h-10 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mb-3" />
        <p className="text-slate-400 text-xs">Aggregating batch placement readiness metrics...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <GraduationCap className="text-emerald-400" size={26} />
            <h1 className="text-2xl sm:text-3xl font-bold text-white">
              Institutional Placement & Readiness Portal
            </h1>
          </div>
          <p className="text-sm text-slate-400">
            {analytics.institution_name} • {analytics.academic_year} • Training & Placement Cell (TPO)
          </p>
        </div>

        <button
          onClick={() => alert('Placement readiness report exported to PDF/CSV!')}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 transition-colors"
        >
          <FileSpreadsheet size={14} className="text-emerald-400" />
          <span>Export TPO Report</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* Placement Readiness */}
        <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-2">
          <div className="text-xs text-slate-400 font-medium">Batch Placement Readiness</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {analytics.average_readiness_score}%
            </span>
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-0.5">
              <TrendingUp size={12} />
              +14% YoY
            </span>
          </div>
          <p className="text-[11px] text-slate-500">
            {analytics.placement_readiness_distribution.placement_ready_students} students currently meet hiring benchmarks.
          </p>
        </div>

        {/* Verified Credentials */}
        <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-2">
          <div className="text-xs text-slate-400 font-medium">Verified Credentials Audited</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-amber-400">
              {analytics.verification_metrics.total_certificates_audited}
            </span>
            <span className="text-xs text-amber-400/80 font-mono">
              ({analytics.verification_metrics.gold_badges_awarded} Gold)
            </span>
          </div>
          <p className="text-[11px] text-slate-500">
            Authentic certificates verified via OCR & QR signatures.
          </p>
        </div>

        {/* Fraud Prevention Rate */}
        <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-2">
          <div className="text-xs text-slate-400 font-medium">Credential Integrity Index</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-indigo-400">
              {analytics.verification_metrics.fraud_prevention_rate}
            </span>
          </div>
          <p className="text-[11px] text-rose-400 flex items-center gap-1">
            <AlertCircle size={12} />
            <span>{analytics.verification_metrics.flagged_tampered_submissions} tampered submissions caught</span>
          </p>
        </div>

        {/* Total Enrolled */}
        <div className="p-5 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-2">
          <div className="text-xs text-slate-400 font-medium">Active Batch Size</div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {analytics.total_enrolled_students}
            </span>
            <span className="text-xs text-slate-400 font-mono">Students</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Across CSE, IT, Data Science and AI branches.
          </p>
        </div>

      </div>

      {/* Grid: Top Verified Skills vs Batch Deficits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Top Verified Skills */}
        <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
          <div className="flex items-center gap-2">
            <Award className="text-amber-400" size={18} />
            <h3 className="text-base font-bold text-white">Batch Core Competency Strengths</h3>
          </div>

          <div className="space-y-3">
            {analytics.top_verified_skills.map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-200">{item.skill}</span>
                  <span className="text-emerald-400 font-mono">{item.verified_students} Verified Students</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500"
                    style={{ width: `${Math.min(100, item.verified_students * 40)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Batch Skill Deficits (Actionable for College Curriculum) */}
        <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="text-rose-400" size={18} />
            <h3 className="text-base font-bold text-white">Critical Batch Skill Deficits</h3>
          </div>
          <p className="text-xs text-slate-400">
            Identified by comparing active student verified skills against live recruiter job requirements.
          </p>

          <div className="space-y-3">
            {analytics.top_skill_deficits.map((deficit, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-white">{deficit.skill}</div>
                  <div className="text-[11px] text-slate-400">
                    Industry Demand: <strong className="text-amber-400">{deficit.industry_demand}</strong>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-mono font-bold text-rose-400">
                    {deficit.students_missing_percentage}% Missing
                  </div>
                  <div className="text-[10px] text-slate-500">Requires Lab Workshop</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Student Roster Table */}
      <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Users className="text-indigo-400" size={18} />
          <span>Batch Students Credential Status</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">Department</th>
                <th className="py-3 px-4">CGPA</th>
                <th className="py-3 px-4">Trust Badge</th>
                <th className="py-3 px-4">Verified Skills</th>
                <th className="py-3 px-4 text-right">Readiness Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {students.map((st) => (
                <tr key={st.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">
                    {st.full_name}
                  </td>
                  <td className="py-3 px-4 text-slate-400">
                    {st.department}
                  </td>
                  <td className="py-3 px-4 font-mono font-medium text-slate-200">
                    {st.cgpa}
                  </td>
                  <td className="py-3 px-4">
                    <TrustBadge tier={st.highest_badge} size="sm" />
                  </td>
                  <td className="py-3 px-4 font-mono text-emerald-400">
                    {st.verified_skills_count} verified
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-white font-mono">
                    {st.placement_readiness_score}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
