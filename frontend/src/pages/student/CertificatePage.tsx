import React, { useState, useEffect } from 'react';
import { useAuth } from '../../lib/authContext';
import { certificateAPI } from '../../lib/api';
import { Certificate } from '../../lib/types';
import { TrustBadge } from '../../components/verification/TrustBadge';
import { VerificationModal } from '../../components/verification/VerificationModal';
import { 
  Award, 
  UploadCloud, 
  ShieldCheck, 
  AlertTriangle, 
  FileCheck2, 
  Zap, 
  CheckCircle2, 
  Search,
  Fingerprint
} from 'lucide-react';

export const CertificatePage: React.FC = () => {
  const { user } = useAuth();
  const [certs, setCerts] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [selectedAuditId, setSelectedAuditId] = useState<number | null>(null);
  const [latestResult, setLatestResult] = useState<any | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [issuingOrg, setIssuingOrg] = useState('');
  const [file, setFile] = useState<File | null>(null);

  const fetchCerts = async () => {
    try {
      const data = await certificateAPI.listCertificates();
      setCerts(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchCerts();
  }, []);

  const handleUpload = async (uploadFile: File, certTitle: string, certIssuer: string) => {
    setVerifying(true);
    setLatestResult(null);
    try {
      const res = await certificateAPI.uploadCertificate(uploadFile, certTitle, certIssuer);
      setLatestResult(res);
      await fetchCerts();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Verification failed');
    } finally {
      setVerifying(false);
    }
  };

  // 1-Click Demo: Valid Certificate tailored to logged in student
  const runValidDemo = async () => {
    const studentName = user?.full_name || 'Aarav Sharma';
    const stamp = Date.now().toString().slice(-6);
    const content = `Amazon Web Services (AWS) Certificate of Achievement
Presented to ${studentName}
For completing: AWS Certified Solutions Architect - Associate
Issued: January 2026
Credential ID: AWS-DEV-${user?.id || 1}-${stamp}
Verification URL: https://aws.amazon.com/verification/AWS-DEV-${user?.id || 1}-${stamp}`;
    
    const blob = new Blob([content], { type: 'application/pdf' });
    const demoFile = new File([blob], `valid_aws_cert_${stamp}.pdf`, { type: 'application/pdf' });
    
    setTitle('AWS Certified Solutions Architect');
    setIssuingOrg('Amazon Web Services (AWS)');
    setFile(demoFile);
    await handleUpload(demoFile, 'AWS Certified Solutions Architect', 'Amazon Web Services (AWS)');
  };

  // 1-Click Demo: Tampered / Forged Certificate
  const runTamperedDemo = async () => {
    // Generate simulated altered file with Photoshop metadata header to trigger tamper detection
    const content = `Creator: Adobe Photoshop 2024
Producer: Canva Editor
Altered Recipient: Rohan Verma
Original Certificate: UC-99210
Issued to: Altered Text Region with compression discontinuity`;
    
    const blob = new Blob([content], { type: 'application/pdf' });
    const demoFile = new File([blob], 'forged_photoshop_cert.pdf', { type: 'application/pdf' });
    
    setTitle('Deep Learning Specialization (Forged)');
    setIssuingOrg('Coursera (Claimed)');
    setFile(demoFile);
    await handleUpload(demoFile, 'Deep Learning Specialization (Forged)', 'Coursera');
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Award className="text-amber-400" size={26} />
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            4-Tier Certificate Verification Engine
          </h1>
        </div>
        <p className="text-sm text-slate-400">
          Upload certificates to undergo multi-modal verification: SHA-256 duplicate checks, QR authority lookup, OCR name consistency, and Error Level Analysis (ELA) forensic tamper detection.
        </p>
      </div>

      {/* Main Upload & Demo Sandbox Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/40 border border-slate-700/80 shadow-2xl space-y-6">
        
        {/* Judge Demo Fast-Packs */}
        <div className="p-4 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <Zap size={15} className="text-amber-400 fill-amber-400" />
              <span>Hackathon Evaluation Sandbox (1-Click Presets)</span>
            </div>
            <p className="text-[11px] text-slate-300 mt-0.5">
              Test both positive authentic validation and negative forensic tamper detection instantly:
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={runValidDemo}
              disabled={verifying}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition-colors shadow-md shadow-emerald-600/20"
            >
              <CheckCircle2 size={14} />
              <span>Test 1: Valid AWS (Gold Badge)</span>
            </button>

            <button
              onClick={runTamperedDemo}
              disabled={verifying}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-600 text-white hover:bg-rose-500 transition-colors shadow-md shadow-rose-600/20"
            >
              <AlertTriangle size={14} />
              <span>Test 2: Tampered Cert (Flagged)</span>
            </button>
          </div>
        </div>

        {/* Manual Upload Form */}
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            if (file && title && issuingOrg) {
              handleUpload(file, title, issuingOrg);
            }
          }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Certificate Title
            </label>
            <input
              type="text"
              placeholder="e.g. AWS Certified Developer"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Issuing Organization
            </label>
            <input
              type="text"
              placeholder="e.g. Amazon Web Services (AWS)"
              value={issuingOrg}
              onChange={(e) => setIssuingOrg(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Select Document (PDF / Image)
            </label>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files?.[0]) setFile(e.target.files[0]);
              }}
              className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 text-xs file:mr-2 file:py-1 file:px-2.5 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500"
            />
          </div>

          <div className="md:col-span-3 flex justify-end">
            <button
              type="submit"
              disabled={verifying || !file}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-lg shadow-indigo-500/25 flex items-center gap-2"
            >
              <ShieldCheck size={16} />
              <span>{verifying ? 'Running 4-Tier Inspection...' : 'Trigger Verification'}</span>
            </button>
          </div>
        </form>

        {/* Live Processing Indicator */}
        {verifying && (
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-indigo-500/40 text-center space-y-3">
            <div className="w-10 h-10 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mx-auto" />
            <div className="text-sm font-semibold text-white">Running Credential Audit Protocol</div>
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-400">
              <span>[1/4] SHA-256 Hash Check</span>
              <span>•</span>
              <span>[2/4] QR Code Scanning</span>
              <span>•</span>
              <span>[3/4] OCR Entity Extraction</span>
              <span>•</span>
              <span>[4/4] ELA Tamper Forensics</span>
            </div>
          </div>
        )}

        {/* Latest Verification Result Banner */}
        {latestResult && (
          <div className={`p-5 rounded-2xl border animate-in fade-in space-y-3 ${
            latestResult.verification_status === 'VERIFIED'
              ? 'bg-emerald-500/10 border-emerald-500/30'
              : 'bg-rose-500/10 border-rose-500/30'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrustBadge tier={latestResult.badge_tier} size="md" showDetails />
                <span className="text-sm font-bold text-white">
                  Score: {latestResult.verification_score}/100
                </span>
              </div>
              <button
                onClick={() => setSelectedAuditId(latestResult.certificate_id)}
                className="text-xs font-semibold text-indigo-300 underline underline-offset-2 hover:text-white"
              >
                View Full Forensic Audit Report →
              </button>
            </div>

            <p className="text-xs text-slate-200">
              <strong>Verdict:</strong> {latestResult.audit_verdict}
            </p>

            {latestResult.awarded_skills && latestResult.awarded_skills.length > 0 && (
              <div className="flex items-center gap-2 text-xs">
                <span className="text-emerald-400 font-semibold">Skills Auto-Verified:</span>
                <span className="text-slate-300 font-mono">
                  {latestResult.awarded_skills.join(', ')}
                </span>
              </div>
            )}
          </div>
        )}

      </div>

      {/* Verified Certificates Roster */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <FileCheck2 className="text-indigo-400" size={20} />
          <span>My Credential Registry</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {certs.map((cert) => (
            <div
              key={cert.id}
              className="p-5 rounded-2xl bg-slate-800/40 border border-slate-700/60 hover:border-slate-600 transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <TrustBadge tier={cert.badge_tier} size="sm" showDetails />
                  <span className="text-xs font-mono text-slate-400">
                    {cert.verification_score}% Trust
                  </span>
                </div>
                <h3 className="text-base font-bold text-white mb-1">
                  {cert.title}
                </h3>
                <p className="text-xs text-slate-400">
                  {cert.issuing_org} {cert.issue_date && `• ${cert.issue_date}`}
                </p>
                <div className="text-[11px] font-mono text-slate-500 mt-2 truncate">
                  Hash: {cert.file_hash_sha256}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between">
                <span className={`text-xs font-semibold ${
                  cert.verification_status === 'VERIFIED' ? 'text-emerald-400' : 'text-rose-400'
                }`}>
                  Status: {cert.verification_status}
                </span>

                <button
                  onClick={() => setSelectedAuditId(cert.id)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600 hover:text-white transition-colors"
                >
                  Inspect Audit
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Forensic Audit Modal */}
      {selectedAuditId && (
        <VerificationModal
          certId={selectedAuditId}
          onClose={() => setSelectedAuditId(null)}
        />
      )}

    </div>
  );
};
