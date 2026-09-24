# 4-Tier Credential Verification Engine

CareerLens implements a multi-layer verification protocol to solve certificate fraud:

## Layer 1: Cryptographic Hash Digest (SHA-256)
- Computes SHA-256 fingerprint upon upload.
- Checks database for collision with any certificate uploaded by a different student account.
- **Outcome**: Immediate `FLAGGED` status if a duplicate file is detected.

## Layer 2: 2D QR Code Matrix Validation
- Decodes embedded QR codes using OpenCV `cv2.QRCodeDetector` across images and PDF pages rendered via `pypdfium2`.
- Validates extracted URL against white-listed certificate authorities (`aws.amazon.com`, `coursera.org`, `nptel.ac.in`, `credly.com`, `google.com`).
- **Outcome**: +35 trust points and qualification for **GOLD BADGE**.

## Layer 3: OCR Text & Recipient Entity Extraction
- Extracts raw text using `pdfplumber` / `pypdf` (for PDF certs) and OCR for raster images.
- Parses Course Title, Issuing Authority, Credential ID, and Recipient Name.
- Performs fuzzy string distance matching comparing student's registered full name with certificate name.
- **Outcome**: Prevents using authentic certificates belonging to someone else.

## Layer 4: Forensic Tamper Detection (ELA + Metadata)
- **Error Level Analysis (ELA)**: Resaves image at 90% JPEG quality and analyzes difference extrema. High localized variance indicates edited text or pasted overlays.
- **PDF Metadata Heuristics**: Audits `/Creator` and `/Producer` attributes for image editors (Photoshop, Canva, GIMP).
- **Outcome**: Documents with altered layers or mismatched creation/modification timelines are immediately flagged.
