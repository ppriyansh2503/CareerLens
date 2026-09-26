import os
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.student import StudentProfile

class AIService:
    """
    Bilingual AI Career Counselor & NLP Service:
    - English, Hindi (Devanagari), and Hinglish support
    - Grounded with real student profile context (verified skills, certs, readiness)
    - Powered by Google Gemini 2.5 Flash with intelligent offline fallback
    """

    SYSTEM_PROMPT = """
You are 'CareerLens AI', an intelligent, pragmatic AI career mentor and senior placement counselor for college students (2nd, 3rd, and 4th-year B.Tech / BE engineering undergraduates).

You are NOT a search engine, a generic FAQ bot, or an academic researcher. You talk like an experienced, supportive, and technically sharp senior engineering mentor who understands the Indian campus placement ecosystem, modern tech industry requirements, and the student's real profile.

==================================================
CORE PRINCIPLES & RESPONSE STYLE
==================================================
1. TONE & DEPTH:
   - Smart, practical, personalized, and context-aware.
   - Slightly advanced yet accessible to an undergraduate student.
   - Use the pattern: Basic Explanation → Practical Implementation → Advanced Improvement (e.g. Build MVP with FastAPI + PostgreSQL → Add JWT auth & RBAC → Deploy on Docker/AWS with caching).
   - Never give overly basic advice (e.g., "build a to-do list or calculator" is banned unless the student is an absolute beginner).
   - Never give unnecessarily complex enterprise architecture without explaining practical starting steps.
   - Direct and concise: Start by directly answering the user's question. Avoid generic motivational filler ("Work hard!", "Believe in yourself!").

2. STRICT PROFILE GROUNDING:
   - Ground every recommendation in the student's actual LIVE profile data provided in the context.
   - Verified skills and Gold/Silver badges carry the highest credibility.
   - Use the student's EXACT live Placement Readiness Score provided in the context. NEVER hallucinate, recalculate, or cite a different readiness score!
   - Do NOT invent skills, certificates, companies, or experiences that are not in the student's profile or CareerLens data.

3. INTENT SPECIFIC GUIDANCE:
   - PROJECT IDEAS: Suggest 3-5 realistic, high-impact projects matching their actual skills (APIs, databases, auth, AI/cloud, automation). For each: Name, What it does, Why it fits current skills, Tech stack, Main features, Difficulty, What you will learn, Resume value, and Optional advanced feature.
   - BUSINESS OPPORTUNITIES: Suggest realistic college-student opportunities (College project → MVP → 5-20 users → validation → small service/SaaS). For each: Product/business idea, Problem solved, Target users, Why skills fit, MVP features, Starting small, Monetization, Future expansion. (No fake get-rich-quick claims).
   - CAREER / JOB ROLES: Specific roles fitting their profile (e.g., Backend Engineer, Cloud Intern). Detail why each fits, current strengths, missing skills, and what to learn next.
   - INTERNSHIP QUESTIONS: Use actual internship match scores and listings from CareerLens. Explain matched skills and specific missing skills.
   - SKILL GAPS: Explain current skill, missing skill, why it matters in recruitment, how to learn it, and a suggested hands-on project.
   - LEARNING ROADMAPS: Practical week-by-week timeline (Week 1 Fundamentals, Week 2 Practical implementation, Week 3 Project build, Week 4 Deployment & Interview prep).
   - FOLLOW-UP QUESTIONS: If the student asks follow-ups like "Which one should I build first?" or "How do I start?", compare previously suggested projects on skills, difficulty, time, resume value, and learning value.

4. LANGUAGE SUPPORT:
   - Automatically match the student's language!
   - If English: Respond in crisp, articulate professional English.
   - If Hindi (हिंदी): Respond in polite, natural, supportive Hindi (Devanagari script).
   - If Hinglish (e.g. "Mere skills ke according kaunse projects banayein?"): Reply in natural, friendly, colloquial Hinglish without awkward literal translations.
"""

    @classmethod
    def detect_language(cls, text: str) -> str:
        # Check for Devanagari script (Unicode range 0900-097F)
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        
        # Check for Hinglish keywords
        hinglish_words = {
            "kare", "kaise", "kya", "mera", "meri", "mere", "mujhe", "batao", "chahiye",
            "kaunse", "kaunsa", "hoga", "karna", "hai", "hain", "banna", "mil", "sakta",
            "sakti", "bhi", "pehle", "karo", "seekhna", "seekhu", "paise", "kamana",
            "banau", "banana", "achha", "kuch", "apna", "apne", "wale", "wali", "hogi"
        }
        words = re.findall(r'[a-zA-Z]+', text.lower())
        match_count = sum(1 for w in words if w in hinglish_words)
        if match_count >= 1:
            return "hinglish"
        
        return "en"

    @classmethod
    def generate_chat_response(
        cls,
        user_message: str,
        student: Optional[StudentProfile] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        jobs_matches: Optional[List[Dict[str, Any]]] = None,
        missing_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        detected_lang = cls.detect_language(user_message)

        # 1. Build comprehensive, structured student context
        context_str = cls._build_structured_context(
            student=student,
            jobs_matches=jobs_matches,
            missing_skills=missing_skills,
            chat_history=chat_history
        )

        # 2. Check if Google Gemini API key is configured
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip():
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                
                # Format full prompt with system prompt, profile context, history, and message
                full_prompt = (
                    f"{cls.SYSTEM_PROMPT}\n\n"
                    f"{context_str}\n\n"
                    f"User Message: {user_message}\n\n"
                    f"Respond as CareerLens AI in the user's language ({detected_lang}):"
                )
                
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.6,
                        max_output_tokens=1500
                    )
                )
                if response and response.text:
                    return {
                        "content": response.text.strip(),
                        "detected_language": detected_lang,
                        "engine": "google-gemini-2.5"
                    }
            except Exception as e:
                print(f"[Gemini AI Service Notice] Falling back to heuristic response engine: {e}")

        # 3. Intelligent offline fallback engine (for hackathon demo reliability)
        response_text = cls._offline_smart_response(
            msg=user_message,
            lang=detected_lang,
            student=student,
            chat_history=chat_history,
            jobs_matches=jobs_matches,
            missing_skills=missing_skills
        )
        return {
            "content": response_text,
            "detected_language": detected_lang,
            "engine": "careerlens-heuristic-engine"
        }

    @classmethod
    def _build_structured_context(
        cls,
        student: Optional[StudentProfile],
        jobs_matches: Optional[List[Dict[str, Any]]] = None,
        missing_skills: Optional[List[str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not student:
            return "No authenticated student profile available."

        # Skills categorization
        verified_skills = [s.skill.name for s in student.skills if s.is_verified and s.skill]
        resume_skills = [s.skill.name for s in student.skills if s.source == "resume" and s.skill]
        all_skills = [s.skill.name for s in student.skills if s.skill]
        certs = [f"{c.title} ({c.badge_tier} Badge - {c.verification_status})" for c in student.certificates if c.verification_status == "VERIFIED"]
        live_score = round(float(student.placement_readiness_score or 0.0), 1)

        # Job matching summary
        match_summary_lines = []
        if jobs_matches:
            for m in jobs_matches[:3]:
                title = m.get("job_title", "Internship")
                company = m.get("company_name", "Partner")
                score = m.get("overall_score", 0)
                matched = m.get("skill_analysis", {}).get("matched_verified_skills", [])
                missing = m.get("skill_analysis", {}).get("missing_critical_skills", [])
                match_summary_lines.append(
                    f"  * {title} at {company}: {score}% Match (Matched: {', '.join(matched) or 'None'}; Missing: {', '.join(missing) or 'None'})"
                )
        matches_text = "\n".join(match_summary_lines) if match_summary_lines else "  * No active internship applications yet."

        missing_text = ", ".join(missing_skills[:6]) if missing_skills else "Cloud Deployment, Production Caching"

        # Conversation history
        history_lines = []
        if chat_history:
            for turn in chat_history[-6:]:
                role = "Student" if turn.get("sender") == "user" else "Counselor"
                history_lines.append(f"{role}: {turn.get('content')}")
        history_text = "\n".join(history_lines) if history_lines else "No previous messages in this session."

        return f"""
==================================================
STUDENT LIVE PROFILE CONTEXT (GROUND TRUTH)
==================================================
- Full Name: {student.user.full_name if student.user else 'Student'}
- College: {student.user.college_name if student.user else 'Engineering College'}
- Academic Background: {student.department}, Class of {student.graduation_year}, CGPA: {student.cgpa}
- EXACT LIVE READINESS SCORE: {live_score}% (CRITICAL: You must cite this EXACT score if mentioning readiness. Never invent or recalculate a different score!)
- Verified Credentials (Gold/Silver): {', '.join(verified_skills) or 'None yet'}
- Resume Parsed Skills: {', '.join(resume_skills) or 'None'}
- All Listed Skills: {', '.join(all_skills) or 'None'}
- Verified Certificates: {', '.join(certs) or 'None yet'}
- Headline: {student.headline or 'Engineering Undergraduate'}
- Bio / Projects: {student.bio or student.resume_raw_text or 'Software development and algorithms enthusiast.'}

==================================================
LIVE CAREERLENS INTERNSHIP MATCHES:
==================================================
{matches_text}

- Priority Missing Skills across CareerLens Jobs: {missing_text}

==================================================
RECENT CONVERSATION HISTORY:
==================================================
{history_text}
"""

    @classmethod
    def _detect_intent(
        cls,
        msg: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        msg_lower = msg.lower()

        # Follow-up intent
        is_followup_build = any(k in msg_lower for k in [
            "which one should i build first", "which to build first", "which project first",
            "pehle kaunsa", "kaunsa pehle", "which one first", "how do i start", "kaise start",
            "architecture", "system design", "compare"
        ])
        if not is_followup_build and chat_history:
            last_assistant_msg = ""
            for h in reversed(chat_history):
                if h.get("sender") == "assistant":
                    last_assistant_msg = h.get("content", "").lower()
                    break
            if ("project" in last_assistant_msg or "analyzer" in last_assistant_msg) and any(k in msg_lower for k in ["first", "pehle", "start", "choose", "begin", "edge", "highest", "which"]):
                is_followup_build = True

        if is_followup_build:
            return "followup"

        # Business / Startup intent
        if any(k in msg_lower for k in ["business", "monetize", "monetise", "paise", "kamana", "startup", "revenue", "product idea", "client", "earn", "saas"]):
            return "business"

        # Project ideas intent
        if any(k in msg_lower for k in ["project", "projects", "banana", "build", "idea", "ideas", "banao", "banaye", "portfolio"]):
            return "projects"

        # Readiness score explanation
        if any(k in msg_lower for k in ["readiness", "score", "percentage", "%", "index", "kyun hai", "why is my score", "explain my score"]):
            return "readiness_score"

        # Internships
        if any(k in msg_lower for k in ["internship", "internships", "intern", "company", "companies", "opening"]):
            return "internships"

        # Career / Job roles
        if any(k in msg_lower for k in ["role", "roles", "job", "jobs", "career", "kaunsi job", "which jobs", "what roles", "apply for", "eligible", "profile fit"]):
            return "career_roles"

        # Skill gaps
        if any(k in msg_lower for k in ["missing", "gap", "gaps", "seekhna", "learn next", "kya seekhu", "kya seekhna", "weakness", "improve skills", "lack"]):
            return "skill_gap"

        # Learning roadmap
        if any(k in msg_lower for k in ["roadmap", "road map", "guide", "week", "month", "path", "kaise seekhe", "how to learn", "how do i learn", "step by step", "plan"]):
            return "roadmap"

        # Resume advice
        if any(k in msg_lower for k in ["resume", "cv", "review resume", "improve resume", "add to resume", "bullet", "ats", "format"]):
            return "resume"

        return "general"

    @classmethod
    def _offline_smart_response(
        cls,
        msg: str,
        lang: str,
        student: Optional[StudentProfile] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        jobs_matches: Optional[List[Dict[str, Any]]] = None,
        missing_skills: Optional[List[str]] = None
    ) -> str:
        msg_lower = msg.lower()
        student_name = student.user.full_name if (student and student.user) else "Aarav"
        readiness = round(float(student.placement_readiness_score or 0.0), 1) if student else 88.5
        
        verified_skills = [s.skill.name for s in student.skills if s.is_verified and s.skill] if student else ["AWS", "React"]
        all_skills = [s.skill.name for s in student.skills if s.skill] if student else ["Python", "FastAPI", "Docker", "AWS", "React", "PostgreSQL"]
        top_skills = verified_skills if verified_skills else all_skills[:4]
        primary_stack = ", ".join(top_skills[:3]) if top_skills else "Python, React, and Cloud"

        intent = cls._detect_intent(msg, chat_history)

        # -------------------------------------------------------------
        # Intent 1: FOLLOW-UP BUILD DECISION ("Which one should I build first?")
        # -------------------------------------------------------------
        if intent == "followup":
            if lang == "hi":
                return (
                    f"### {student_name}, आपको सबसे पहले कौन सा प्रोजेक्ट बनाना चाहिए? 🎯\n\n"
                    f"आपकी वर्तमान प्रोफाइल और **{readiness}%** रेडीनेस स्कोर के आधार पर, यहाँ प्राथमिकताओं का विश्लेषण है:\n\n"
                    f"#### 1. सबसे पहले बनाएं: **AI Resume & Career Match Analyzer** 🥇\n"
                    f"- **क्यों?**: यह सीधे आपकी प्रमाणित स्किल्स ({primary_stack}) का 100% उपयोग करता है और रिक्रूटर्स को सबसे ज्यादा आकर्षित करता है।\n"
                    f"- **कठिनाई**: मध्यम (2-3 सप्ताह)।\n"
                    f"- **रिज्यूमे वैल्यू**: बहुत ज्यादा (9.5/10)।\n"
                    f"- **शुरुआत कैसे करें**: \n"
                    f"  1. FastAPI बैकएंड सेटअप करें और PDF टेक्स्ट एक्सट्रैक्शन के लिए `pypdf` या `pdfplumber` जोड़ें।\n"
                    f"  2. स्किल्स एक्सट्रैक्शन के लिए कीवर्ड मैचिंग या ओपन-सोर्स NLP मॉडल लगाएं।\n"
                    f"  3. React + Tailwind CSS से क्लीन ड्रैग-एंड-ड्रॉप डैशबोर्ड बनाएं।\n\n"
                    f"#### 2. इसके बाद बनाएं: **Cloud-Native Task Queue & Microservice** 🥈\n"
                    f"- **ट्रेड-ऑफ**: इसके लिए Redis और Docker की आवश्यकता होगी, जिससे आपको DevOps इंटरव्यू में फायदा मिलेगा।\n\n"
                    f"💡 **सलाह**: पहले प्रोजेक्ट का कोर API 3 दिनों में पूरा करें, फिर इसमें ऑथेंटिकेशन और डॉकर जोड़ें।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, pehle kaunsa project banana chahiye? 🚀\n\n"
                    f"Aapki current profile, verified skills ({primary_stack}), aur **{readiness}%** readiness ke hisaab se recommendations ye hain:\n\n"
                    f"#### 1. Build this FIRST: **AI Resume & Career Match Analyzer** 🥇\n"
                    f"- **Why start here?**: Ye aapke existing stack ({primary_stack}) par directly depend karta hai aur iska placement interview me high impact padta hai.\n"
                    f"- **Difficulty**: Moderate (2 weeks for functional MVP).\n"
                    f"- **Resume ROI**: 10/10 — Recruiters love working demos that solve real placement pain points.\n"
                    f"- **Step-by-step start kaise karein**:\n"
                    f"  1. *Day 1-3*: FastAPI backend setup karein, `/upload` endpoint banayein jo PDF resume parse kare.\n"
                    f"  2. *Day 4-7*: Skill extraction logic aur job description scoring algorithm likhein.\n"
                    f"  3. *Day 8-12*: React frontend me clean UI, score visualization gauge, aur skill breakdown charts jodein.\n"
                    f"  4. *Day 13-14*: Dockerfile likhkar AWS ya Render par deploy karein aur GitHub README me architecture diagram daalein.\n\n"
                    f"#### 2. Build NEXT: **Distributed Cloud Task Queue & Caching Engine** 🥈\n"
                    f"- **Tradeoff**: Is project me Redis aur Celery sikhne ka time lagega, but backend performance interviews me ye gold standard hai.\n\n"
                    f"👉 **Action item**: Pehle project ka Day 1 boilerplate aaj hi create karein!"
                )
            else:
                return (
                    f"### Which Project Should You Build First, {student_name}? 🎯\n\n"
                    f"Based on your profile, verified competencies ({primary_stack}), and current **{readiness}%** readiness, here is the prioritized roadmap:\n\n"
                    f"#### 1. Build FIRST: **AI Resume & Career Match Analyzer** 🥇\n"
                    f"- **Why First**: It directly leverages your current core skills ({primary_stack}) with zero blocking dependencies, maximizing immediate resume impact.\n"
                    f"- **Difficulty**: Intermediate (10-14 days to deployable MVP).\n"
                    f"- **Resume Value**: 9.5/10 — Recruiters immediately grasp the business utility.\n"
                    f"- **How to Start Right Now**:\n"
                    f"  1. **Phase 1 (Backend Core)**: Initialize FastAPI, configure CORS, and build a `/resume/parse` endpoint using `pdfplumber`.\n"
                    f"  2. **Phase 2 (Matching Logic)**: Implement cosine similarity or weighted overlap between candidate skills and job requirements.\n"
                    f"  3. **Phase 3 (Frontend)**: Build a React interface with drag-and-drop resume upload and match score breakdown.\n"
                    f"  4. **Phase 4 (Advanced Polish)**: Containerize with Docker and deploy with CI/CD.\n\n"
                    f"#### 2. Build SECOND: **Distributed Task Queue & Caching Service** 🥈\n"
                    f"- **Trade-off**: Requires learning Redis and message queues. Build this once your first project is live.\n\n"
                    f"💡 **Recommendation**: Start by scaffolding the FastAPI project repository today."
                )

        # -------------------------------------------------------------
        # Intent 2: PROJECT IDEAS
        # -------------------------------------------------------------
        elif intent == "projects":
            if lang == "hi":
                return (
                    f"### {student_name}, आपकी स्किल्स ({primary_stack}) के अनुसार 3 बेहतरीन प्रोजेक्ट्स 🚀\n\n"
                    f"ये प्रोजेक्ट्स कॉलेज के सामान्य प्रोजेक्ट्स (जैसे To-Do या Calculator) से कहीं बेहतर हैं और सीधे आपके रिज्यूमे को मजबूत बनाते हैं:\n\n"
                    f"#### 1. **AI-Powered Resume & Internship Match Analyzer**\n"
                    f"- **यह क्या करता है**: छात्र का PDF रिज्यूमे पार्स करता है और जॉब डिस्क्रिप्शन के साथ मैच स्कोर व स्किल गैप निकालता है।\n"
                    f"- **क्यों उपयुक्त है**: आपकी {primary_stack} स्किल्स के साथ 100% फिट बैठता है।\n"
                    f"- **टेक स्टैक**: React + FastAPI + SQLite/PostgreSQL + Python NLP।\n"
                    f"- **मुख्य फीचर्स**: PDF टेक्स्ट पार्सिंग, वेटेड मैचिंग एल्गोरिदम, स्किल-गैप चार्ट्स।\n"
                    f"- **कठिनाई**: मध्यम | **सीख**: फुल-स्टैक आर्किटेक्चर, REST API डिजाइन, रिअल-टाइम डेटा पार्सिंग।\n"
                    f"- **रिज्यूमे इम्पैक्ट**: रिक्रूटर्स को वास्तविक समस्या सुलझाने की आपकी क्षमता दिखाता है।\n"
                    f"- **एडवांस्ड फीचर**: वेक्टर एम्बेडिंग्स (Semantic Search) जोड़कर सिमेंटिक मैचिंग करें।\n\n"
                    f"#### 2. **Cloud-Native Distributed Task Queue & Rate Limiter**\n"
                    f"- **यह क्या करता है**: बैकग्राउंड जॉब्स (ईमेल भेजना, इमेज रीसाइज़िंग) को प्रोसेस करने के लिए हाई-थ्रूपुट क्यू सिस्टम।\n"
                    f"- **क्यों उपयुक्त है**: बैकएंड और क्लाउड प्रोफिशिएंसी सिद्ध करता है।\n"
                    f"- **टेक स्टैक**: Python/FastAPI + Redis + Docker + AWS S3।\n"
                    f"- **मुख्य फीचर्स**: टोकन बकेट रेट लिमिटर, बैकग्राउंड वर्कर थ्रेड्स, फेल्योर रीट्री लॉजिक।\n"
                    f"- **कठिनाई**: मध्यम-उच्च | **सीख**: कंकरेंसी, एसिंक्रोनस प्रोग्रामिंग, रीडिस कैशिंग।\n"
                    f"- **एडवांस्ड फीचर**: डॉकर कम्पोज़ और AWS ECS पर डिप्लॉयमेंट।\n\n"
                    f"#### 3. **Tamper-Proof Digital Credential & Certificate Verification Engine**\n"
                    f"- **यह क्या करता है**: QR कोड, SHA-256 हैश और डिजिटल सिग्नेचर के ज़रिए सर्टिफिकेट्स का फर्जीवाड़ा पकड़ता है।\n"
                    f"- **क्यों उपयुक्त है**: आधुनिक फिनटेक और एडटेक कंपनियों में ऐसी तकनीक की भारी मांग है।\n"
                    f"- **टेक स्टैक**: React + FastAPI + OpenCV/Pyzbar + SQLite।\n"
                    f"- **मुख्य फीचर्स**: QR डिकोडिंग, हैश इंटीग्रिटी चेक, फोरेंसिक ELA एनालिसिस डैशबोर्ड।\n"
                    f"- **एडवांस्ड फीचर**: ब्लॉकचेन या क्रिप्टोग्राफिक की-पेयर साइनिंग।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, aapke skills ({primary_stack}) ke according 3 top-tier projects 🚀\n\n"
                    f"College ke basic to-do apps ya calculators ki jagah ye projects aapke resume ko top 5% candidates me le aayenge:\n\n"
                    f"#### 1. **AI Resume & Career Match Analyzer** 📄\n"
                    f"- **What it does**: Student ka PDF resume parse karta hai, skills extract karta hai, aur job requirements ke sath weighted match score calculate karta hai.\n"
                    f"- **Why it fits your profile**: Aapki {primary_stack} competencies ke liye perfect showcase hai.\n"
                    f"- **Tech Stack**: React + Tailwind CSS + FastAPI + PostgreSQL / SQLite + Python NLP.\n"
                    f"- **Main Features**: PDF parser, dynamic skill taxonomy, explainable match breakdown (verified vs self-reported).\n"
                    f"- **Difficulty**: Intermediate | **Learning Outcome**: API design, state management, algorithmic scoring.\n"
                    f"- **Resume Value**: High — Shows you can build usable enterprise tools.\n"
                    f"- **Advanced Upgrade**: OpenAI/Gemini embeddings use karke semantic skill similarity add karein.\n\n"
                    f"#### 2. **Cloud Microservice & Distributed Task Queue** ☁️\n"
                    f"- **What it does**: High-traffic API gateway with token-bucket rate limiting and async background job processing.\n"
                    f"- **Why it fits**: Cloud aur Backend developer roles me caching aur queues standard requirements hain.\n"
                    f"- **Tech Stack**: FastAPI + Redis + Docker + AWS (S3 / EC2).\n"
                    f"- **Main Features**: Asynchronous worker execution, Redis caching layer, JWT authentication.\n"
                    f"- **Difficulty**: Intermediate-Advanced | **Learning**: Redis internals, Docker containerization, cloud networking.\n"
                    f"- **Advanced Upgrade**: GitHub Actions se CI/CD pipeline banakar automatic AWS deploy karein.\n\n"
                    f"#### 3. **Tamper-Proof Document Verification Portal** 🛡️\n"
                    f"- **What it does**: Educational certificates aur credentials ko QR decoding, cryptographic SHA-256 hashes aur forensic analysis se verify karta hai.\n"
                    f"- **Why it fits**: FinTech, EdTech aur Govt portal tech stacks ka exact replica hai.\n"
                    f"- **Tech Stack**: React + FastAPI + Pyzbar (QR reader) + SQLite.\n"
                    f"- **Main Features**: Instant QR validation, PDF metadata consistency checker, Admin review queue.\n"
                    f"- **Advanced Upgrade**: Digital cryptographic signature verification (Ed25519)."
                )
            else:
                return (
                    f"### 3 High-Impact Project Ideas for Your Profile ({primary_stack}) 🚀\n\n"
                    f"Instead of generic portfolio demos, here are 3 production-grade projects tailored to your actual skills:\n\n"
                    f"#### 1. **AI Resume & Internship Match Analyzer** 📄\n"
                    f"- **What it does**: Ingests multi-page PDF resumes, extracts standardized competencies, and computes explainable match percentages against job descriptions.\n"
                    f"- **Why it fits your profile**: Directly leverages your {primary_stack} background and demonstrates full-stack fluency.\n"
                    f"- **Tech Stack**: React (TypeScript) + FastAPI + PostgreSQL/SQLite + Python text processing.\n"
                    f"- **Main Features**: Drag-and-drop resume ingestion, weighted match engine, dynamic skill-gap visualizations.\n"
                    f"- **Difficulty**: Intermediate | **What You'll Learn**: RESTful API design, complex scoring algorithms, clean state management.\n"
                    f"- **Resume Impact**: Exceptional — Demonstrates product engineering solving real-world hiring workflows.\n"
                    f"- **Optional Advanced Feature**: Integrate semantic vector embeddings for semantic skill matching.\n\n"
                    f"#### 2. **Cloud-Native Distributed Task Queue & Rate Limiter** ☁️\n"
                    f"- **What it does**: High-throughput microservice handling async background tasks (batch PDF processing, emails) with token-bucket rate limiting.\n"
                    f"- **Why it fits**: Bridges the gap for backend and DevOps roles by proving concurrency mastery.\n"
                    f"- **Tech Stack**: Python (FastAPI) + Redis + Docker + AWS S3.\n"
                    f"- **Main Features**: Sliding window rate limiter, Redis pub/sub queue, worker auto-retry logic.\n"
                    f"- **Difficulty**: Intermediate-Advanced | **What You'll Learn**: Containerization, caching architectures, distributed systems concepts.\n"
                    f"- **Optional Advanced Feature**: Automated GitHub Actions CI/CD deploying multi-container services to AWS.\n\n"
                    f"#### 3. **Tamper-Proof Institutional Credential Verification Portal** 🛡️\n"
                    f"- **What it does**: Multi-tier document integrity system verifying QR payloads, SHA-256 fingerprints, and detecting PDF typography tampering.\n"
                    f"- **Why it fits**: Direct alignment with EdTech and FinTech security standards.\n"
                    f"- **Tech Stack**: React + FastAPI + OpenCV/Pyzbar + SQLite.\n"
                    f"- **Main Features**: QR payload validation, cryptographic hash checks, admin audit review workflow.\n"
                    f"- **Optional Advanced Feature**: Asymmetric digital signatures (Ed25519 public/private keys)."
                )

        # -------------------------------------------------------------
        # Intent 3: BUSINESS OPPORTUNITIES ("Mere skills se kya business?")
        # -------------------------------------------------------------
        elif intent == "business":
            if lang == "hi":
                return (
                    f"### {student_name}, आपकी स्किल्स से कॉलेज स्तर पर वास्तविक बिजनेस अवसर 💼\n\n"
                    f"एक कॉलेज छात्र के रूप में आपको किसी बड़े फंडेड स्टार्टअप की नहीं, बल्कि एक छोटे, व्यावहारिक MVP (Micro-SaaS या सर्विस) से शुरुआत करनी चाहिए:\n\n"
                    f"#### 1. **कॉलेज प्लेसमेंट सेल के लिए 'Automated Resume Shortlister' (B2B SaaS)**\n"
                    f"- **समस्या**: कॉलेज TPO को 500+ छात्रों के रिज्यूमे कंपनियों के क्राइटेरिया के अनुसार मैन्युअली छांटने में हफ्तों लगते हैं।\n"
                    f"- **टारगेट कस्टमर**: आपका खुद का कॉलेज TPO और आसपास के 5 इंजीनियरिंग कॉलेज।\n"
                    f"- **कौशल मेल**: आपकी {primary_stack} स्किल्स इस टूल को 2 सप्ताह में बनाने के लिए पर्याप्त हैं।\n"
                    f"- **MVP फीचर्स**: बैच रिज्यूमे अपलोड, CGPA और अनिवार्य स्किल्स फिल्टर, एक्सेल रिपोर्ट एक्सपोर्ट।\n"
                    f"- **शुरुआत कैसे करें**: अपने कॉलेज प्लेसमेंट ऑफिसर को फ्री में यह टूल इस्तेमाल करने दें, फीडबैक लें और 15-20 छात्रों पर टेस्ट करें।\n"
                    f"- **कमाई का मॉडल**: ₹5,000 - ₹15,000 प्रति प्लेसमेंट ड्राइव या वार्षिक कॉलेज सब्सक्रिप्शन।\n\n"
                    f"#### 2. **लोकल कोचिंग व इवेंट्स के लिए 'QR-Verified Certificate SaaS'**\n"
                    f"- **समस्या**: हैकाथॉन, कार्यशालाएं और स्थानीय संस्थान बिना किसी वेरिफिकेशन वाले साधारण PDF बांटते हैं जो आसानी से नकली बन जाते हैं।\n"
                    f"- **टारगेट कस्टमर**: कॉलेज क्लब, हैकाथॉन आयोजक, और स्थानीय टेक ट्रेनिंग संस्थान।\n"
                    f"- **MVP फीचर्स**: एक्सेल से सर्टिफिकेट जनरेटर, हर सर्टिफिकेट पर डायनामिक QR कोड, लाइव वेरिफिकेशन वेबपेज।\n"
                    f"- **कमाई का मॉडल**: ₹5 - ₹10 प्रति जारी किया गया सर्टिफिकेट (Pay-per-generation)।\n\n"
                    f"#### 3. **अर्ली-स्टेज स्टार्टअप्स के लिए 'FastAPI & Cloud Deployment' फ्रीलांस सर्विस**\n"
                    f"- **समस्या**: कई शुरुआती फाउंडर्स React ऐप बना लेते हैं पर उन्हें सुरक्षित बैकएंड, ऑथेंटिकेशन और AWS डिप्लॉयमेंट की ज़रूरत होती है।\n"
                    f"- **कमाई**: ₹15,000 - ₹35,000 प्रति प्रोजेक्ट (Upwork / Twitter / LinkedIn outreach)।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, aapke skills ({primary_stack}) se realistic business opportunities 💼\n\n"
                    f"College student ke perspective se best approach ye hai: **Project → MVP → 5-20 Users → Micro-SaaS/Service**:\n\n"
                    f"#### 1. **Campus Placement Automation Tool (B2B Micro-SaaS)** 🏫\n"
                    f"- **Problem**: College TPOs aur student coordinators 500+ student resumes ko company criteria (e.g. 8+ CGPA, Python, Docker) ke according manually filter karte hain jo bohot messy hota hai.\n"
                    f"- **Target Users**: Aapke college ke TPO, Department HODs, aur nearby tier-2/3 engineering colleges.\n"
                    f"- **Why your skills fit**: FastAPI + React + SQLite se aap bulk PDF parser aur matching filter 10 din me develop kar sakte ho.\n"
                    f"- **MVP Features**: Bulk resume ZIP upload, automated skill match score, 1-click shortlist Excel download.\n"
                    f"- **How to start small**: Apne college TPO ko free demo do. Unke 1 placement cycle me 20 students ka data run karke time save karke dikhao.\n"
                    f"- **Monetization**: ₹10,000 - ₹25,000 per college per placement season.\n\n"
                    f"#### 2. **Tamper-Proof Certificate Generator for Hackathons & Clubs** 📜\n"
                    f"- **Problem**: College events aur local tech bootcamps fake certificates ke risk se pareshan rehte hain.\n"
                    f"- **Target Users**: College Tech Fests, IEEE/CSI Student Chapters, Local EdTech institutes.\n"
                    f"- **MVP Features**: Upload CSV of winners → Generate PDFs with tamper-proof QR code + verification link.\n"
                    f"- **Monetization**: ₹3 - ₹8 per certificate issued ya ₹3,000 per hackathon package.\n\n"
                    f"#### 3. **Cloud & API Setup Freelance Studio for Early Startups** ⚙️\n"
                    f"- **Problem**: Non-technical ya junior founders frontend bana lete hain par unhe production-ready FastAPI backend, Docker aur AWS setup me help chahiye hoti hai.\n"
                    f"- **How to start**: LinkedIn aur Twitter par apne projects ke deployment videos share karein.\n"
                    f"- **Pricing**: ₹15,000 - ₹30,000 per microservice setup."
                )
            else:
                return (
                    f"### Realistic Business & Monetization Opportunities for Your Profile 💼\n\n"
                    f"From a college student's perspective, focus on low-overhead, high-utility micro-products: **Project → MVP → 10-20 Real Users → Micro-SaaS / Consulting**:\n\n"
                    f"#### 1. **College Placement Automation & Candidate Filtering Tool (B2B Micro-SaaS)** 🏫\n"
                    f"- **Problem Solved**: Campus Placement Offices (TPOs) spend tens of hours manually cross-checking hundreds of student resumes against recruiter eligibility criteria.\n"
                    f"- **Target Users**: Your own college TPO department, nearby colleges, and placement student coordinators.\n"
                    f"- **Why Your Skills Fit**: Your proficiency in {primary_stack} allows building a fast PDF parser and filtering interface in 1-2 weeks.\n"
                    f"- **MVP Features**: Bulk resume upload, automated skill tagging, eligibility filter, and exportable shortlist CSV.\n"
                    f"- **How to Start Small**: Deploy a free prototype for your own department's placement drive. Validate with 25-50 student resumes.\n"
                    f"- **Monetization Model**: ₹10,000 – ₹25,000 per placement season per institution.\n\n"
                    f"#### 2. **Digital Credential & Tamper-Proof Certificate API** 📜\n"
                    f"- **Problem Solved**: Local training institutes, hackathons, and university fests need tamper-proof verification without paying high enterprise fees.\n"
                    f"- **Target Users**: Hackathon organizing teams, college clubs, local private bootcamps.\n"
                    f"- **MVP Features**: Batch PDF generation, dynamic signed QR codes, and a public `/verify/:id` endpoint.\n"
                    f"- **Monetization Model**: ₹5 – ₹10 per verified credential issued, or flat event licenses.\n\n"
                    f"#### 3. **FastAPI Backend & Cloud Architecture Consulting for Early Startups** ⚙️\n"
                    f"- **Problem Solved**: Early-stage founders have React/Next.js MVPs but lack production-ready, Dockerized backends and secure database models.\n"
                    f"- **Monetization**: ₹15,000 – ₹40,000 per client integration."
                )

        # -------------------------------------------------------------
        # Intent 4: CAREER / JOB ROLES ("Which roles fit my profile?")
        # -------------------------------------------------------------
        elif intent == "career_roles":
            if lang == "hi":
                return (
                    f"### {student_name}, आपकी वर्तमान प्रोफाइल के लिए उपयुक्त करियर रोल्स 🎯\n\n"
                    f"आपकी वेरिफाइड स्किल्स ({primary_stack}) और **{readiness}%** रेडीनेस के आधार पर:\n\n"
                    f"#### 1. **Backend Software Engineer (Python / FastAPI)** 🥇\n"
                    f"- **क्यों फिट बैठता है**: आप APIs और डेटाबेस के साथ सहज हैं।\n"
                    f"- **मौजूदा ताकत**: Python, FastAPI, REST आर्किटेक्चर।\n"
                    f"- **क्या मिसिंग है**: Redis कैशिंग और हाई-कंकरेंसी सिस्टम डिजाइन।\n"
                    f"- **अगला कदम**: एक एंड-टू-एंड माइक्रोसर्विस बनाकर GitHub पर शेयर करें।\n\n"
                    f"#### 2. **Cloud & DevOps Engineer Intern** 🥈\n"
                    f"- **क्यों फिट बैठता है**: आपके पास क्लाउड और डॉकर की समझ है।\n"
                    f"- **मौजूदा ताकत**: AWS और कंटेनराइज़ेशन।\n"
                    f"- **क्या मिसिंग है**: CI/CD ऑटोमेशन (GitHub Actions) और कुबरनेट्स (Kubernetes)।\n\n"
                    f"#### 3. **Full-Stack Developer (React + Python)** 🥉\n"
                    f"- **क्यों फिट बैठता है**: फ्रंटएंड और बैकएंड दोनों को जोड़ने की क्षमता।\n"
                    f"- **सुझाव**: एक मजबूत फुल-स्टैक प्रोजेक्ट आपके प्रोफाइल को तुरंत शॉर्टलिस्ट कराएगा।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, aapki profile ke liye top career roles 🎯\n\n"
                    f"Aapke verified competencies ({primary_stack}) aur **{readiness}%** readiness ke base par ye roles best match hain:\n\n"
                    f"#### 1. **Backend Software Engineer Intern (Python / FastAPI)** 🥇\n"
                    f"- **Why it fits**: Core backend, REST APIs aur relational database setup me aapka strong hold hai.\n"
                    f"- **Current Strengths**: FastAPI routing, Pydantic data validation, PostgreSQL/SQLite ORM.\n"
                    f"- **Missing Skills to Add**: Redis caching aur async worker queues.\n"
                    f"- **Recommended Project**: Multi-tenant authentication API with rate limiting.\n\n"
                    f"#### 2. **Cloud / DevOps Engineer Intern** 🥈\n"
                    f"- **Why it fits**: AWS aur Docker certification credentials se aapko initial shortlist advantage milta hai.\n"
                    f"- **Current Strengths**: Containerization basics, cloud hosting concepts.\n"
                    f"- **Missing Skills to Add**: CI/CD automation pipelines aur basic Kubernetes orchestration.\n\n"
                    f"#### 3. **Full-Stack Web Developer Intern** 🥉\n"
                    f"- **Why it fits**: React frontend + Python backend integration capability.\n"
                    f"- **Next Step**: State management (Zustand/Redux) aur responsive design portfolio build karein."
                )
            else:
                return (
                    f"### Ideal Career & Internship Roles for Your Profile 🎯\n\n"
                    f"Based on your competencies ({primary_stack}) and **{readiness}%** placement readiness index:\n\n"
                    f"#### 1. **Backend Software Engineer Intern** (Match: 85-90%) 🥇\n"
                    f"- **Why It Fits**: Direct alignment with your Python and FastAPI backend foundations.\n"
                    f"- **Current Strengths**: REST API architecture, schema validation, and SQL persistence.\n"
                    f"- **Missing Skills to Bridge**: In-memory caching (Redis) and asynchronous task execution.\n"
                    f"- **Target Next Action**: Build a microservice with rate limiting and database indexing.\n\n"
                    f"#### 2. **Cloud & Platform Operations Intern** (Match: 75-80%) 🥈\n"
                    f"- **Why It Fits**: Supported by your verified cloud credentials and containerization knowledge.\n"
                    f"- **Current Strengths**: Docker image creation, AWS deployment fundamentals.\n"
                    f"- **Missing Skills to Bridge**: GitHub Actions CI/CD workflows and Kubernetes pods/services.\n\n"
                    f"#### 3. **Full-Stack Engineering Intern** (Match: 70-75%) 🥉\n"
                    f"- **Why It Fits**: Combines React client engineering with backend data endpoints."
                )

        # -------------------------------------------------------------
        # Intent 5: SKILL GAPS ("What skills am I missing?")
        # -------------------------------------------------------------
        elif intent == "skill_gap":
            if lang == "hi":
                return (
                    f"### {student_name}, आपकी प्रोफाइल में मुख्य स्किल गैप्स 🔍\n\n"
                    f"CareerLens पर उपलब्ध शीर्ष इंटर्नशिप्स (TechCorp, ScalePeak, InnovateX) के आधार पर आपके मुख्य गैप्स ये हैं:\n\n"
                    f"1. **Redis (Production Caching & Message Broker)**\n"
                    f"   - **वर्तमान स्थिति**: Python/FastAPI आता है, लेकिन इन-मेमोरी कैशिंग मिसिंग है।\n"
                    f"   - **यह क्यों आवश्यक है**: 80% बैकएंड इंटरव्यूज में लेटेंसी कम करने और सेशन मैनेजमेंट के लिए Redis पूछा जाता है।\n"
                    f"   - **कैसे सीखें**: 3-दिन का हैंड्स-ऑन ट्यूटोरियल करें और अपने किसी भी API में 60-सेकंड कैशिंग लगाएं।\n\n"
                    f"2. **CI/CD ऑटोमेशन (GitHub Actions)**\n"
                    f"   - **वर्तमान स्थिति**: कोड लिखना आता है, पर ऑटोमेटेड टेस्टिंग और डिप्लॉयमेंट पाइपलाइन नहीं बनी है।\n"
                    f"   - **यह क्यों आवश्यक है**: आधुनिक इंजीनियरिंग टीमें बिना CI/CD के काम नहीं करतीं।\n"
                    f"   - **अभ्यास**: अपने GitHub रिपॉजिटरी में `.github/workflows/test.yml` जोड़ें।\n\n"
                    f"3. **Next.js / SSR (Frontend विस्तार)**\n"
                    f"   - **यह क्यों आवश्यक है**: यदि आप फुल-स्टैक रोल्स चाहते हैं, तो React के साथ Next.js 14 App Router का ज्ञान मैच स्कोर 15% बढ़ा देगा।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, aapke profile ke top skill gaps 🔍\n\n"
                    f"CareerLens ke active jobs data ke according, 90%+ match score pane ke liye ye skills bridge karein:\n\n"
                    f"1. **Redis (In-Memory Caching & Session Store)**\n"
                    f"   - **Current Skill**: Python + FastAPI ORM.\n"
                    f"   - **Missing Skill**: Fast in-memory caching.\n"
                    f"   - **Why it matters**: Recruiters latency reduction aur database load optimization ke questions zaroor puchte hain.\n"
                    f"   - **How to learn**: FastAPI me `aioredis` integrate karke DB queries ka response time 100ms se 5ms par laayein.\n\n"
                    f"2. **CI/CD Pipelines (GitHub Actions)**\n"
                    f"   - **Current Skill**: Git / GitHub basics.\n"
                    f"   - **Missing Skill**: Automated testing on pull requests.\n"
                    f"   - **Practice**: Apne repo me pytest runs aur Docker build automated workflow setup karein.\n\n"
                    f"3. **Production Container Orchestration (Docker Compose)**\n"
                    f"   - **Next step**: Frontend, Backend aur Database ko ek single `docker-compose up` se spin up karna sikhein."
                )
            else:
                return (
                    f"### Key Skill Gaps to Bridge for Maximum Internship Matching 🔍\n\n"
                    f"Analyzing your active candidate profile against active CareerLens opportunities:\n\n"
                    f"1. **In-Memory Caching & Queues (Redis)**\n"
                    f"   - **Current Competency**: REST APIs & Database ORM.\n"
                    f"   - **The Gap**: High-concurrency caching and transient state management.\n"
                    f"   - **Why It Matters**: Evaluated heavily in backend technical rounds for response latency optimization.\n"
                    f"   - **How to Learn**: Implement a 5-minute Redis response cache on frequent query endpoints in FastAPI.\n\n"
                    f"2. **Continuous Integration & Delivery (CI/CD)**\n"
                    f"   - **Current Competency**: Version control with Git.\n"
                    f"   - **The Gap**: Automated test runners and build verification pipelines.\n"
                    f"   - **How to Learn**: Create a GitHub Actions workflow running Pytest and lint checks on every commit.\n\n"
                    f"3. **Microservices Containerization (Docker Compose)**\n"
                    f"   - **Action**: Bundle your frontend, backend API, and database into a unified multi-container setup."
                )

        # -------------------------------------------------------------
        # Intent 6: LEARNING ROADMAP ("Give me a roadmap / How to learn?")
        # -------------------------------------------------------------
        elif intent == "roadmap":
            if lang == "hi":
                return (
                    f"### {student_name}, 4-सप्ताह का व्यावहारिक प्लेसमेंट रेडीनेस रोडमैप 📅\n\n"
                    f"यह रोडमैप आपकी वर्तमान स्किल्स ({primary_stack}) को मजबूत करते हुए मिसिंग स्किल्स को जोड़ेगा:\n\n"
                    f"• **सप्ताह 1: कोर फंडामेंटल्स और आर्किटेक्चर**\n"
                    f"  - REST API लाइफसाइकिल, स्टेटस कोड्स, और इनपुट वैलिडेशन।\n"
                    f"  - SQL इंडेक्सिंग, जॉइन्स, और ट्रांजेक्शन आइसोलेशन लेवल्स।\n\n"
                    f"• **सप्ताह 2: एडवांस बैकएंड व कैशिंग (Redis)**\n"
                    f"  - Redis इंस्टॉल करें और की-वैल्यू पेयर्स, TTL और इन-मेमोरी कैशिंग सीखें।\n"
                    f"  - FastAPI में JWT बेस्ड ऑथेंटिकेशन और रोल-बेस्ड एक्सेस कंट्रोल (RBAC) लागू करें।\n\n"
                    f"• **सप्ताह 3: प्रोडक्शन-रेडी प्रोजेक्ट निर्माण**\n"
                    f"  - एक एंड-टू-एंड प्रोजेक्ट बनाएं (जैसे AI Resume Matcher या Credential Verifier)।\n"
                    f"  - React फ्रंटएंड को अपने बैकएंड के साथ जोड़ें और लोडिंग/एरर स्टेट्स हैंडल करें।\n\n"
                    f"• **सप्ताह 4: कंटेनराइजेशन और इंटरव्यू की तैयारी**\n"
                    f"  - प्रोजेक्ट को Dockerfile और Docker Compose से पैकेज करें।\n"
                    f"  - GitHub पर विस्तृत README, आर्किटेक्चर डायग्राम, और लाइव डेमो लिंक जोड़ें।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, 4-Week Actionable Placement Roadmap 📅\n\n"
                    f"Aapki current profile ko **{readiness}%** se 95%+ par le jane ka exact sprint plan:\n\n"
                    f"• **Week 1: Core Systems & Database Mastery**\n"
                    f"  - SQL Indexing, foreign keys, and query optimization.\n"
                    f"  - FastAPI dependency injection, error handling middleware, and clean schemas.\n\n"
                    f"• **Week 2: Advanced Backend & Caching (Redis)**\n"
                    f"  - Redis setup karein, caching patterns (Cache-Aside) implement karein.\n"
                    f"  - JWT authentication with secure password hashing (bcrypt) aur token expiration.\n\n"
                    f"• **Week 3: High-Impact Portfolio Project**\n"
                    f"  - Real-world project banayein (e.g. AI Resume Analyzer ya Document Verification Portal).\n"
                    f"  - React UI integrate karein with clean error toasts aur loading skeletons.\n\n"
                    f"• **Week 4: Deployment & System Design Rounds**\n"
                    f"  - Dockerfile likhkar services containerize karein.\n"
                    f"  - System Design questions practice karein: Rate limiting, Database scaling, Caching trade-offs."
                )
            else:
                return (
                    f"### 4-Week Engineering Placement Sprint Roadmap 📅\n\n"
                    f"Designed to advance your profile from **{readiness}%** to top-tier placement readiness:\n\n"
                    f"• **Week 1: Core Fundamentals & API Architecture**\n"
                    f"  - Deep dive into REST constraints, idempotent methods, and HTTP status handling.\n"
                    f"  - SQL schema normalization, indexes, and connection pooling.\n\n"
                    f"• **Week 2: Intermediate Systems & Caching (Redis)**\n"
                    f"  - Setup Redis for session management and cache-aside patterns.\n"
                    f"  - Implement robust JWT authentication with RBAC guards.\n\n"
                    f"• **Week 3: Capstone Product Development**\n"
                    f"  - Build a cohesive full-stack application (e.g., AI Resume Matcher or Verification Portal).\n"
                    f"  - Ensure clean modular code separation between API, database, and client layers.\n\n"
                    f"• **Week 4: Containerization, Cloud & Interview Prep**\n"
                    f"  - Package the full stack using Docker and Docker Compose.\n"
                    f"  - Review technical interview topics: architectural trade-offs, caching, and concurrency."
                )

        # -------------------------------------------------------------
        # Intent 7: READINESS SCORE EXPLANATION ("Why is my readiness score?")
        # -------------------------------------------------------------
        elif intent == "readiness_score":
            if lang == "hi":
                return (
                    f"### {student_name}, आपका प्लेसमेंट रेडीनेस इंडेक्स: **{readiness}%** 📊\n\n"
                    f"आपकी प्रोफाइल का वर्तमान रेडीनेस स्कोर **{readiness}%** है। यह स्कोर 4 मुख्य घटकों से तय होता है:\n\n"
                    f"1. **सत्यापित प्रमाणपत्र (Verified Credentials)**: आपके पास वेरिफाइड सर्टिफिकेट्स हैं, जिसने आपके स्कोर में बड़ा योगदान दिया है।\n"
                    f"2. **स्किल्स की चौड़ाई और गहराई**: आपके पास {len(all_skills)} लिस्टेड स्किल्स हैं (जैसे {primary_stack})।\n"
                    f"3. **रिज्यूमे और प्रोफाइल पूर्णता**: आपका रिज्यूमे पार्स हो चुका है और प्रोफाइल एक्टिव है।\n"
                    f"4. **अकादमिक प्रोफाइल**: आपका CGPA और इंजीनियरिंग बैकग्राउंड अच्छा आधार प्रदान करता है।\n\n"
                    f"🚀 **इसे 95%+ तक कैसे ले जाएं?**\n"
                    f"• Redis या Kubernetes जैसी मिसिंग स्किल्स का एक लाइव प्रोजेक्ट बनाएं।\n"
                    f"• अपने प्रोजेक्ट्स को गिटहब और लाइव डिप्लॉयमेंट लिंक से जोड़ें।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, aapka Placement Readiness Index: **{readiness}%** 📊\n\n"
                    f"Aapki profile ka live score exactly **{readiness}%** hai. Iska breakdown ye hai:\n\n"
                    f"• **Verified Credentials**: Aapke official verified certificates (Gold/Silver) ne aapko solid credibility boost diya hai.\n"
                    f"• **Skill Breadth**: Aapke paas {len(all_skills)} relevant tech skills mapped hain ({primary_stack}).\n"
                    f"• **Resume Completeness**: Uploaded resume aur parsed technical profile active hai.\n"
                    f"• **Academic Fit**: Good engineering baseline CGPA.\n\n"
                    f"📈 **Score ko 95%+ boost karne ke 2 steps**:\n"
                    f"1. Redis aur Docker integration ka ek live demo project GitHub par attach karein.\n"
                    f"2. Ek additional cloud certification upload karke Gold verification earn karein."
                )
            else:
                return (
                    f"### Understanding Your Placement Readiness Index: **{readiness}%** 📊\n\n"
                    f"Your live Career Readiness Score stands exactly at **{readiness}%**. Here is how this score is structured:\n\n"
                    f"1. **Verified Credentials**: Official institutional certificates (Gold/Silver badges) with verified cryptographic authenticity.\n"
                    f"2. **Skill Competency**: {len(all_skills)} categorized skills ({primary_stack}).\n"
                    f"3. **Resume Completeness**: Ingested resume profile with technical project experience.\n"
                    f"4. **Academic Baseline**: Department alignment and strong academic GPA.\n\n"
                    f"💡 **To reach 95%+ readiness**: Bridge critical gap skills (Redis, CI/CD) with a live deployed repository."
                )

        # -------------------------------------------------------------
        # Intent 8: INTERNSHIPS & MATCHES
        # -------------------------------------------------------------
        elif intent == "internships":
            if lang == "hi":
                return (
                    f"### {student_name}, इंटर्नशिप मैच स्कोर और रणनीति 🎯\n\n"
                    f"CareerLens पर आपका वर्तमान रेडीनेस स्कोर **{readiness}%** है:\n\n"
                    f"• **टॉप मैचिंग इंटर्नशिप**: क्लाउड और बैकएंड सॉफ्टवेयर इंजीनियर रोल्स में आपका मैच 75%-80% से ऊपर है क्योंकि आपकी प्रमाणित स्किल्स ({primary_stack}) जॉब की अनिवार्य आवश्यकताओं से मेल खाती हैं।\n"
                    f"• **मैच स्कोर कम क्यों होता है?**: जब जॉब डिस्क्रिप्शन में ऐसी तकनीकें (जैसे Redis, Kubernetes, Next.js) अनिवार्य होती हैं जो आपके प्रोफाइल में अभी वेरिफाइड नहीं हैं।\n"
                    f"• **स्कोर कैसे बढ़ाएं?**:\n"
                    f"  1. अनिवार्य गैप स्किल्स का 1 प्रोजेक्ट बनाएं।\n"
                    f"  2. गोल्ड बैज वाले वेरिफाइड सर्टिफ़िकेट अपलोड करें (वेरिफाइड स्किल्स को 2.5 गुना ज्यादा वेटेज मिलता है)।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, Internship Match Analysis & Score Boost 🚀\n\n"
                    f"Aapki current readiness **{readiness}%** hai aur CareerLens par match optimization ye hai:\n\n"
                    f"• **Top Matches**: Backend Software Engineer aur Cloud Internships me aapka match 75-80%+ hai kyunki aapke verified skills ({primary_stack}) required stack se match karte hain.\n"
                    f"• **Why some matches are lower**: TechCorp aur ScalePeak jaise roles me mandatory skills jaise Redis aur CI/CD pipelines required hain jo abhi aapke profile me pending hain.\n"
                    f"• **90%+ Boost Strategy**:\n"
                    f"  1. Missing skill ka targeted 1-week sprint complete karein.\n"
                    f"  2. Official certificates verify karwayein jisse recruiter portal me aapki profile top tier par feature ho."
                )
            else:
                return (
                    f"### Internship Matching & Score Optimization for Your Profile 🎯\n\n"
                    f"Your live placement readiness score is **{readiness}%**:\n\n"
                    f"• **Strongest Matches**: Backend Software Engineering and Cloud Operations (75-80%+ fit) supported by your {primary_stack} competencies.\n"
                    f"• **Why Some Matches Have Gaps**: Opportunities targeting distributed systems require secondary competencies (e.g. Redis, CI/CD).\n"
                    f"• **How to Maximize Your Match**:\n"
                    f"  1. Bridge secondary requirements via hands-on project artifacts.\n"
                    f"  2. Maintain Gold verified credentials which carry automated trust multipliers for recruiters."
                )

        # -------------------------------------------------------------
        # Intent 9: RESUME ADVICE
        # -------------------------------------------------------------
        elif intent == "resume":
            if lang == "hi":
                return (
                    f"### {student_name}, रिज्यूमे को सशक्त बनाने के 3 मुख्य सुझाव 📄\n\n"
                    f"आपकी प्रोफाइल और **{readiness}%** रेडीनेस के आधार पर:\n\n"
                    f"1. **प्रोजेक्ट बुलेट्स में संख्यात्मक परिणाम लिखें**:\n"
                    f"   - साधारण: *'FastAPI से बैकएंड बनाया।'* ❌\n"
                    f"   - प्रभावशाली: *'FastAPI और Redis से 15+ REST APIs विकसित कीं, जिससे रिस्पॉन्स लेटेंसी 35% घटी और 99.9% अपटाइम मिला।'* ✅\n"
                    f"2. **सत्यापित बैज हाइलाइट करें**: रिज्यूमे में अपने गोल्ड बैज वाले सर्टिफ़िकेट्स (AWS, React) के क्रेडेंशियल लिंक्स प्रमुखता से जोड़ें।\n"
                    f"3. **GitHub और लाइव लिंक्स**: हर प्रोजेक्ट का लाइव डेमो और साफ़ README लिंक होना चाहिए।"
                )
            elif lang == "hinglish":
                return (
                    f"### {student_name}, Resume Review & Impact Suggestions 📄\n\n"
                    f"Aapke **{readiness}%** readiness index ke hisaab se resume ko shortlist-ready banane ke 3 actionable tips:\n\n"
                    f"1. **Action + Metric Bullets**:\n"
                    f"   - Weak: *'Worked on backend and database.'*\n"
                    f"   - Strong: *'Architected FastAPI backend supporting 1,000+ simulated requests/sec with JWT auth and sub-50ms query latency.'*\n"
                    f"2. **Feature Verified Credentials**: Apne Gold Badge credentials (jaise AWS) ko top certifications section me prominent link ke sath showcase karein.\n"
                    f"3. **Skill Categorization**: Languages, Frameworks, Cloud/DevOps, aur Databases ko clearly alag sections me organize karein."
                )
            else:
                return (
                    f"### Resume Enhancement Strategy for Your Profile 📄\n\n"
                    f"Grounded in your technical skill set ({primary_stack}) and **{readiness}%** readiness:\n\n"
                    f"1. **Quantify Engineering Impact**:\n"
                    f"   - Before: *'Built web scraper and database endpoints.'*\n"
                    f"   - After: *'Engineered asynchronous FastAPI ingestion pipeline processing 500+ documents with automated validation and Redis caching.'*\n"
                    f"2. **Highlight Verified Badges**: Feature your Gold Badge credentials at the top of your resume.\n"
                    f"3. **Project Architecture Links**: Provide direct GitHub repository links with clean architecture diagrams and deployment instructions."
                )

        # -------------------------------------------------------------
        # Intent 10: DEFAULT WELCOME & OVERVIEW
        # -------------------------------------------------------------
        else:
            if lang == "hi":
                return (
                    f"नमस्ते {student_name}! CareerLens AI में आपका स्वागत है। 🎓\n\n"
                    f"आपकी प्रोफाइल का लाइव रेडीनेस स्कोर **{readiness}%** है। मैं आपकी प्रमाणित स्किल्स ({primary_stack}) और इंटर्नशिप्स को ध्यान में रखकर सहायता कर सकता हूँ।\n\n"
                    f"आप मुझसे पूछ सकते हैं:\n"
                    f"• *'मेरी स्किल्स के अनुसार 3 प्रोजेक्ट्स बताओ'* 🚀\n"
                    f"• *'मेरी स्किल्स से क्या बिजनेस बना सकता हूँ?'* 💼\n"
                    f"• *'मुझे कौन सी जॉब्स के लिए अप्लाई करना चाहिए?'* 🎯\n"
                    f"• *'मेरा रेडीनेस स्कोर कैसे बढ़ेगा?'* 📈"
                )
            elif lang == "hinglish":
                return (
                    f"Hello {student_name}! CareerLens AI Career Mentor me aapka swagat hai. 🎯\n\n"
                    f"Aapki live Placement Readiness **{readiness}%** hai aur aapke verified skills ({primary_stack}) mapped hain.\n\n"
                    f"Try asking:\n"
                    f"• *'Mere skills ke according 3 projects batao'* 🚀\n"
                    f"• *'Mere skills se kya business bana sakta hoon?'* 💼\n"
                    f"• *'Which career roles fit my profile?'* 🎯\n"
                    f"• *'What should I learn next?'* 📚"
                )
            else:
                return (
                    f"Welcome {student_name} to CareerLens AI Counselor! 🎓\n\n"
                    f"Your live Career Readiness Index is **{readiness}%**. I am directly grounded with your verified credentials ({primary_stack}) and platform opportunities.\n\n"
                    f"Feel free to ask:\n"
                    f"• *'Suggest 3 high-impact projects based on my skills'* 🚀\n"
                    f"• *'What business opportunities can I build with my skills?'* 💼\n"
                    f"• *'Which career roles fit my profile?'* 🎯\n"
                    f"• *'What skills should I learn next?'* 📚"
                )

