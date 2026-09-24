import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_cert_images():
    os.makedirs("uploads/certificates", exist_ok=True)
    os.makedirs("uploads/resumes", exist_ok=True)
    
    # 1. Generate Valid Certificate Image
    img = Image.new('RGB', (1000, 700), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Border
    draw.rectangle([(20, 20), (980, 680)], outline=(30, 64, 175), width=8)
    draw.rectangle([(30, 30), (970, 670)], outline=(217, 119, 6), width=3)
    
    # Text
    draw.text((250, 80), "CERTIFICATE OF ACHIEVEMENT", fill=(30, 64, 175))
    draw.text((360, 160), "This is proudly presented to", fill=(100, 116, 139))
    draw.text((340, 220), "Aarav Sharma", fill=(15, 23, 42))
    draw.text((220, 310), "for successfully passing the certification examination for", fill=(71, 85, 105))
    draw.text((260, 360), "AWS Certified Developer - Associate", fill=(180, 83, 9))
    draw.text((280, 430), "Issuing Organization: Amazon Web Services (AWS)", fill=(51, 65, 85))
    draw.text((320, 480), "Credential ID: AWS-DEV-984210", fill=(100, 116, 139))
    draw.text((320, 520), "Issue Date: January 15, 2026", fill=(100, 116, 139))
    draw.text((240, 600), "Verification URL: https://aws.amazon.com/verification/AWS-DEV-984210", fill=(37, 99, 235))
    
    img.save("uploads/certificates/valid_aws_cert.png")

    # 2. Generate Tampered Certificate Image (with high-compression noise overlay to trigger ELA)
    tampered_img = img.copy()
    draw_t = ImageDraw.Draw(tampered_img)
    # Paste a white block over name with mismatched pixel artifacts
    draw_t.rectangle([(300, 210), (700, 270)], fill=(245, 245, 245))
    draw_t.text((320, 225), "Rohan Verma (Altered Name)", fill=(220, 38, 38))
    
    # Intentionally save with high compression multiple times to generate ELA discontinuity
    tampered_img.save("uploads/certificates/tampered_cert.jpg", "JPEG", quality=40)

    print("Sample certificate fixtures created successfully!")

if __name__ == "__main__":
    generate_sample_cert_images()
