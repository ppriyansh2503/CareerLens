import React, { useState } from 'react';
import { resumeAPI } from '../../lib/api';
import { 
  FileText, 
  UploadCloud, 
  CheckCircle2, 
  Sparkles, 
  ArrowRight,
  Github,
  Linkedin,
  Mail,
  Zap
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const ResumePage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [extractedData, setExtractedData] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (uploadFile: File) => {
    setLoading(true);
    setError(null);
    try {
      const result = await resumeAPI.uploadResume(uploadFile);
      setExtractedData(result);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to parse resume');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleResume = async () => {
    setLoading(true);
    const content = `%PDF-1.4
Aarav Sharma - Cloud Software Engineer
Email: aarav.sharma@example.com
GitHub: github.com/aarav-sharma-dev
LinkedIn: linkedin.com/in/aarav-sharma
Skills: Python, FastAPI, Docker, AWS, React, TypeScript, PostgreSQL, Git, Redis, Linux
Education: IIIT Delhi, B.Tech CSE (2026), CGPA 8.8
Projects: High-throughput API gateway with FastAPI and Docker.
%%EOF`;
    
    const blob = new Blob([content], { type: 'application/pdf' });
    const sampleFile = new File([blob], 'sample_aarav_sharma_resume.pdf', { type: 'application/pdf' });
    setFile(sampleFile);
    await handleFileUpload(sampleFile);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <FileText className="text-indigo-400" size={24} />
          <h1 className="text-2xl sm:text-3xl font-bold text-white">Resume Parser & Skill Extractor</h1>
        </div>
        <p className="text-sm text-slate-400">
          Upload your PDF resume to automatically extract verified contact links, standardized competencies, and domain skills using AI.
        </p>
      </div>

      {/* Upload Zone Card */}
      <div className="p-8 rounded-3xl bg-slate-800/40 border-2 border-dashed border-slate-700 hover:border-indigo-500/50 transition-colors text-center relative overflow-hidden">
        
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4">
          <UploadCloud size={32} />
        </div>

        <h3 className="text-base font-bold text-white mb-1">
          Upload Your Resume PDF
        </h3>
        <p className="text-xs text-slate-400 mb-6">
          Drag & drop your file here, or browse from your device (Max 10MB)
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3">
          <label className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-500 cursor-pointer transition-colors shadow-lg shadow-indigo-500/20">
            <span>Browse Computer</span>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  setFile(e.target.files[0]);
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
          </label>

          {/* 1-Click Judge Demo Button */}
          <button
            onClick={loadSampleResume}
            disabled={loading}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-semibold bg-slate-800 border border-indigo-500/40 text-indigo-300 hover:bg-slate-700 transition-colors"
          >
            <Zap size={15} className="text-amber-400 fill-amber-400" />
            <span>⚡ 1-Click Load Demo Resume</span>
          </button>
        </div>

        {file && (
          <div className="mt-4 text-xs text-slate-400 font-mono">
            Selected: <span className="text-slate-200">{file.name}</span>
          </div>
        )}

        {loading && (
          <div className="mt-6 flex flex-col items-center justify-center">
            <div className="w-8 h-8 rounded-full border-3 border-indigo-500/20 border-t-indigo-500 animate-spin mb-2" />
            <span className="text-xs text-indigo-300">Extracting skills via NLP engine...</span>
          </div>
        )}

        {error && (
          <div className="mt-4 text-xs text-rose-400 bg-rose-500/10 p-3 rounded-xl border border-rose-500/30">
            {error}
          </div>
        )}
      </div>

      {/* Extracted Output Preview */}
      {extractedData && (
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-800/40 border border-slate-700/80 shadow-2xl space-y-6 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={20} className="text-emerald-400" />
              <h2 className="text-lg font-bold text-white">Resume Extracted Successfully</h2>
            </div>
            <div className="text-xs font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30">
              Readiness Score: {extractedData.readiness_score}%
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Extracted Profile Headline:
            </div>
            <div className="text-base font-semibold text-white">
              {extractedData.headline}
            </div>
          </div>

          {/* Extracted Skills Matrix */}
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center justify-between">
              <span>Standardized Technical Skills Discovered ({extractedData.extracted_skills?.length || 0}):</span>
              <span className="text-indigo-400 text-[11px] font-normal">Auto-mapped to Industry Taxonomy</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {extractedData.extracted_skills?.map((sk: any, idx: number) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800 text-slate-200 border border-slate-700"
                >
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  <span>{sk.name}</span>
                  <span className="text-[10px] text-slate-500 uppercase">({sk.category})</span>
                </span>
              ))}
            </div>
          </div>

          {/* Next Step Banner */}
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Sparkles size={20} className="text-amber-400 shrink-0" />
              <div>
                <div className="text-xs font-bold text-white">Want to earn a GOLD or SILVER verification badge?</div>
                <div className="text-[11px] text-slate-300">Upload your certificate to run OCR, QR, and Tamper checks to boost credibility.</div>
              </div>
            </div>

            <Link
              to="/student/certificates"
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400 transition-colors shrink-0 flex items-center gap-1"
            >
              <span>Verify Certs</span>
              <ArrowRight size={13} />
            </Link>
          </div>

        </div>
      )}

    </div>
  );
};
