# CareerLens REST API Reference

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Documentation: `http://localhost:8000/docs`

## 1. Authentication & Role Switcher
- `POST /auth/register` - Register student, recruiter, or college admin
- `POST /auth/login` - Obtain JWT access token
- `GET /auth/me` - Get active authenticated user details
- `POST /auth/demo-switch/{role}` - Fast-switch between demo personas (`student`, `recruiter`, `college_admin`)

## 2. Student Profile & Readiness
- `GET /profile/student` - Get student profile, verified skills, and badges
- `PUT /profile/student` - Update student profile fields
- `GET /profile/readiness` - Get placement readiness score decomposition

## 3. Resume Processing
- `POST /resume/upload` - Upload PDF resume, extract contact links, and standardized skills

## 4. Certificate Verification Engine
- `POST /certificates/upload` - Upload certificate, execute 4-tier audit, award Gold/Silver badge
- `GET /certificates/` - List user certificates with verification status
- `GET /certificates/{id}/audit` - Get detailed forensic audit report (hash, QR, OCR, ELA)

## 5. Jobs & Explainable Matching
- `GET /jobs/` - List jobs with dynamic match scores tailored to active student
- `GET /jobs/{id}` - Get job detail
- `POST /jobs/` - Recruiter create job with skill weights
- `GET /matching/explain/{job_id}` - Get 4-component explainable match breakdown
- `POST /matching/roadmap/{job_id}` - Generate personalized 4-week learning roadmap

## 6. Bilingual Career Counselor
- `POST /chat/message` - Send message (English, Hindi, Hinglish) with student context grounding
- `GET /chat/history` - Retrieve chat history

## 7. Recruiter & College Dashboards
- `GET /recruiter/candidates` - Search verified candidates with badge & skill filters
- `GET /recruiter/candidate/{id}` - View candidate credibility card and verified proof
- `GET /college/analytics` - Institutional readiness, department benchmarks, batch deficits
- `GET /college/students` - Batch student roster with badge distribution
