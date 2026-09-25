import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, 
  ShieldAlert, 
  Users, 
  Building2, 
  GraduationCap, 
  Award, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  FileText, 
  RefreshCw, 
  Eye, 
  Search,
  ExternalLink,
  ChevronRight,
  Shield,
  Layers,
  History
} from "lucide-react";
import { adminAPI, extractErrorMessage } from "../../lib/api";
import { 
  PlatformStats, 
  CertificateReviewItem, 
  UserApprovalItem, 
  AuditLogItem 
} from "../../lib/types";

export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"reviews" | "students" | "recruiters" | "colleges" | "audit">("reviews");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Real backend datasets
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [certificates, setCertificates] = useState<CertificateReviewItem[]>([]);
  const [students, setStudents] = useState<UserApprovalItem[]>([]);
  const [recruiters, setRecruiters] = useState<UserApprovalItem[]>([]);
  const [colleges, setColleges] = useState<UserApprovalItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);

  // Selected certificate for deep inspection & review modal
  const [selectedCert, setSelectedCert] = useState<CertificateReviewItem | null>(null);
  const [reviewReason, setReviewReason] = useState("");
  const [submittingAction, setSubmittingAction] = useState(false);

  // Action modal for user approval (student, recruiter, college)
  const [userActionModal, setUserActionModal] = useState<{
    type: "student" | "recruiter" | "college";
    user: UserApprovalItem;
    action: "APPROVE" | "REJECT";
  } | null>(null);
  const [userActionReason, setUserActionReason] = useState("");

  const fetchData = async () => {
    try {
      setError(null);
      const [statsData, certsData, studentsData, recsData, colsData, logsData] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.listPendingCertificates(),
        adminAPI.listStudents(),
        adminAPI.listRecruiters(),
        adminAPI.listColleges(),
        adminAPI.getAuditLogs()
      ]);
      setStats(statsData);
      setCertificates(certsData);
      setStudents(studentsData);
      setRecruiters(recsData);
      setColleges(colsData);
      setAuditLogs(logsData);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to load platform administration metrics."));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleCertificateReview = async (action: "APPROVE" | "REJECT") => {
    if (!selectedCert) return;
    if (action === "REJECT" && !reviewReason.trim()) {
      setError("Please provide a mandatory reason for certificate rejection.");
      return;
    }

    setSubmittingAction(true);
    setError(null);
    try {
      await adminAPI.reviewCertificate(selectedCert.id, action, reviewReason.trim());
      setSuccessMsg(`Certificate ${action === "APPROVE" ? "approved" : "rejected"} successfully.`);
      setSelectedCert(null);
      setReviewReason("");
      fetchData();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to update certificate review status."));
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleUserApproval = async () => {
    if (!userActionModal) return;
    if (userActionModal.action === "REJECT" && !userActionReason.trim()) {
      setError("Please provide a mandatory reason for account rejection.");
      return;
    }

    setSubmittingAction(true);
    setError(null);
    try {
      if (userActionModal.type === "student") {
        await adminAPI.reviewStudent(userActionModal.user.id, userActionModal.action, userActionReason.trim());
        setSuccessMsg(`Student account ${userActionModal.user.full_name} ${userActionModal.action.toLowerCase()}ed.`);
      } else if (userActionModal.type === "recruiter") {
        await adminAPI.reviewRecruiter(userActionModal.user.id, userActionModal.action, userActionReason.trim());
        setSuccessMsg(`Recruiter ${userActionModal.user.company_name || userActionModal.user.full_name} ${userActionModal.action.toLowerCase()}ed.`);
      } else {
        await adminAPI.reviewCollege(userActionModal.user.id, userActionModal.action, userActionReason.trim());
        setSuccessMsg(`Institution ${userActionModal.user.college_name || userActionModal.user.full_name} ${userActionModal.action.toLowerCase()}ed.`);
      }
      setUserActionModal(null);
      setUserActionReason("");
      fetchData();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to update account approval status."));
    } finally {
      setSubmittingAction(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-sm font-semibold text-slate-400">Loading Platform Administration Console...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 blur-[90px] rounded-full pointer-events-none" />
        <div className="space-y-1 z-10">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5">
              <ShieldCheck size={13} className="text-indigo-400" />
              Platform Administrator Role
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Live Governance
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Platform Governance & <span className="text-indigo-400">Review Console</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time audit oversight, credential forensics inspection, and recruiter/college accreditation
          </p>
        </div>

        <div className="flex items-center gap-3 z-10">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-2"
          >
            <RefreshCw size={14} className={refreshing ? "animate-spin text-indigo-400" : "text-slate-400"} />
            <span>Refresh State</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle size={18} className="text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs sm:text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Real Statistics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3 sm:gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-medium uppercase font-mono">Total Users</span>
            <Users size={16} className="text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-white">{stats?.total_users ?? 0}</div>
          <div className="text-[10px] text-slate-400">
            {stats?.students_count ?? 0} Students · {stats?.recruiters_count ?? 0} Rec.
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-amber-500/30 space-y-1 relative overflow-hidden">
          <div className="flex items-center justify-between text-amber-400">
            <span className="text-[11px] font-medium uppercase font-mono">Review Queue</span>
            <Clock size={16} className="text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-300">{stats?.pending_certificates_count ?? 0}</div>
          <div className="text-[10px] text-amber-400/80 font-medium">Awaiting manual check</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-emerald-500/30 space-y-1">
          <div className="flex items-center justify-between text-emerald-400">
            <span className="text-[11px] font-medium uppercase font-mono">Verified Certs</span>
            <CheckCircle2 size={16} className="text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-300">{stats?.verified_certificates_count ?? 0}</div>
          <div className="text-[10px] text-emerald-400/80">Tamper-free credentials</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-rose-500/30 space-y-1">
          <div className="flex items-center justify-between text-rose-400">
            <span className="text-[11px] font-medium uppercase font-mono">Flagged Anomalies</span>
            <ShieldAlert size={16} className="text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-300">{stats?.flagged_certificates_count ?? 0}</div>
          <div className="text-[10px] text-rose-400/80">4-tier forensic alerts</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-medium uppercase font-mono">Pending Students</span>
            <GraduationCap size={16} className="text-amber-400" />
          </div>
          <div className="text-2xl font-black text-amber-300">{stats?.pending_students_count ?? 0}</div>
          <div className="text-[10px] text-slate-400">Awaiting approval</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-medium uppercase font-mono">Pending Recruiters</span>
            <Building2 size={16} className="text-purple-400" />
          </div>
          <div className="text-2xl font-black text-purple-300">{stats?.pending_recruiters_count ?? 0}</div>
          <div className="text-[10px] text-slate-400">Waiting authorization</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-medium uppercase font-mono">Pending Colleges</span>
            <Award size={16} className="text-teal-400" />
          </div>
          <div className="text-2xl font-black text-teal-300">{stats?.pending_colleges_count ?? 0}</div>
          <div className="text-[10px] text-slate-400">TPO verified status</div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
        <button
          onClick={() => setActiveTab("reviews")}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === "reviews"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Shield size={16} />
          <span>Certificate Reviews</span>
          {certificates.length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-white/20 text-white">
              {certificates.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("students")}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === "students"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <GraduationCap size={16} />
          <span>Student Approvals</span>
          {students.filter(s => s.approval_status === "PENDING").length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {students.filter(s => s.approval_status === "PENDING").length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("recruiters")}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === "recruiters"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Building2 size={16} />
          <span>Recruiter Approvals</span>
          {recruiters.filter(r => r.approval_status === "PENDING").length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {recruiters.filter(r => r.approval_status === "PENDING").length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("colleges")}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === "colleges"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <GraduationCap size={16} />
          <span>College Approvals</span>
          {colleges.filter(c => c.approval_status === "PENDING").length > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">
              {colleges.filter(c => c.approval_status === "PENDING").length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("audit")}
          className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-2 whitespace-nowrap ${
            activeTab === "audit"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <History size={16} />
          <span>System Audit Trail</span>
          <span className="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-slate-300">
            {auditLogs.length}
          </span>
        </button>
      </div>

      {/* Tab 1: Certificate Reviews */}
      {activeTab === "reviews" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">Certificate Verification Reviews</h2>
              <p className="text-xs text-slate-400">
                Inspect AI/OCR extracted credentials, cryptographic hashes, and tamper forensics. Supplementing the 4-tier engine with admin judgment.
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Showing {certificates.length} item(s)
            </span>
          </div>

          {certificates.length === 0 ? (
            <div className="p-12 text-center rounded-3xl bg-slate-900/40 border border-slate-800 space-y-3">
              <CheckCircle2 size={40} className="text-emerald-400 mx-auto" />
              <div className="text-sm font-bold text-white">Review Queue is Clear</div>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                No certificates are currently flagged or pending administrative review. The automated 4-tier engine is validating submissions in real-time.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-800/70 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                  <tr>
                    <th className="py-3.5 px-4">Student</th>
                    <th className="py-3.5 px-4">Certificate Details</th>
                    <th className="py-3.5 px-4">Automated Status</th>
                    <th className="py-3.5 px-4">Admin Review</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {certificates.map((cert) => (
                    <tr key={cert.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-4 px-4 space-y-0.5">
                        <div className="font-bold text-white">{cert.student_name}</div>
                        <div className="text-[11px] text-slate-400">{cert.student_email}</div>
                        {cert.college_name && (
                          <div className="text-[10px] text-slate-500 truncate max-w-[180px]">
                            {cert.college_name}
                          </div>
                        )}
                      </td>

                      <td className="py-4 px-4 space-y-1">
                        <div className="font-semibold text-white">{cert.title}</div>
                        <div className="text-[11px] text-indigo-400">{cert.issuing_org}</div>
                        <div className="font-mono text-[9px] text-slate-500 truncate max-w-[220px]">
                          SHA: {cert.file_hash_sha256}
                        </div>
                      </td>

                      <td className="py-4 px-4 space-y-1">
                        <div className="flex items-center gap-1.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            cert.verification_status === "VERIFIED"
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : cert.verification_status === "FLAGGED"
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          }`}>
                            {cert.verification_status}
                          </span>
                          <span className="font-mono text-[11px] text-slate-400">
                            {cert.verification_score.toFixed(0)}/100
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400">
                          Badge: <span className="font-semibold text-slate-300">{cert.badge_tier}</span> · QR: {cert.qr_detected ? "Found" : "None"}
                        </div>
                      </td>

                      <td className="py-4 px-4 space-y-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          cert.admin_review_status === "APPROVED"
                            ? "bg-emerald-500/20 text-emerald-300"
                            : cert.admin_review_status === "REJECTED"
                            ? "bg-rose-500/20 text-rose-300"
                            : "bg-amber-500/20 text-amber-300"
                        }`}>
                          {cert.admin_review_status}
                        </span>
                        {cert.admin_review_reason && (
                          <div className="text-[10px] text-slate-400 italic truncate max-w-[200px]">
                            "{cert.admin_review_reason}"
                          </div>
                        )}
                      </td>

                      <td className="py-4 px-4 text-right">
                        <button
                          onClick={() => {
                            setSelectedCert(cert);
                            setReviewReason(cert.admin_review_reason || "");
                          }}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition flex items-center gap-1.5 ml-auto"
                        >
                          <Eye size={13} />
                          <span>Inspect & Review</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab: Student Approvals */}
      {activeTab === "students" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">Student Accounts & Approvals</h2>
              <p className="text-xs text-slate-400">
                Newly registered students start in PENDING approval status. Once approved, candidates gain access to resume extraction, certificate verification, and job matching.
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Total {students.length} student(s) · {students.filter(s => s.approval_status === "PENDING").length} pending
            </span>
          </div>

          <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Student & College</th>
                  <th className="py-3.5 px-4">Academic Profile</th>
                  <th className="py-3.5 px-4">Contact Email</th>
                  <th className="py-3.5 px-4">Registered Date</th>
                  <th className="py-3.5 px-4">Approval Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {students.map((stud) => (
                  <tr key={stud.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-4 px-4 space-y-0.5">
                      <div className="font-bold text-white flex items-center gap-1.5">
                        <GraduationCap size={14} className="text-indigo-400" />
                        <span>{stud.full_name}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">{stud.college_name || "Self-Enrolled Student"}</div>
                    </td>

                    <td className="py-4 px-4 space-y-0.5">
                      <div className="text-slate-300">{stud.department || "Computer Science"}</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        Class of {stud.graduation_year || "2026"} · CGPA: {stud.cgpa ? stud.cgpa.toFixed(1) : "N/A"}
                      </div>
                    </td>

                    <td className="py-4 px-4 font-mono text-[11px] text-slate-300">
                      {stud.email}
                    </td>

                    <td className="py-4 px-4 text-slate-400 text-[11px]">
                      {new Date(stud.created_at).toLocaleDateString()}
                    </td>

                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold ${
                        stud.approval_status === "APPROVED"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : stud.approval_status === "REJECTED"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse"
                      }`}>
                        {stud.approval_status}
                      </span>
                    </td>

                    <td className="py-4 px-4 text-right space-x-2">
                      {stud.approval_status !== "APPROVED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "student", user: stud, action: "APPROVE" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-sm"
                        >
                          Approve
                        </button>
                      )}
                      {stud.approval_status !== "REJECTED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "student", user: stud, action: "REJECT" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-600/80 hover:bg-rose-600 text-white transition shadow-sm"
                        >
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Recruiter Approvals */}
      {activeTab === "recruiters" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">Recruiter Accounts & Workflows</h2>
              <p className="text-xs text-slate-400">
                New recruiters start in PENDING approval status. Approved accounts gain job posting & full candidate discovery privileges.
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Total {recruiters.length} recruiter(s)
            </span>
          </div>

          <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Company & Recruiter</th>
                  <th className="py-3.5 px-4">Contact Email</th>
                  <th className="py-3.5 px-4">Registered Date</th>
                  <th className="py-3.5 px-4">Approval Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {recruiters.map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-4 px-4 space-y-0.5">
                      <div className="font-bold text-white">{rec.company_name || "Enterprise Employer"}</div>
                      <div className="text-[11px] text-slate-400">{rec.full_name}</div>
                    </td>

                    <td className="py-4 px-4 font-mono text-[11px] text-slate-300">
                      {rec.email}
                    </td>

                    <td className="py-4 px-4 text-slate-400 text-[11px]">
                      {new Date(rec.created_at).toLocaleDateString()}
                    </td>

                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold ${
                        rec.approval_status === "APPROVED"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : rec.approval_status === "REJECTED"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse"
                      }`}>
                        {rec.approval_status}
                      </span>
                    </td>

                    <td className="py-4 px-4 text-right space-x-2">
                      {rec.approval_status !== "APPROVED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "recruiter", user: rec, action: "APPROVE" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition"
                        >
                          Approve
                        </button>
                      )}
                      {rec.approval_status !== "REJECTED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "recruiter", user: rec, action: "REJECT" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-600/80 hover:bg-rose-600 text-white transition"
                        >
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: College Approvals */}
      {activeTab === "colleges" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">College TPO Accounts & Workflows</h2>
              <p className="text-xs text-slate-400">
                Placement cells and institutional TPO accounts. Approval grants full batch readiness analytics and student roster exports.
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Total {colleges.length} institution(s)
            </span>
          </div>

          <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Institution & TPO</th>
                  <th className="py-3.5 px-4">Official Email</th>
                  <th className="py-3.5 px-4">Registered Date</th>
                  <th className="py-3.5 px-4">Approval Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {colleges.map((col) => (
                  <tr key={col.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-4 px-4 space-y-0.5">
                      <div className="font-bold text-white">{col.college_name || "Academic Institution"}</div>
                      <div className="text-[11px] text-slate-400">{col.full_name}</div>
                    </td>

                    <td className="py-4 px-4 font-mono text-[11px] text-slate-300">
                      {col.email}
                    </td>

                    <td className="py-4 px-4 text-slate-400 text-[11px]">
                      {new Date(col.created_at).toLocaleDateString()}
                    </td>

                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold ${
                        col.approval_status === "APPROVED"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : col.approval_status === "REJECTED"
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse"
                      }`}>
                        {col.approval_status}
                      </span>
                    </td>

                    <td className="py-4 px-4 text-right space-x-2">
                      {col.approval_status !== "APPROVED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "college", user: col, action: "APPROVE" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition"
                        >
                          Approve
                        </button>
                      )}
                      {col.approval_status !== "REJECTED" && (
                        <button
                          onClick={() => setUserActionModal({ type: "college", user: col, action: "REJECT" })}
                          className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-600/80 hover:bg-rose-600 text-white transition"
                        >
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 4: Audit Logs */}
      {activeTab === "audit" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">System Audit Trail & Security Logs</h2>
              <p className="text-xs text-slate-400">
                Immutable chronological log of all administrator decisions, certificate overrides, and access modifications.
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              Total {auditLogs.length} logged action(s)
            </span>
          </div>

          <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-900/60 shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/70 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Timestamp</th>
                  <th className="py-3.5 px-4">Administrator</th>
                  <th className="py-3.5 px-4">Action</th>
                  <th className="py-3.5 px-4">Target Entity</th>
                  <th className="py-3.5 px-4">Audit Details / Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>

                    <td className="py-3.5 px-4 font-semibold text-white">
                      {log.admin_name || "Platform Admin"}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        log.action.includes("APPROVE")
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : log.action.includes("REJECT")
                          ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                      }`}>
                        {log.action}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 space-y-0.5">
                      <div className="font-semibold text-slate-200">{log.target_name || `ID #${log.target_id}`}</div>
                      <div className="text-[10px] text-slate-500 uppercase font-mono">{log.target_type}</div>
                    </td>

                    <td className="py-3.5 px-4 text-slate-400 max-w-md truncate">
                      {log.details || "Administrative review recorded."}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Certificate Deep Inspection & Review Modal */}
      {selectedCert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in overflow-y-auto">
          <div className="bg-slate-900 border border-slate-700/80 rounded-3xl w-full max-w-3xl shadow-2xl p-6 sm:p-8 space-y-6 my-8 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-slate-800 pb-4">
              <div className="space-y-1">
                <span className="text-[10px] font-mono uppercase bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">
                  4-Tier Forensic Inspection
                </span>
                <h3 className="text-xl font-bold text-white">{selectedCert.title}</h3>
                <p className="text-xs text-slate-400">
                  Claimed Issuer: <span className="text-indigo-400 font-semibold">{selectedCert.issuing_org}</span> · Student: <span className="text-white font-semibold">{selectedCert.student_name}</span> ({selectedCert.student_email})
                </p>
              </div>
              <button
                onClick={() => setSelectedCert(null)}
                className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* 4-Tier Verification Findings Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* SHA-256 Hash Card */}
              <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700 space-y-2">
                <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <CheckCircle2 size={14} className="text-emerald-400" />
                  <span>Tier 1: Cryptographic Hash</span>
                </div>
                <div className="p-2 rounded bg-slate-900 font-mono text-[10px] text-slate-400 break-all">
                  {selectedCert.file_hash_sha256}
                </div>
                <p className="text-[11px] text-slate-400">
                  Unique file fingerprint verified against student records.
                </p>
              </div>

              {/* QR Verification Card */}
              <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700 space-y-2">
                <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <ExternalLink size={14} className="text-indigo-400" />
                  <span>Tier 2: QR & Digital Signature</span>
                </div>
                <div className="text-xs">
                  {selectedCert.qr_detected ? (
                    <span className="text-emerald-400 font-medium">QR code detected & payload parsed</span>
                  ) : (
                    <span className="text-slate-400 italic">No physical QR code found on document</span>
                  )}
                </div>
                {selectedCert.qr_decoded_url && (
                  <div className="p-2 rounded bg-slate-900 font-mono text-[10px] text-indigo-300 break-all">
                    {selectedCert.qr_decoded_url}
                  </div>
                )}
              </div>

              {/* OCR Text Extraction Card */}
              <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700 space-y-2 sm:col-span-2">
                <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <FileText size={14} className="text-purple-400" />
                  <span>Tier 3: OCR Extracted Text & Named Entities</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300 max-h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                  {selectedCert.ocr_extracted_text || "No OCR text extracted."}
                </div>
              </div>

              {/* Forensic Tamper Analysis Details */}
              <div className="p-4 rounded-2xl bg-slate-800/60 border border-slate-700 space-y-2 sm:col-span-2">
                <div className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <ShieldAlert size={14} className={selectedCert.verification_status === "FLAGGED" ? "text-rose-400" : "text-emerald-400"} />
                  <span>Tier 4: Forensic ELA & Compression Analysis</span>
                </div>
                
                {selectedCert.tamper_analysis_details?.forensic_analysis ? (
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Forensic Tampering Verdict:</span>
                      <span className={`font-mono font-bold ${selectedCert.tamper_analysis_details.forensic_analysis.is_tampered ? "text-rose-400" : "text-emerald-400"}`}>
                        {selectedCert.tamper_analysis_details.forensic_analysis.is_tampered ? "ANOMALY DETECTED" : "PASS (CLEAN)"}
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px]">
                      {selectedCert.tamper_analysis_details.forensic_analysis.explanation}
                    </p>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No forensic anomalies recorded.</p>
                )}
              </div>
            </div>

            {/* Admin Decision Section */}
            <div className="pt-4 border-t border-slate-800 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">
                  Administrative Review Rationale / Notes (Mandatory for rejection)
                </label>
                <textarea
                  rows={2}
                  placeholder="e.g. Validated against official university credential database, verified by phone with registrar, etc."
                  value={reviewReason}
                  onChange={(e) => setReviewReason(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500 placeholder:text-slate-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedCert(null)}
                  disabled={submittingAction}
                  className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={() => handleCertificateReview("REJECT")}
                  disabled={submittingAction}
                  className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white transition flex items-center gap-1.5 shadow-lg shadow-rose-600/20"
                >
                  <XCircle size={14} />
                  <span>Reject Certificate</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleCertificateReview("APPROVE")}
                  disabled={submittingAction}
                  className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/20"
                >
                  <CheckCircle2 size={14} />
                  <span>Approve Override</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recruiter / College User Action Modal */}
      {userActionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-md shadow-2xl p-6 space-y-5">
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white">
                {userActionModal.action === "APPROVE" ? "Approve Account" : "Reject Account"}
              </h3>
              <p className="text-xs text-slate-400">
                {userActionModal.type === "student"
                  ? `Student Candidate: ${userActionModal.user.full_name} (${userActionModal.user.college_name || "Enrolled Student"})`
                  : userActionModal.type === "recruiter"
                  ? `Hiring Partner: ${userActionModal.user.company_name || userActionModal.user.full_name}`
                  : `Institution: ${userActionModal.user.college_name || userActionModal.user.full_name}`}
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Audit Notes / Justification {userActionModal.action === "REJECT" ? "(Mandatory)" : "(Optional)"}
              </label>
              <input
                type="text"
                placeholder={userActionModal.action === "REJECT" ? "e.g. Identity unverified, fraudulent credentials" : "e.g. Verified official email and credentials"}
                value={userActionReason}
                onChange={(e) => setUserActionReason(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
                required={userActionModal.action === "REJECT"}
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setUserActionModal(null)}
                disabled={submittingAction}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUserApproval}
                disabled={submittingAction}
                className={`px-4 py-2 rounded-xl text-xs font-semibold text-white transition ${
                  userActionModal.action === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-500"
                    : "bg-rose-600 hover:bg-rose-500"
                }`}
              >
                Confirm {userActionModal.action}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
