# CareerLens System Architecture Document

## 1. High-Level Architectural Pattern
CareerLens adopts a decoupled, micro-service ready, three-tier architecture:
- **Presentation Tier**: React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons.
- **Application & Trust Tier**: Python 3.11+ FastAPI with native OpenCV, Pillow, pypdf, and Google Gemini 2.5 Flash SDK.
- **Persistence Tier**: SQLite (portable local development / hackathon demonstration) / PostgreSQL (production) with SQLAlchemy 2.0 ORM.

## 2. Security & Credential Integrity
- **JWT Authentication**: HS256 algorithm with encrypted user role claims (`student`, `recruiter`, `college_admin`).
- **Cryptographic File Digest**: SHA-256 fingerprints generated for every uploaded document before storage.
- **Image Error Level Analysis (ELA)**: Re-compression difference analysis to detect localized manipulation artifacts.
- **PDF Metadata Heuristics**: Extraction and audit of `/Creator` and `/Producer` headers to detect Canva / Photoshop modifications.
- **Name Token Matching**: Fuzzy token ratio algorithm verifying recipient name against user registration name.

## 3. Explainable Match Scoring Algorithm
```
Total Score = 0.45 * S_verified + 0.20 * S_resume + 0.15 * S_academic + 0.20 * S_depth
```
Where:
- `S_verified`: Weight of required skills backed by verified certificates (Gold/Silver).
- `S_resume`: Weight of required skills extracted from parsed resume (Self-reported).
- `S_academic`: Score based on department domain relevance and CGPA threshold (>= 8.0 = 15 pts).
- `S_depth`: Bonus for verified credentials and active portfolio/GitHub presence.
