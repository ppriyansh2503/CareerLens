import pytest
from app.services.tamper_detector import TamperDetector
from app.services.ocr_service import OCRService
from app.services.qr_scanner import QRScanner

def test_qr_scanner_payload_analysis():
    trusted = QRScanner._analyze_payload("https://aws.amazon.com/verification/AWS-12345")
    assert trusted["qr_found"] is True
    assert trusted["is_trusted_issuer"] is True
    assert trusted["recognized_issuer_domain"] == "aws.amazon.com"

    untrusted = QRScanner._analyze_payload("https://random-unknown-site.xyz/fake")
    assert untrusted["qr_found"] is True
    assert untrusted["is_trusted_issuer"] is False

def test_ocr_entity_parsing():
    sample_text = """
    Certificate of Completion
    This certifies that Aarav Sharma has completed the course
    AWS Certified Developer - Associate
    Issued by Amazon Web Services on January 15, 2026
    Credential ID: AWS-DEV-984210
    """
    res = OCRService.parse_entities(sample_text, student_name="Aarav Sharma")
    assert res["name_found_in_cert"] is True
    assert res["name_match_score"] == 100.0
    assert "Amazon Web Services" in res["issuing_org"] or "AWS" in res["issuing_org"]

def test_tamper_software_detection():
    # Test suspicious software list
    assert "photoshop" in TamperDetector.SUSPICIOUS_SOFTWARE_KEYWORDS
    assert "canva" in TamperDetector.SUSPICIOUS_SOFTWARE_KEYWORDS
