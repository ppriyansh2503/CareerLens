import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/authContext';
import { Navbar } from './components/common/Navbar';
import { LandingPage } from './pages/LandingPage';
import { StudentDashboard } from './pages/student/StudentDashboard';
import { ResumePage } from './pages/student/ResumePage';
import { CertificatePage } from './pages/student/CertificatePage';
import { JobsPage } from './pages/student/JobsPage';
import { ChatPage } from './pages/student/ChatPage';
import { RecruiterDashboard } from './pages/recruiter/RecruiterDashboard';
import { CollegeDashboard } from './pages/college/CollegeDashboard';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
          <Navbar />
          
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              
              {/* Student Routes */}
              <Route path="/student/dashboard" element={<StudentDashboard />} />
              <Route path="/student/resume" element={<ResumePage />} />
              <Route path="/student/certificates" element={<CertificatePage />} />
              <Route path="/student/jobs" element={<JobsPage />} />
              <Route path="/student/chat" element={<ChatPage />} />

              {/* Recruiter Routes */}
              <Route path="/recruiter/dashboard" element={<RecruiterDashboard />} />

              {/* College TPO Routes */}
              <Route path="/college/dashboard" element={<CollegeDashboard />} />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="border-t border-slate-800 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
            <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-4">
              <div>
                CareerLens © 2026 • AI-Powered Verified Career and Internship Matching Platform
              </div>
              <div className="flex items-center gap-4 text-slate-400">
                <span>Multi-Modal Verification Engine</span>
                <span>•</span>
                <span>Explainable Matching</span>
                <span>•</span>
                <span>Bilingual Career Guidance</span>
              </div>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
