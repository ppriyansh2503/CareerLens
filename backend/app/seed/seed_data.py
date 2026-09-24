from datetime import datetime
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.student import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.models.certificate import Certificate
from app.models.job import Job, JobSkill
from app.services.skill_service import get_or_create_skill

def seed_database_if_empty(db: Session):
    # 1. Seed Skills (idempotently)
    skill_definitions = [
        ("Python", "backend"),
        ("FastAPI", "backend"),
        ("Django", "backend"),
        ("Node.js", "backend"),
        ("Go (Golang)", "backend"),
        ("Java", "backend"),
        ("REST APIs", "backend"),
        ("React", "frontend"),
        ("Next.js", "frontend"),
        ("TypeScript", "frontend"),
        ("JavaScript", "frontend"),
        ("Tailwind CSS", "frontend"),
        ("PostgreSQL", "database"),
        ("MongoDB", "database"),
        ("Redis", "database"),
        ("SQLite", "database"),
        ("AWS", "cloud"),
        ("Docker", "cloud"),
        ("Kubernetes", "cloud"),
        ("CI/CD Pipelines", "cloud"),
        ("Git / GitHub", "cloud"),
        ("Machine Learning", "ml_ai"),
        ("Deep Learning", "ml_ai"),
        ("PyTorch", "ml_ai"),
        ("Natural Language Processing", "ml_ai"),
    ]

    skill_objs = {}
    for name, cat in skill_definitions:
        skill = get_or_create_skill(db, name, category=cat)
        skill_objs[name] = skill

    # 2. Check if demo accounts are already seeded
    demo_student = db.query(User).filter(User.email == "student@careerlens.io").first()
    if demo_student:
        return  # Demo accounts already seeded

    print("[CareerLens Seed] Seeding database with realistic demo accounts, skills, and internships...")

    # 2. Seed Users
    hashed_pwd = get_password_hash("password123")

    # Demo Student 1: Aarav Sharma (Gold Badge Student)
    student_user = User(
        email="student@careerlens.io",
        password_hash=hashed_pwd,
        full_name="Aarav Sharma",
        role="student",
        college_name="Indian Institute of Information Technology (IIIT)"
    )
    db.add(student_user)
    db.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        headline="Aspiring Cloud & Backend Engineer | 8th Sem CSE",
        bio="Passionate about distributed backend architectures, FastAPI, and AWS. Certified AWS Developer with hands-on containerization experience.",
        github_url="https://github.com/aarav-sharma-dev",
        linkedin_url="https://linkedin.com/in/aarav-sharma",
        portfolio_url="https://aaravsharma.me",
        resume_file_url="/uploads/resumes/sample_aarav_resume.pdf",
        resume_raw_text="Aarav Sharma | Cloud Software Engineer | Python, FastAPI, Docker, AWS, React, PostgreSQL",
        graduation_year=2026,
        department="Computer Science & Engineering",
        cgpa=8.8,
        placement_readiness_score=88.5
    )
    db.add(student_profile)
    db.flush()

    # Demo Student 2: Priya Patel (AI Specialist)
    student2_user = User(
        email="priya@careerlens.io",
        password_hash=hashed_pwd,
        full_name="Priya Patel",
        role="student",
        college_name="National Institute of Technology (NIT) Trichy"
    )
    db.add(student2_user)
    db.flush()

    student2_profile = StudentProfile(
        user_id=student2_user.id,
        headline="Machine Learning & Deep Learning Researcher",
        bio="Specializing in NLP and PyTorch neural networks. Winner of Smart India Hackathon.",
        github_url="https://github.com/priyapatel-ai",
        linkedin_url="https://linkedin.com/in/priyapatel",
        graduation_year=2026,
        department="Data Science & Artificial Intelligence",
        cgpa=9.2,
        placement_readiness_score=92.0
    )
    db.add(student2_profile)
    db.flush()

    # Demo Student 3: Rohan Verma (Developing Student with unverified skills)
    student3_user = User(
        email="rohan@careerlens.io",
        password_hash=hashed_pwd,
        full_name="Rohan Verma",
        role="student",
        college_name="Delhi Technological University (DTU)"
    )
    db.add(student3_user)
    db.flush()

    student3_profile = StudentProfile(
        user_id=student3_user.id,
        headline="Full Stack Web Enthusiast",
        bio="Frontend developer learning React and Node.js. Building campus projects.",
        graduation_year=2026,
        department="Information Technology",
        cgpa=7.4,
        placement_readiness_score=54.0
    )
    db.add(student3_profile)
    db.flush()

    # Demo Recruiter: Sneha Rao (TechCorp)
    recruiter_user = User(
        email="recruiter@techcorp.com",
        password_hash=hashed_pwd,
        full_name="Sneha Rao",
        role="recruiter",
        company_name="TechCorp Global Labs"
    )
    db.add(recruiter_user)
    db.flush()

    # Demo College TPO: Dr. Rajiv Kapoor
    college_user = User(
        email="college@iiit.ac.in",
        password_hash=hashed_pwd,
        full_name="Dr. Rajiv Kapoor",
        role="college_admin",
        college_name="Indian Institute of Information Technology (IIIT)"
    )
    db.add(college_user)
    db.flush()

    # 3. Seed Verified Certificates for Aarav Sharma
    cert1 = Certificate(
        student_id=student_profile.id,
        title="AWS Certified Developer - Associate",
        issuing_org="Amazon Web Services (AWS)",
        issue_date="January 15, 2026",
        credential_id="AWS-DEV-984210",
        credential_url="https://aws.amazon.com/verification/AWS-DEV-984210",
        file_path="/uploads/certificates/sample_aws_cert.pdf",
        file_hash_sha256="7c5b62e49c71a3648a1a3666d929948d3d92bf22bc6d2994d505bf74f67d3b5c",
        qr_detected=True,
        qr_decoded_url="https://aws.amazon.com/verification/AWS-DEV-984210",
        ocr_extracted_text="This certifies that Aarav Sharma has demonstrated AWS Cloud proficiency. Credential ID: AWS-DEV-984210",
        verification_score=96.0,
        verification_status="VERIFIED",
        badge_tier="GOLD",
        tamper_analysis_details={
            "hash_analysis": {"status": "UNIQUE_INTEGRITY_OK"},
            "qr_analysis": {
                "qr_found": True,
                "is_trusted_issuer": True,
                "recognized_issuer_domain": "aws.amazon.com",
                "validation_status": "VALID_ISSUER_URL"
            },
            "ocr_analysis": {
                "name_found_in_cert": True,
                "name_match_score": 100.0,
                "issuing_org": "Amazon Web Services"
            },
            "forensic_analysis": {
                "is_tampered": False,
                "explanation": "No forensic tampering detected. Image compression levels and PDF metadata are uniform."
            },
            "awarded_skills": ["AWS", "Cloud Computing", "DevOps"]
        }
    )
    db.add(cert1)

    cert2 = Certificate(
        student_id=student_profile.id,
        title="Modern React & Redux Specialization",
        issuing_org="Coursera / DeepLearning.AI",
        issue_date="November 20, 2025",
        credential_id="COURSERA-RCT-5510",
        credential_url="https://coursera.org/verify/COURSERA-RCT-5510",
        file_path="/uploads/certificates/sample_react_cert.pdf",
        file_hash_sha256="4d187291a2745a329ef3e6bbd7c664871e95c1c8a14138e9d3d0c41044453b0e",
        qr_detected=True,
        qr_decoded_url="https://coursera.org/verify/COURSERA-RCT-5510",
        ocr_extracted_text="Aarav Sharma has successfully completed Modern React & Component Architecture",
        verification_score=92.0,
        verification_status="VERIFIED",
        badge_tier="GOLD",
        tamper_analysis_details={
            "hash_analysis": {"status": "UNIQUE_INTEGRITY_OK"},
            "qr_analysis": {"qr_found": True, "is_trusted_issuer": True},
            "ocr_analysis": {"name_found_in_cert": True, "name_match_score": 100.0},
            "forensic_analysis": {"is_tampered": False, "explanation": "Clean institutional document."},
            "awarded_skills": ["React", "JavaScript", "Frontend Development"]
        }
    )
    db.add(cert2)
    db.flush()

    # 4. Attach Student Skills (Aarav)
    student_skills_data = [
        ("Python", "advanced", "resume", True, None),
        ("FastAPI", "advanced", "resume", True, None),
        ("AWS", "advanced", "certificate", True, cert1.id),
        ("Docker", "intermediate", "resume", True, None),
        ("React", "advanced", "certificate", True, cert2.id),
        ("TypeScript", "intermediate", "resume", False, None),
        ("PostgreSQL", "intermediate", "resume", False, None),
        ("Git / GitHub", "advanced", "resume", True, None),
    ]

    for sk_name, prof, src, is_ver, cert_id in student_skills_data:
        if sk_name in skill_objs:
            db.add(StudentSkill(
                student_id=student_profile.id,
                skill_id=skill_objs[sk_name].id,
                proficiency=prof,
                source=src,
                is_verified=is_ver,
                verified_by_certificate_id=cert_id
            ))

    # Priya's skills
    for sk_name in ["Python", "Machine Learning", "Deep Learning", "PyTorch", "PostgreSQL"]:
        if sk_name in skill_objs:
            db.add(StudentSkill(
                student_id=student2_profile.id,
                skill_id=skill_objs[sk_name].id,
                proficiency="advanced",
                source="certificate",
                is_verified=True
            ))

    # Rohan's unverified skills
    for sk_name in ["JavaScript", "React", "Node.js", "HTML5"]:
        if sk_name in skill_objs:
            db.add(StudentSkill(
                student_id=student3_profile.id,
                skill_id=skill_objs[sk_name].id,
                proficiency="beginner",
                source="self_reported",
                is_verified=False
            ))

    # 5. Seed Jobs & Internships
    job1 = Job(
        recruiter_id=recruiter_user.id,
        title="Cloud Software Engineer Intern",
        company_name="TechCorp Global Labs",
        location="Remote (India)",
        job_type="internship",
        stipend_or_salary="₹45,000 / month",
        description="Join our Core Cloud Infrastructure team to build resilient microservices using FastAPI, Docker, and AWS. You will develop high-throughput event processing pipelines and assist in container orchestration.",
        requirements_summary="Solid understanding of Python, REST APIs, Docker, and Cloud fundamentals. Experience with Redis caching is a strong plus."
    )
    db.add(job1)
    db.flush()

    for sk_name, weight, mandatory in [("Python", 1.5, True), ("FastAPI", 1.5, True), ("AWS", 2.0, True), ("Docker", 1.2, True), ("Redis", 1.0, False), ("PostgreSQL", 1.0, False)]:
        if sk_name in skill_objs:
            db.add(JobSkill(job_id=job1.id, skill_id=skill_objs[sk_name].id, weight=weight, is_mandatory=mandatory))

    job2 = Job(
        recruiter_id=recruiter_user.id,
        title="Full Stack Engineer Intern",
        company_name="InnovateX Digital",
        location="Bengaluru, Karnataka (Hybrid)",
        job_type="internship",
        stipend_or_salary="₹35,000 / month",
        description="Looking for energetic full stack interns passionate about Next.js, React, TypeScript, and clean API design. You will work directly with our founding engineering team to launch customer-facing products.",
        requirements_summary="Proficiency with modern React, TypeScript, Node.js or Python backend, and relational databases."
    )
    db.add(job2)
    db.flush()

    for sk_name, weight, mandatory in [("React", 1.5, True), ("TypeScript", 1.2, True), ("Next.js", 1.0, False), ("PostgreSQL", 1.2, True), ("Docker", 0.8, False)]:
        if sk_name in skill_objs:
            db.add(JobSkill(job_id=job2.id, skill_id=skill_objs[sk_name].id, weight=weight, is_mandatory=mandatory))

    job3 = Job(
        recruiter_id=recruiter_user.id,
        title="AI / ML Research Intern",
        company_name="DataNova Intelligence",
        location="Remote",
        job_type="internship",
        stipend_or_salary="₹50,000 / month",
        description="Work on state-of-the-art Natural Language Processing, fine-tuning large language models, and developing automated evaluation benchmarks.",
        requirements_summary="Strong foundation in PyTorch, Machine Learning algorithms, Python, and data processing libraries."
    )
    db.add(job3)
    db.flush()

    for sk_name, weight, mandatory in [("Python", 1.5, True), ("Machine Learning", 2.0, True), ("Deep Learning", 1.5, True), ("PyTorch", 1.8, True), ("Docker", 1.0, False)]:
        if sk_name in skill_objs:
            db.add(JobSkill(job_id=job3.id, skill_id=skill_objs[sk_name].id, weight=weight, is_mandatory=mandatory))

    job4 = Job(
        recruiter_id=recruiter_user.id,
        title="Distributed Systems & DevOps Intern",
        company_name="ScalePeak Technologies",
        location="Hyderabad, Telangana",
        job_type="internship",
        stipend_or_salary="₹40,000 / month",
        description="Help optimize our Kubernetes clusters, setup CI/CD pipelines, and implement Redis caching layers for sub-millisecond latencies.",
        requirements_summary="Docker, Kubernetes, Linux fundamentals, CI/CD pipelines, and Redis."
    )
    db.add(job4)
    db.flush()

    for sk_name, weight, mandatory in [("Docker", 1.5, True), ("Kubernetes", 1.8, True), ("Redis", 1.4, True), ("AWS", 1.2, True), ("CI/CD Pipelines", 1.0, False)]:
        if sk_name in skill_objs:
            db.add(JobSkill(job_id=job4.id, skill_id=skill_objs[sk_name].id, weight=weight, is_mandatory=mandatory))

    db.commit()
    print("[CareerLens Seed] Database successfully seeded with 3 students, 1 recruiter, 1 college TPO, 4 jobs, and verified credentials!")
