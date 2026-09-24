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
You are 'CareerLens AI', an expert career counselor and placement advisor for Indian engineering and college students.
You are empathetic, encouraging, practical, and highly knowledgeable about software engineering, cloud, AI, data science, and tech internships.

Languages supported:
1. English
2. Hindi (हिंदी)
3. Hinglish (colloquial Indian mix of Hindi & English, e.g., "Aapka resume strong hai, but AWS certification se match score boost hoga.")

CRITICAL BEHAVIOR:
- Respond in the SAME language or blend the student used!
  - If user writes in English, reply in crisp professional English.
  - If user writes in Hindi (हिंदी), reply in polite, supportive Hindi.
  - If user writes in Hinglish (e.g. "Mujhe internship kaise milegi?"), reply in natural, friendly Hinglish.
- Ground your advice in the student's actual profile data provided in the context (their verified skills, current readiness score, missing skills).
- Emphasize the importance of VERIFIED skills and tamper-proof certificates over unverified claims.
- Keep answers actionable, concise (under 250 words), and formatted with bullet points.
"""

    @classmethod
    def detect_language(cls, text: str) -> str:
        # Check for Devanagari script (Unicode range 0900-097F)
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        
        # Check for Hinglish keywords
        hinglish_words = [
            "kare", "kaise", "kya", "mera", "meri", "mujhe", "batao", "chahiye",
            "kaunse", "hoga", "karna", "hai", "banna", "mil", "sakta", "bhi"
        ]
        words = text.lower().split()
        match_count = sum(1 for w in words if w in hinglish_words)
        if match_count >= 1:
            return "hinglish"
        
        return "en"

    @classmethod
    def generate_chat_response(
        cls,
        user_message: str,
        student: Optional[StudentProfile] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        detected_lang = cls.detect_language(user_message)

        # Build student context summary
        context_str = ""
        if student:
            verified_skills = [s.skill.name for s in student.skills if s.is_verified and s.skill]
            all_skills = [s.skill.name for s in student.skills if s.skill]
            certs = [f"{c.title} ({c.badge_tier} Badge)" for c in student.certificates if c.verification_status == "VERIFIED"]
            
            context_str = f"""
Student Profile Context:
- Full Name: {student.user.full_name if student.user else 'Student'}
- College: {student.user.college_name if student.user else 'Engineering College'}
- Department: {student.department}, Year: {student.graduation_year}, CGPA: {student.cgpa}
- Placement Readiness Score: {student.placement_readiness_score}%
- Verified Skills (Credibility Gold/Silver): {', '.join(verified_skills) or 'None yet'}
- All Listed Skills: {', '.join(all_skills) or 'None'}
- Verified Certificates: {', '.join(certs) or 'None yet'}
"""

        # Check if Google Gemini API key is configured
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip():
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                full_prompt = f"{cls.SYSTEM_PROMPT}\n\n{context_str}\n\nUser Question: {user_message}\n\nProvide your response:"
                
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=600
                    )
                )
                if response and response.text:
                    return {
                        "content": response.text.strip(),
                        "detected_language": detected_lang,
                        "engine": "google-gemini-2.5"
                    }
            except Exception as e:
                # Log and fallback seamlessly
                print(f"[Gemini AI Service Notice] Falling back to heuristic response engine: {e}")

        # Intelligent offline fallback engine (for hackathon demo reliability)
        response_text = cls._offline_smart_response(user_message, detected_lang, student)
        return {
            "content": response_text,
            "detected_language": detected_lang,
            "engine": "careerlens-heuristic-engine"
        }

    @classmethod
    def _offline_smart_response(
        cls,
        msg: str,
        lang: str,
        student: Optional[StudentProfile] = None
    ) -> str:
        msg_lower = msg.lower()
        student_name = student.user.full_name if (student and student.user) else "Aarav"
        readiness = student.placement_readiness_score if student else 78.0

        if lang == "hi":
            # Hindi responses
            if "resume" in msg_lower or "रिज्यूमे" in msg:
                return (
                    f"नमस्ते {student_name}! आपका वर्तमान प्लेसमेंट रेडीनेस स्कोर **{readiness}%** है।\n\n"
                    "अपने रिज्यूमे को बेहतर बनाने के लिए ये कदम उठाएं:\n"
                    "1. **प्रमाणित स्किल्स जोड़ें**: अपने AWS या React सर्टिफ़िकेट अपलोड करें ताकि आपको 'Gold Badge' मिले। रिक्रूटर्स वेरिफाइड प्रोफाइल्स को 3 गुना ज्यादा प्राथमिकता देते हैं।\n"
                    "2. **इम्पैक्ट मेट्रिक्स**: प्रोजेक्ट्स में सिर्फ तकनीक मत लिखें, परिणाम बताएं (जैसे: 'FastAPI बैकएंड से लेटेंसी 40% घटाई')।\n"
                    "3. **GitHub लिंक्स**: अपने मुख्य प्रोजेक्ट्स के लाइव डेमो और कोड लिंक्स एक्टिव रखें।"
                )
            elif "सर्टिफिकेट" in msg or "वेरिफिकेशन" in msg or "गोल्ड" in msg:
                return (
                    "CareerLens पर **Gold Badge** पाने के लिए:\n\n"
                    "• आधिकारिक संस्थान (Coursera, NPTEL, AWS) का ओरिजिनल PDF अपलोड करें जिसमें QR कोड हो।\n"
                    "• हमारा 4-लेयर वेरिफिकेशन इंजन डिजिटल सिग्नेचर, नाम और ELA टेंपर चेक करके 2 सेकंड में आपको गोल्ड बैज दे देगा!\n"
                    "• यदि कोई बदलाव (Tampering) पाया जाता है, तो सिस्टम उसे तुरंत फ्लैग कर देता है।"
                )
            else:
                return (
                    f"नमस्ते {student_name}! CareerLens AI में आपका स्वागत है।\n\n"
                    f"आपकी प्रोफाइल का रेडीनेस स्कोर **{readiness}%** है। मैं आपको इंटर्नशिप मैचिंग, स्किल-गैप रोडमैप और सर्टिफ़िकेट वेरिफिकेशन में मदद कर सकता हूँ।\n"
                    "आप मुझसे पूछ सकते हैं:\n"
                    "• *'मेरी प्रोफाइल के लिए बेस्ट इंटर्नशिप कौन सी है?'*\n"
                    "• *'रिज्यूमे में कौन सी स्किल्स मिसिंग हैं?'*\n"
                    "• *'इंटरव्यू की तैयारी कैसे करें?'*"
                )

        elif lang == "hinglish":
            # Hinglish responses
            if "resume" in msg_lower:
                return (
                    f"Hey {student_name}! Aapka current Placement Readiness score **{readiness}%** hai. 🚀\n\n"
                    "Resume ko top-tier banane ke liye ye 3 changes karein:\n"
                    "1. **Verified Badges**: Apne original certificates upload karke **Gold Badge** earn karein. Unverified skills ke comparison me recruiters verified candidates ko shortlist karte hain.\n"
                    "2. **Action-Oriented Bullets**: Har project me metrics daalein (e.g., *'Built full-stack app serving 500+ daily users with 99% uptime'*).\n"
                    "3. **Tech Stack Clarity**: Jo skills job description me required hain (like Redis, Docker), unka hands-on proof portfolio me zaroor dikhayein."
                )
            elif "match" in msg_lower or "score" in msg_lower or "boost" in msg_lower:
                return (
                    f"Apna match score 90%+ boost karne ka exact formula ye hai:\n\n"
                    "• **Verified Skill Boost (+45%)**: Cloud & Backend certifications verify karwayein.\n"
                    "• **Skill-Gap Sprint**: Targeted 4-week roadmap follow karke missing skills (jaise Docker & Redis) ka live project banayein.\n"
                    "• **Verified Credential**: Ek bar certificate verify ho gaya, recruiter discovery feed me aapki profile top ranking par show hogi!"
                )
            elif "interview" in msg_lower or "internship" in msg_lower:
                return (
                    f"Internship interviews crack karne ke liye {student_name}, ye roadmap follow karein:\n\n"
                    "1. **Core CS Fundamentals**: Data Structures, OOPs, DBMS concepts aur REST API lifecycle clear rakhein.\n"
                    "2. **Explainable Projects**: Jo projects resume par hain, unke architectural tradeoffs explain karne aane chahiye.\n"
                    "3. **Mock Practice**: Mujhe bol sakte ho 'Mock technical interview start karo' aur hum system design & coding questions practice karenge!"
                )
            else:
                return (
                    f"Hello {student_name}! CareerLens AI Career Counselor me aapka swagat hai. 🎯\n\n"
                    f"Aapki current readiness **{readiness}%** hai. Main aapko internship matching, certificate verification aur skill roadmap me help kar sakta hu.\n\n"
                    "Try asking:\n"
                    "• *'Mera match score 95% kaise hoga?'*\n"
                    "• *'Cloud engineer internship ke liye kaunse skills chahiye?'*\n"
                    "• *'Why is my certificate Silver instead of Gold?'*"
                )

        else:
            # English responses
            if "resume" in msg_lower:
                return (
                    f"Hello {student_name}! Your current Career Readiness Index is **{readiness}%**.\n\n"
                    "Here are 3 high-impact recommendations to elevate your profile:\n"
                    "1. **Earn Gold Verification Badges**: Back your claimed skills with official certificates. Verified skills carry a 2.5x multiplier in recruiter searches.\n"
                    "2. **Quantify Project Impact**: Use metrics (e.g. *'Reduced API response latency by 35% using Redis caching'*).\n"
                    "3. **Target Gap Skills**: Bridge missing requirements highlighted in your internship match breakdown."
                )
            elif "match" in msg_lower or "score" in msg_lower or "internship" in msg_lower:
                return (
                    f"To maximize your internship match score at companies like TechCorp or CloudScale:\n\n"
                    "• **Verified Competencies (45% weight)**: Official credentials directly contribute to verified skill points.\n"
                    "• **4-Week Actionable Sprint**: Complete the guided roadmap for missing skills (such as Kubernetes or Redis).\n"
                    "• **Recruiter Visibility**: Profiles with 2+ Gold Badges get automatically featured on the Company Discovery Portal."
                )
            else:
                return (
                    f"Welcome {student_name} to CareerLens AI Counselor! 🎓\n\n"
                    f"Your current readiness score is **{readiness}%**. I am grounded with your verified credentials, skill breakdown, and matching internship listings.\n\n"
                    "Feel free to ask me:\n"
                    "• *'How can I bridge my skill gaps for Cloud Engineering?'*\n"
                    "• *'Review my resume for full-stack developer roles'*\n"
                    "• *'What is the difference between Gold and Silver credential badges?'*"
                )
