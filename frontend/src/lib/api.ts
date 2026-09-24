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
  User
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

export default api;
