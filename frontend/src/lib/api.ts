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

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('careerlens_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
