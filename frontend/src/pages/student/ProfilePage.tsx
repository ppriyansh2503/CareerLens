import React, { useEffect, useState } from "react";
import { profileAPI } from "../../lib/api";
import { StudentProfile } from "../../lib/types";
import { TrustBadge } from "../../components/verification/TrustBadge";
import { 
  User, 
  Mail, 
  GraduationCap, 
  Github, 
  Linkedin, 
  Globe, 
  Award, 
  ShieldCheck, 
  CheckCircle2, 
  Edit3, 
  Save, 
  FileText,
  ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form Fields
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [department, setDepartment] = useState("");
  const [cgpa, setCgpa] = useState<number>(8.0);
  const [gradYear, setGradYear] = useState<number>(2026);

  const loadProfile = async () => {
    try {
      const data = await profileAPI.getStudentProfile();
      setProfile(data);
      setHeadline(data.headline || "");
      setBio(data.bio || "");
      setGithubUrl(data.github_url || "");
      setLinkedinUrl(data.linkedin_url || "");
      setPortfolioUrl(data.portfolio_url || "");
      setDepartment(data.department || "Computer Science");
      setCgpa(data.cgpa || 8.0);
      setGradYear(data.graduation_year || 2026);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    try {
      const updated = await profileAPI.updateStudentProfile({
        headline,
        bio,
        github_url: githubUrl,
        linkedin_url: linkedinUrl,
        portfolio_url: portfolioUrl,
        department,
        cgpa: Number(cgpa),
        graduation_year: Number(gradYear)
      });
      setProfile(updated);
      setEditing(false);
      setSuccessMsg("Profile successfully updated!");
      setTimeout(() => setSuccessMsg(null), 3500);
    } catch (err) {
      alert("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center">
        <div className="w-10 h-10 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mb-3" />
        <p className="text-slate-400 text-xs">Loading student profile...</p>
      </div>
    );
  }

  if (!profile) return null;

  const verifiedSkills = profile.skills.filter(s => s.is_verified);
  const unverifiedSkills = profile.skills.filter(s => !s.is_verified);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <User className="text-indigo-400" size={24} />
            <h1 className="text-2xl sm:text-3xl font-bold text-white">Student Profile</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Manage your academic credentials, verified skills, and career portfolio links
          </p>
        </div>

        <button
          onClick={() => setEditing(!editing)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-colors ${
            editing
              ? "bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700"
              : "bg-indigo-600 text-white hover:bg-indigo-500 shadow-md shadow-indigo-600/20"
          }`}
        >
          <Edit3 size={14} />
          <span>{editing ? "Cancel Editing" : "Edit Profile Details"}</span>
        </button>
      </div>

      {successMsg && (
        <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Profile Info Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/40 border border-slate-700/80 shadow-2xl space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-6 pb-6 border-b border-slate-700/60">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-2xl font-extrabold text-white shadow-xl shadow-indigo-500/20">
              {profile.full_name ? profile.full_name.charAt(0) : "S"}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-white">{profile.full_name}</h2>
                <TrustBadge tier="GOLD" size="sm" />
              </div>
              <p className="text-xs text-indigo-300 font-medium mt-0.5">{profile.headline}</p>
              <div className="flex items-center gap-2 mt-1 text-xs text-slate-400">
                <Mail size={13} className="text-slate-500" />
                <span>{profile.email}</span>
                <span>•</span>
                <span>🏛️ {profile.college_name}</span>
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono uppercase">Readiness Index</div>
            <div className="text-3xl font-black bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
              {profile.placement_readiness_score}%
            </div>
          </div>
        </div>

        {/* Edit Form or View Details */}
        {editing ? (
          <form onSubmit={handleSave} className="space-y-4 pt-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Profile Headline</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  placeholder="e.g. Cloud & Distributed Systems Enthusiast"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">CGPA (10 pt scale)</label>
                <input
                  type="number"
                  step="0.1"
                  value={cgpa}
                  onChange={(e) => setCgpa(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Graduation Year</label>
                <input
                  type="number"
                  value={gradYear}
                  onChange={(e) => setGradYear(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">GitHub URL</label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">LinkedIn URL</label>
                <input
                  type="url"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  placeholder="https://linkedin.com/in/..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Bio / Career Objective</label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Briefly describe your specialization, notable accomplishments, and target roles..."
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500 resize-none"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                <Save size={14} />
                <span>{saving ? "Saving..." : "Save Profile Changes"}</span>
              </button>
            </div>
          </form>
        ) : (
          <div className="space-y-4 pt-2 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div>
                <span className="text-slate-500 block uppercase font-mono text-[10px]">Department</span>
                <span className="font-semibold text-slate-200">{profile.department}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-mono text-[10px]">Graduation</span>
                <span className="font-semibold text-slate-200">Class of {profile.graduation_year}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-mono text-[10px]">CGPA</span>
                <span className="font-semibold text-slate-200">{profile.cgpa} / 10.0</span>
              </div>
            </div>

            {profile.bio && (
              <p className="text-slate-300 leading-relaxed bg-slate-900/40 p-4 rounded-2xl border border-slate-800/80">
                {profile.bio}
              </p>
            )}

            <div className="flex flex-wrap gap-3 pt-2">
              {profile.github_url && (
                <a
                  href={profile.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 hover:text-white hover:bg-slate-700 transition-colors"
                >
                  <Github size={14} />
                  <span>GitHub</span>
                </a>
              )}
              {profile.linkedin_url && (
                <a
                  href={profile.linkedin_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 hover:text-white hover:bg-slate-700 transition-colors"
                >
                  <Linkedin size={14} />
                  <span>LinkedIn</span>
                </a>
              )}
              {profile.portfolio_url && (
                <a
                  href={profile.portfolio_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 hover:text-white hover:bg-slate-700 transition-colors"
                >
                  <Globe size={14} />
                  <span>Portfolio</span>
                </a>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Verified Skills & Certificates Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Verified Skills */}
        <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="text-emerald-400" size={18} />
              <h3 className="text-base font-bold text-white">Verified Competencies ({verifiedSkills.length})</h3>
            </div>
            <Link
              to="/student/certificates"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              <span>Verify Skills</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="flex flex-wrap gap-2">
            {verifiedSkills.length > 0 ? (
              verifiedSkills.map((sk) => (
                <span
                  key={sk.id}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/40"
                >
                  <CheckCircle2 size={12} className="text-emerald-400" />
                  <span>{sk.name}</span>
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-400">No verified skills yet. Upload a certificate to verify skills!</span>
            )}
          </div>
        </div>

        {/* Verified Certificates */}
        <div className="p-6 rounded-3xl bg-slate-800/40 border border-slate-700/60 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Award className="text-amber-400" size={18} />
              <h3 className="text-base font-bold text-white">Registered Credentials ({profile.certificates.length})</h3>
            </div>
            <Link
              to="/student/certificates"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              <span>Add Credential</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          <div className="space-y-2">
            {profile.certificates.length > 0 ? (
              profile.certificates.map((c) => (
                <div key={c.id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-white">{c.title}</div>
                    <div className="text-[11px] text-slate-400">{c.issuing_org}</div>
                  </div>
                  <TrustBadge tier={c.badge_tier} size="sm" />
                </div>
              ))
            ) : (
              <span className="text-xs text-slate-400">No certificates uploaded yet.</span>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};
