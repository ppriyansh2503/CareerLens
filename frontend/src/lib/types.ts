export type UserRole = 'student' | 'recruiter' | 'college_admin' | 'platform_admin';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  approval_status?: 'APPROVED' | 'PENDING' | 'REJECTED';
  college_name?: string;
  company_name?: string;
  avatar_url?: string;
}

export interface StudentSkill {
  id: number;
  skill_id: number;
  name: string;
  category: string;
  proficiency: string;
  source: string;
  is_verified: boolean;
  verified_by_certificate_id?: number | null;
}

export interface CertificateSummary {
  id: number;
  title: string;
  issuing_org: string;
  verification_status: 'VERIFIED' | 'FLAGGED' | 'REJECTED' | 'PENDING';
  badge_tier: 'GOLD' | 'SILVER' | 'BRONZE' | 'NONE';
  verification_score: number;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  full_name: string;
  email: string;
  college_name?: string;
  headline?: string;
  bio?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  resume_file_url?: string;
  graduation_year: number;
  department: string;
  cgpa: number;
  placement_readiness_score: number;
  skills: StudentSkill[];
  certificates: CertificateSummary[];
}

export interface Certificate {
  id: number;
  student_id: number;
  title: string;
  issuing_org: string;
  issue_date?: string;
  credential_id?: string;
  credential_url?: string;
  file_path: string;
  file_hash_sha256: string;
  qr_detected: boolean;
  qr_decoded_url?: string;
  verification_score: number;
  verification_status: 'VERIFIED' | 'FLAGGED' | 'REJECTED' | 'PENDING';
  badge_tier: 'GOLD' | 'SILVER' | 'BRONZE' | 'NONE';
  verified_at: string;
}

export interface VerificationAuditDetail {
  certificate: Certificate;
  hash_verification: any;
  qr_verification: any;
  ocr_verification: any;
  tamper_analysis: any;
  verified_skills_awarded: string[];
  verdict: string;
  audit_timestamp: string;
}

export interface JobSkill {
  id: number;
  name: string;
  category: string;
  is_mandatory: boolean;
  weight: number;
}

export interface Job {
  id: number;
  recruiter_id: number;
  title: string;
  company_name: string;
  location: string;
  job_type: string;
  stipend_or_salary: string;
  description: string;
  requirements_summary?: string;
  is_active: boolean;
  created_at: string;
  skills: JobSkill[];
  match_score?: number;
  match_tier?: string;
}

export interface ScoreBreakdown {
  verified_skills_component: number;
  unverified_skills_component: number;
  academic_fit_component: number;
  project_fit_component: number;
}

export interface SkillAnalysis {
  matched_verified_skills: string[];
  matched_unverified_skills: string[];
  missing_critical_skills: string[];
  bonus_skills: string[];
}

export interface ExplainableMatch {
  job_id: number;
  job_title: string;
  company_name: string;
  overall_score: number;
  match_tier: string;
  score_breakdown: ScoreBreakdown;
  skill_analysis: SkillAnalysis;
  readiness_verdict: string;
  recommended_action: string;
}

export interface RoadmapWeek {
  week_number: number;
  theme: string;
  goal: string;
  key_topics: string[];
  action_items: string[];
  recommended_resources: string[];
  milestone_project: string;
}

export interface Roadmap {
  job_id: number;
  target_role: string;
  current_match_score: number;
  projected_match_score: number;
  summary: string;
  weeks: RoadmapWeek[];
  created_at: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  sender: 'user' | 'assistant';
  content: string;
  detected_language: string;
  created_at: string;
}

export interface Candidate {
  student_id: number;
  user_id: number;
  full_name: string;
  college_name: string;
  headline: string;
  department: string;
  graduation_year: number;
  cgpa: number;
  placement_readiness_score: number;
  highest_badge: 'GOLD' | 'SILVER' | 'NONE';
  gold_badges_count: number;
  silver_badges_count: number;
  verified_skills: string[];
  all_skills: string[];
  certificates_count: number;
  resume_url?: string;
  github_url?: string;
  linkedin_url?: string;
}

export interface CollegeAnalytics {
  institution_name: string;
  academic_year: string;
  total_enrolled_students: number;
  average_readiness_score: number;
  placement_readiness_distribution: {
    placement_ready_students: number;
    near_ready_students: number;
    upskilling_needed_students: number;
    ready_percentage: number;
  };
  verification_metrics: {
    total_certificates_audited: number;
    gold_badges_awarded: number;
    silver_badges_awarded: number;
    flagged_tampered_submissions: number;
    fraud_prevention_rate: string;
  };
  department_benchmarks: {
    department: string;
    student_count: number;
    avg_readiness: number;
    placement_ready_percentage: number;
  }[];
  top_verified_skills: {
    skill: string;
    verified_students: number;
  }[];
  top_skill_deficits: {
    skill: string;
    students_missing_percentage: number;
    industry_demand: string;
  }[];
}
