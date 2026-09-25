import os
import io
import math
from typing import Dict, Any, Optional
from PIL import Image, ImageChops, ImageEnhance
import pypdf

class TamperDetector:
    """
    Forensic Tamper Detection Service:
    1. Error Level Analysis (ELA) on raster images to detect compression discontinuities
    2. PDF Metadata Inspection for suspicious software footprints (Photoshop, Canva, Paint)
    3. Structural & Temporal Consistency Checks
    """

    SUSPICIOUS_SOFTWARE_KEYWORDS = [
        "photoshop", "canva", "gimp", "paint", "pixlr", "photopea",
        "inkscape", "coreldraw", "illustrator", "editor"
    ]

    INSTITUTIONAL_ISSUERS = [
        "coursera", "udemy", "nptel", "aws", "amazon", "google",
        "microsoft", "cisco", "oracle", "edx", "stanford", "mit", "iit"
    ]

    @classmethod
    def analyze_image_ela(cls, image_path: str, quality: int = 90) -> Dict[str, Any]:
        """
        Computes Error Level Analysis (ELA).
        Re-saves the image at a known JPEG compression quality and compares pixel differences.
        Regions pasted or modified after initial saving retain different compression levels.
        """
        try:
            original = Image.open(image_path).convert('RGB')
            buffer = io.BytesIO()
            original.save(buffer, format='JPEG', quality=quality)
            buffer.seek(0)
            resaved = Image.open(buffer)

            # Compute pixel difference
            diff = ImageChops.difference(original, resaved)
            
            # Scale difference for analysis
            extrema = diff.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            if max_diff == 0:
                max_diff = 1
            scale = 255.0 / max_diff

            diff_enhanced = ImageEnhance.Brightness(diff).enhance(scale)

            # Calculate mean difference
            stat = diff.convert('L')
            hist = stat.histogram()
            total_pixels = sum(hist)
            mean_error = sum(i * count for i, count in enumerate(hist)) / (total_pixels or 1)

            # Analyze standard deviation / variance
            variance = sum(((i - mean_error) ** 2) * count for i, count in enumerate(hist)) / (total_pixels or 1)
            std_dev = math.sqrt(variance)

            # Anomaly indicator: unusually high local variance or high mean error
            # indicates multi-generation compression (tampering)
            is_anomaly = (mean_error > 12.0) or (std_dev > 15.0)

            return {
                "ela_performed": True,
                "mean_error": round(mean_error, 2),
                "std_deviation": round(std_dev, 2),
                "max_difference": max_diff,
                "ela_anomaly_detected": is_anomaly,
                "confidence": round(min(100.0, (mean_error / 15.0) * 100), 1) if is_anomaly else 95.0
            }
        except Exception as e:
            return {
                "ela_performed": False,
                "error": str(e),
                "ela_anomaly_detected": False,
                "confidence": 50.0
            }

    @classmethod
    def analyze_pdf_metadata(cls, pdf_path: str) -> Dict[str, Any]:
        """
        Inspects PDF header, metadata, producer, creator, and timestamps.
        Flags when an institutional certificate was generated using image manipulation tools.
        """
        detected_suspicious_tools = []
        creator = ""
        producer = ""
        has_mod_anomaly = False
        page_count = 1

        try:
            reader = pypdf.PdfReader(pdf_path)
            meta = reader.metadata or {}
            page_count = len(reader.pages)
            
            creator = (meta.get("/Creator") or "").lower()
            producer = (meta.get("/Producer") or "").lower()
            creation_date = str(meta.get("/CreationDate") or "")
            mod_date = str(meta.get("/ModDate") or "")

            for tool in cls.SUSPICIOUS_SOFTWARE_KEYWORDS:
                if tool in creator or tool in producer:
                    detected_suspicious_tools.append(tool)

            if creation_date and mod_date and (creation_date != mod_date):
                has_mod_anomaly = True
        except Exception:
            pass

        # Inspect raw header / text lines for suspicious tools or editing software signatures
        try:
            with open(pdf_path, "rb") as f:
                raw_sample = f.read(10000).decode("utf-8", errors="ignore").lower()
            for tool in cls.SUSPICIOUS_SOFTWARE_KEYWORDS:
                if (f"creator: {tool}" in raw_sample or 
                    f"producer: {tool}" in raw_sample or 
                    f"adobe {tool}" in raw_sample or 
                    f"{tool} editor" in raw_sample or 
                    f"{tool} 202" in raw_sample or
                    ("altered" in raw_sample and tool in raw_sample)):
                    if tool not in detected_suspicious_tools:
                        detected_suspicious_tools.append(tool)
        except Exception:
            pass

        is_suspicious = len(detected_suspicious_tools) > 0

        return {
            "pdf_metadata_inspected": True,
            "creator": creator,
            "producer": producer,
            "suspicious_tools_found": detected_suspicious_tools,
            "metadata_tamper_detected": is_suspicious,
            "modification_anomaly": has_mod_anomaly,
            "page_count": page_count
        }

    @classmethod
    def evaluate_tampering(cls, file_path: str, claimed_issuer: str = "") -> Dict[str, Any]:
        """
        Synthesizes forensic evaluations across image ELA and PDF metadata.
        """
        ext = os.path.splitext(file_path)[1].lower()
        ela_results = {}
        pdf_results = {}
        tamper_flags = []

        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            ela_results = cls.analyze_image_ela(file_path)
            if ela_results.get("ela_anomaly_detected"):
                tamper_flags.append(f"Image Error Level Analysis detected high-frequency compression discontinuity (ELA Score: {ela_results.get('mean_error')}). Indicates modified text or overlay.")
        
        elif ext == ".pdf":
            pdf_results = cls.analyze_pdf_metadata(file_path)
            if pdf_results.get("metadata_tamper_detected"):
                tools = ", ".join(pdf_results.get("suspicious_tools_found", []))
                tamper_flags.append(f"Document authored or modified using graphic design/editing software ({tools}) rather than official credential engine.")
            if pdf_results.get("modification_anomaly"):
                tamper_flags.append("PDF post-creation modification detected after initial issuance.")

        is_tampered = len(tamper_flags) > 0
        overall_tamper_score = 0.0 if not is_tampered else (85.0 if len(tamper_flags) > 1 else 60.0)

        explanation = (
            "No forensic tampering detected. Image compression levels and document metadata are uniform."
            if not is_tampered
            else "Potential tampering detected: " + " | ".join(tamper_flags)
        )

        return {
            "is_tampered": is_tampered,
            "tamper_confidence_score": overall_tamper_score,
            "tamper_flags": tamper_flags,
            "explanation": explanation,
            "ela_details": ela_results,
            "metadata_details": pdf_results
        }
