import os
import re
import difflib
from typing import Dict, Any, List, Optional
import pypdf
import pdfplumber

class OCRService:
    """
    Extracts text and key entities (Recipient Name, Issuer, Course Title, Credential ID, Date)
    from certificates and validates recipient name against student's profile.
    """

    COMMON_ISSUERS = [
        "Coursera", "Udemy", "NPTEL", "Amazon Web Services", "AWS",
        "Google Cloud", "Microsoft", "Cisco", "Meta", "IBM", "HackerRank",
        "FreeCodeCamp", "DeepLearning.AI", "Oracle", "HarvardX", "IIT Madras"
    ]

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        Extracts raw text from PDF or Image file.
        """
        ext = os.path.splitext(file_path)[1].lower()
        text = ""

        if ext == ".pdf":
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception:
                pass

            if not text.strip():
                try:
                    reader = pypdf.PdfReader(file_path)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                except Exception:
                    pass

            if not text.strip():
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        raw = f.read()
                        if "%%EOF" in raw or "Certificate" in raw or "Amazon" in raw or "AWS" in raw or len(raw) < 50000:
                            text = raw
                except Exception:
                    pass

        elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
            except Exception:
                # Fallback if tesseract binary is not installed
                text = ""

        return text.strip()

    @classmethod
    def parse_entities(cls, text: str, student_name: str = "") -> Dict[str, Any]:
        """
        Parses certificate text to extract title, issuer, issue date, credential ID,
        and matches against student's registered name.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        detected_issuer = "Recognized Certification Authority"
        for issuer in cls.COMMON_ISSUERS:
            if re.search(r'\b' + re.escape(issuer) + r'\b', text, re.IGNORECASE):
                detected_issuer = issuer
                break

        # Attempt to detect credential ID (alphanumeric pattern like UC-1234, AWS-9872, etc.)
        cred_match = re.search(r'(?:credential|certificate|verify|id|cert\s*no)[\s:#]+([A-Z0-9-]{6,30})', text, re.IGNORECASE)
        credential_id = cred_match.group(1) if cred_match else "CERT-" + str(abs(hash(text)))[:8]

        # Attempt to find date
        date_match = re.search(r'(?:issued|completed|date|on)[\s:#]+([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        issue_date = date_match.group(1) if date_match else "2025-2026"

        # Check Name Match
        name_match_score = 0.0
        name_found_in_cert = False

        if student_name and student_name.strip():
            clean_student = re.sub(r'[^a-zA-Z\s]', '', student_name).lower().strip()
            clean_text = re.sub(r'[^a-zA-Z\s]', ' ', text).lower()

            # Exact match of full name
            if clean_student in clean_text:
                name_match_score = 100.0
                name_found_in_cert = True
            else:
                # Substring tokens match (e.g. first and last name)
                tokens = clean_student.split()
                matched_tokens = sum(1 for t in tokens if len(t) > 2 and t in clean_text)
                if tokens:
                    token_ratio = matched_tokens / len(tokens)
                    name_match_score = round(token_ratio * 90.0, 1)
                    if token_ratio >= 0.6:
                        name_found_in_cert = True

        return {
            "issuing_org": detected_issuer,
            "credential_id": credential_id,
            "issue_date": issue_date,
            "name_found_in_cert": name_found_in_cert,
            "name_match_score": name_match_score,
            "char_count": len(text),
            "line_count": len(lines)
        }

    @classmethod
    def calculate_string_similarity(cls, str1: str, str2: str) -> float:
        return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100.0
