# CareerLens 5-Minute Hackathon Presentation Script

## 00:00 - 00:45 | The Hook & Problem
- *"Judges, over 70% of tech resumes today contain exaggerated or forged claims. Traditional job platforms rely on unverified keyword stuffing, and college placement offices have zero visibility into actual student readiness."*
- *"We built CareerLens: an AI-powered verified career and internship matching platform with a 4-tier forensic verification engine."*

## 00:45 - 01:45 | The Verification Engine in Action
- Navigate to `/student/certificates`.
- Click **"Test 1: Valid AWS (Gold Badge)"**:
  - Show the live 4-tier pipeline: SHA-256 integrity check -> QR decode -> OCR name matching -> ELA tamper check.
  - Show **GOLD BADGE** issued and Cloud skills auto-verified.
- Click **"Test 2: Tampered Cert (Flagged)"**:
  - Show how Error Level Analysis and metadata heuristics catch the Photoshop alteration and flag the submission in 2 seconds.
- Click **"Inspect Audit"** to showcase the full forensic report.

## 01:45 - 02:45 | Explainable Matching & 4-Week Roadmap
- Navigate to `/student/jobs`.
- Show **Cloud Software Engineer Intern** at TechCorp (**86% Match**).
- Click **"Explain Score & Gap"**:
  - Point out that CareerLens does not hide behind a black box:
    - 38/45 pts from Verified Skills
    - 16/20 pts from Resume Skills
    - 14/15 pts from Academic Fit
    - 18/20 pts from Credential Depth
  - Point out missing critical skills: Docker and Redis.
- Click **"Bridge Gap: 4-Week Roadmap"**:
  - Show how the AI generates a customized 4-week sprint with hands-on projects projecting a 96% match upon completion.

## 02:45 - 03:30 | Bilingual AI Counselor
- Navigate to `/student/chat`.
- Click the prompt chip or type in Hinglish:
  - *"Mera match score 95% kaise hoga?"*
  - Show how the AI replies in natural Hinglish while grounded in Aarav's verified AWS certificate.
- Ask in Hindi:
  - *"रिज्यूमे में कौन सी स्किल्स जोड़नी चाहिए?"*
  - Show immediate bilingual response.

## 03:30 - 04:30 | Multi-Role Value: Recruiter & College Dashboards
- Use the navbar Demo Role Switcher:
  - Switch to **Recruiter View (Sneha Rao @ TechCorp)**.
  - Filter by **"GOLD ONLY"** to show how verified candidates are prioritized for instant 1-click interviewing.
  - Switch to **College TPO View (Dr. Rajiv Kapoor @ IIIT)**.
  - Show cohort placement readiness (78.2%) and batch skill deficits (68% students missing Docker).

## 04:30 - 05:00 | Conclusion & Impact
- *"CareerLens creates a virtuous cycle: students build real verified skills, companies hire with confidence, and universities prepare students for actual market demand."*
