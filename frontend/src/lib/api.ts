import axios from 'axios';
import { 
  StudentProfile, 
  Certificate, 
  VerificationAuditDetail, 
  Job, 
  ExplainableMatch, 
  Roadmap, 
  ChatMessage, 
  Candidate, 
  CollegeAnalytics,
  User,
  PlatformStats,
  CertificateReviewItem,
  UserApprovalItem,
  AuditLogItem
} from './types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('careerlens_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Automatic fallback: if proxy fails (500/502/Network Error) when using relative URL, retry directly to backend
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest) return Promise.reject(error);

    const isProxyFailure =
      (error.response?.status === 500 || error.response?.status === 502) &&
      (!error.response?.data?.detail || typeof error.response?.data === 'string');
    const isNetworkError = !error.response && (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error'));

    if ((isProxyFailure || isNetworkError) && !originalRequest._retriedDirect) {
      originalRequest._retriedDirect = true;
      try {
        const directBase = 'http://127.0.0.1:8000/api/v1';
        let targetUrl = originalRequest.url || '';
        if (targetUrl.startsWith('/api/v1')) {
          targetUrl = targetUrl.replace('/api/v1', '');
        }
        if (!targetUrl.startsWith('http')) {
          targetUrl = `${directBase}${targetUrl.startsWith('/') ? '' : '/'}${targetUrl}`;
        }
        const fallbackResponse = await axios({
          ...originalRequest,
          url: targetUrl,
        });
        return fallbackResponse;
      } catch (retryError) {
        return Promise.reject(retryError);
      }
    }
    return Promise.reject(error);
  }
);

export const setAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('careerlens_token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    localStorage.removeItem('careerlens_token');
    delete api.defaults.headers.common['Authorization'];
  }
};

export const extractErrorMessage = (err: any, fallback: string = "An error occurred"): string => {
  if (!err) return fallback;
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d.msg || (typeof d === 'string' ? d : JSON.stringify(d))).join(', ');
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  const status = err?.response?.status;
  if (status === 500 || status === 502) {
    return "Server error occurred. Please ensure the backend is running and try again.";
  }
  if (err?.message && err.message.includes('500')) {
    return "Server error occurred. Please ensure the backend is running and try again.";
  }
  return err?.response?.data?.message || err?.message || fallback;
};

const savedToken = localStorage.getItem('careerlens_token');
if (savedToken) {
  api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
}

export const authAPI = {
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },
  register: async (userData: any) => {
    const res = await api.post('/auth/register', userData);
    return res.data;
  },
  me: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },
  demoSwitch: async (role: 'student' | 'recruiter' | 'college_admin') => {
    const res = await api.post(`/auth/demo-switch/${role}`);
    return res.data;
  }
};

export const profileAPI = {
  getStudentProfile: async (): Promise<StudentProfile> => {
    const res = await api.get('/profile/student');
    return res.data;
  },
  updateStudentProfile: async (data: any): Promise<StudentProfile> => {
    const res = await api.put('/profile/student', data);
    return res.data;
  },
  getReadiness: async () => {
    const res = await api.get('/profile/readiness');
    return res.data;
  }
};

export const resumeAPI = {
  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  }
};

export const certificateAPI = {
  uploadCertificate: async (file: File, title: string, issuingOrg: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('issuing_org', issuingOrg);
    const res = await api.post('/certificates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  listCertificates: async (): Promise<Certificate[]> => {
    const res = await api.get('/certificates/');
    return res.data;
  },
  getAudit: async (certId: number): Promise<VerificationAuditDetail> => {
    const res = await api.get(`/certificates/${certId}/audit`);
    return res.data;
  }
};

export const jobsAPI = {
  getJobs: async (): Promise<Job[]> => {
    const res = await api.get('/jobs/');
    return res.data;
  },
  getJobById: async (jobId: number): Promise<Job> => {
    const res = await api.get(`/jobs/${jobId}`);
    return res.data;
  },
  createJob: async (data: any): Promise<Job> => {
    const res = await api.post('/jobs/', data);
    return res.data;
  }
};

export const matchingAPI = {
  getExplainableMatch: async (jobId: number): Promise<ExplainableMatch> => {
    const res = await api.get(`/matching/explain/${jobId}`);
    return res.data;
  },
  getRoadmap: async (jobId: number): Promise<Roadmap> => {
    const res = await api.post(`/matching/roadmap/${jobId}`);
    return res.data;
  }
};

export const chatAPI = {
  sendMessage: async (content: string, sessionId?: number): Promise<ChatMessage> => {
    const res = await api.post('/chat/message', { content, session_id: sessionId });
    return res.data;
  },
  getHistory: async (): Promise<ChatMessage[]> => {
    const res = await api.get('/chat/history');
    return res.data;
  }
};

export const recruiterAPI = {
  discoverCandidates: async (params?: { skill?: string; badge?: string; verified_only?: boolean }): Promise<Candidate[]> => {
    const res = await api.get('/recruiter/candidates', { params });
    return res.data;
  },
  getCandidateCard: async (studentId: number) => {
    const res = await api.get(`/recruiter/candidate/${studentId}`);
    return res.data;
  }
};

export const collegeAPI = {
  getAnalytics: async (): Promise<CollegeAnalytics> => {
    const res = await api.get('/college/analytics');
    return res.data;
  },
  getStudents: async () => {
    const res = await api.get('/college/students');
    return res.data;
  }
};

export const adminAPI = {
  getStats: async (): Promise<PlatformStats> => {
    const res = await api.get('/admin/stats');
    return res.data;
  },
  listPendingCertificates: async (): Promise<CertificateReviewItem[]> => {
    const res = await api.get('/admin/certificates/pending');
    return res.data;
  },
  reviewCertificate: async (certId: number, action: 'APPROVE' | 'REJECT', reason?: string) => {
    const res = await api.post(`/admin/certificates/${certId}/review`, { action, reason });
    return res.data;
  },
  listStudents: async (): Promise<UserApprovalItem[]> => {
    const res = await api.get('/admin/approvals/students');
    return res.data;
  },
  reviewStudent: async (userId: number, action: 'APPROVE' | 'REJECT', reason?: string) => {
    const res = await api.post(`/admin/approvals/students/${userId}`, { action, reason });
    return res.data;
  },
  listRecruiters: async (): Promise<UserApprovalItem[]> => {
    const res = await api.get('/admin/approvals/recruiters');
    return res.data;
  },
  reviewRecruiter: async (userId: number, action: 'APPROVE' | 'REJECT', reason?: string) => {
    const res = await api.post(`/admin/approvals/recruiters/${userId}`, { action, reason });
    return res.data;
  },
  listColleges: async (): Promise<UserApprovalItem[]> => {
    const res = await api.get('/admin/approvals/colleges');
    return res.data;
  },
  reviewCollege: async (userId: number, action: 'APPROVE' | 'REJECT', reason?: string) => {
    const res = await api.post(`/admin/approvals/colleges/${userId}`, { action, reason });
    return res.data;
  },
  getAuditLogs: async (): Promise<AuditLogItem[]> => {
    const res = await api.get('/admin/audit-logs');
    return res.data;
  }
};

export default api;
