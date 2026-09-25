import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './lib/authContext';
import { Navbar } from './components/common/Navbar';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { StudentDashboard } from './pages/student/StudentDashboard';
import { ProfilePage } from './pages/student/ProfilePage';
import { ResumePage } from './pages/student/ResumePage';
import { CertificatePage } from './pages/student/CertificatePage';
import { JobsPage } from './pages/student/JobsPage';
import { ChatPage } from './pages/student/ChatPage';
import { RecruiterDashboard } from './pages/recruiter/RecruiterDashboard';
import { CollegeDashboard } from './pages/college/CollegeDashboard';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserRole } from './lib/types';

interface ProtectedRouteProps {
  children: React.ReactElement;
  allowedRoles?: UserRole[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin mb-3" />
        <p className="text-slate-400 text-xs">Authenticating session...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === 'platform_admin') return <Navigate to="/admin/dashboard" replace />;
    if (user.role === 'student') return <Navigate to="/student/dashboard" replace />;
    if (user.role === 'recruiter') return <Navigate to="/recruiter/dashboard" replace />;
    if (user.role === 'college_admin') return <Navigate to="/college/dashboard" replace />;
    return <Navigate to="/" replace />;
  }

  return children;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
          <Navbar />
          
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Student Protected Routes */}
              <Route 
                path="/student/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <StudentDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student/profile" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <ProfilePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student/resume" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <ResumePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student/certificates" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <CertificatePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student/jobs" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <JobsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/student/chat" 
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <ChatPage />
                  </ProtectedRoute>
                } 
              />

              {/* Recruiter Protected Routes */}
              <Route 
                path="/recruiter/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['recruiter']}>
                    <RecruiterDashboard />
                  </ProtectedRoute>
                } 
              />

              {/* College TPO Protected Routes */}
              <Route 
                path="/college/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['college_admin']}>
                    <CollegeDashboard />
                  </ProtectedRoute>
                } 
              />

              {/* Platform Admin Protected Routes */}
              <Route 
                path="/admin/dashboard" 
                element={
                  <ProtectedRoute allowedRoles={['platform_admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                } 
              />

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
