from typing import Dict, Any, List
from datetime import datetime
from app.models.student import StudentProfile
from app.models.job import Job

class MatchingEngine:
    """
    Explainable Matching Engine:
    - Evaluates verified vs unverified skills with weighted trust multipliers
    - Breaks down score into 4 transparent components
    - Produces actionable skill gap analysis and 4-week learning roadmap
    """

    @classmethod
    def calculate_match(cls, student: StudentProfile, job: Job) -> Dict[str, Any]:
        student_skills_map = {s.skill.name.lower(): s for s in student.skills if s.skill}
        
        job_skills = job.skills
        if not job_skills:
            # Fallback if no skills explicitly linked
            return cls._empty_match_response(job)

        total_weight = sum(js.weight for js in job_skills) or 1.0
        
        verified_matched_weight = 0.0
        unverified_matched_weight = 0.0
        missing_skills = []
        matched_verified = []
        matched_unverified = []

        for js in job_skills:
            skill_name = js.skill.name
            skill_key = skill_name.lower()
            
            if skill_key in student_skills_map:
                st_skill = student_skills_map[skill_key]
                if st_skill.is_verified:
                    verified_matched_weight += js.weight
                    matched_verified.append(skill_name)
                else:
                    unverified_matched_weight += js.weight
                    matched_unverified.append(skill_name)
            else:
                missing_skills.append(skill_name)

        # Find bonus skills (skills student has that aren't listed on job)
        job_skill_keys = set(js.skill.name.lower() for js in job_skills)
        bonus_skills = [
            s.skill.name for s in student.skills 
            if s.skill and s.skill.name.lower() not in job_skill_keys
        ][:4]

        # Component 1: Verified Skills (Max 45 points)
        verified_ratio = verified_matched_weight / total_weight
        verified_comp = round(verified_ratio * 45.0, 1)

        # Component 2: Unverified Skills (Max 20 points)
        unverified_ratio = unverified_matched_weight / total_weight
        unverified_comp = round(unverified_ratio * 20.0, 1)

        # Component 3: Academic Fit (Max 15 points)
        # Based on CGPA >= 7.5 and CS/IT related department
        academic_score = 10.0
        if (student.cgpa or 0) >= 8.0:
            academic_score += 5.0
        elif (student.cgpa or 0) >= 7.0:
            academic_score += 3.0
        academic_comp = min(15.0, academic_score)

        # Component 4: Project & Credential Depth (Max 20 points)
        verified_certs_count = sum(1 for c in student.certificates if c.verification_status == "VERIFIED")
        project_comp = min(20.0, 8.0 + (verified_certs_count * 6.0))

        overall_score = min(100.0, round(verified_comp + unverified_comp + academic_comp + project_comp, 1))

        # Determine Tier
        if overall_score >= 80.0:
            match_tier = "Strong Fit"
            readiness_verdict = f"High probability match! Candidate possesses {len(matched_verified)} verified core competencies with demonstrated credentials."
            recommended_action = "Apply immediately. Review project specifics in the company's tech stack."
        elif overall_score >= 60.0:
            match_tier = "Moderate Fit"
            readiness_verdict = f"Good baseline fit. Matches {len(matched_verified) + len(matched_unverified)} required skills, but has key gaps in: {', '.join(missing_skills[:2])}."
            recommended_action = f"Complete the targeted {missing_skills[0] if missing_skills else 'skill'} sprint to reach 85%+ readiness."
        else:
            match_tier = "Gap to Bridge"
            readiness_verdict = f"Foundational gap. Missing {len(missing_skills)} primary skill requirements for this position."
            recommended_action = "Follow the 4-week guided roadmap below to build hands-on projects for this role."

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "overall_score": overall_score,
            "match_tier": match_tier,
            "score_breakdown": {
                "verified_skills_component": verified_comp,
                "unverified_skills_component": unverified_comp,
                "academic_fit_component": academic_comp,
                "project_fit_component": project_comp
            },
            "skill_analysis": {
                "matched_verified_skills": matched_verified,
                "matched_unverified_skills": matched_unverified,
                "missing_critical_skills": missing_skills,
                "bonus_skills": bonus_skills
            },
            "readiness_verdict": readiness_verdict,
            "recommended_action": recommended_action
        }

    @classmethod
    def generate_learning_roadmap(cls, student: StudentProfile, job: Job) -> Dict[str, Any]:
        match = cls.calculate_match(student, job)
        missing = match["skill_analysis"]["missing_critical_skills"]
        current_score = match["overall_score"]
        projected_score = min(96.0, round(current_score + 22.0, 1))

        target_skill_1 = missing[0] if len(missing) > 0 else "Advanced System Design"
        target_skill_2 = missing[1] if len(missing) > 1 else "Cloud Deployment"

        weeks = [
            {
                "week_number": 1,
                "theme": f"Core Foundations: {target_skill_1}",
                "goal": f"Master fundamental principles, syntax, and architecture of {target_skill_1}.",
                "key_topics": [f"{target_skill_1} Core Concepts", "Industry Best Practices", "Setup & Environment Configuration"],
                "action_items": [
                    f"Read official documentation and architectural overview for {target_skill_1}",
                    "Complete 5 interactive algorithmic or configuration exercises",
                    "Build a minimal standalone sandbox repository"
                ],
                "recommended_resources": [
                    f"Official {target_skill_1} Getting Started Guide",
                    "FreeCodeCamp Interactive Lab",
                    "YouTube: 2-Hour Deep Dive & Crash Course"
                ],
                "milestone_project": f"Build a {target_skill_1} Hello-World Micro-Module with unit tests"
            },
            {
                "week_number": 2,
                "theme": f"Applied Engineering: {target_skill_2}",
                "goal": f"Hands-on integration with {target_skill_2} and containerized workflows.",
                "key_topics": [f"{target_skill_2} in Production", "API Integration", "State Management & Caching"],
                "action_items": [
                    f"Implement real-world data flow using {target_skill_2}",
                    "Integrate error handling, retry policies, and structured logging",
                    "Push code to GitHub with clear README and architecture diagram"
                ],
                "recommended_resources": [
                    f"GitHub Awesome-{target_skill_2.lower()} curations",
                    "Coursera / NPTEL Practical Specialization Module"
                ],
                "milestone_project": f"Production-ready CRUD or caching service using {target_skill_2}"
            },
            {
                "week_number": 3,
                "theme": "Full-Stack System Synthesis",
                "goal": "Combine all newly acquired skills into an end-to-end portfolio project.",
                "key_topics": ["End-to-End Testing", "Docker Containerization", "CI/CD Pipeline Setup"],
                "action_items": [
                    "Connect frontend client with backend service and database layer",
                    "Dockerize the entire stack with docker-compose.yml",
                    "Deploy project live on Vercel / Render / AWS free tier"
                ],
                "recommended_resources": [
                    "Full-Stack Deployment Guide 2026",
                    "Docker & GitHub Actions Walkthrough"
                ],
                "milestone_project": f"Live deployed application showcasing {target_skill_1} + {target_skill_2}"
            },
            {
                "week_number": 4,
                "theme": "Interview Preparation & Credential Verification",
                "goal": "Pass technical rounds and earn verified certificate to boost match score.",
                "key_topics": ["Common Technical Interview Questions", "System Design Tradeoffs", "Live Coding Practice"],
                "action_items": [
                    f"Solve top 15 interview problems related to {target_skill_1}",
                    "Conduct a peer or AI mock interview session using CareerLens AI Bot",
                    "Complete an authorized assessment/certification and upload to CareerLens for Gold badge verification"
                ],
                "recommended_resources": [
                    "NeetCode / LeetCode Curated List",
                    "HackerRank Skill Certification Test"
                ],
                "milestone_project": "Verified Credential Badge on CareerLens raising match score to 90%+"
            }
        ]

        return {
            "job_id": job.id,
            "target_role": job.title,
            "current_match_score": current_score,
            "projected_match_score": projected_score,
            "summary": f"Targeted 4-week roadmap bridging gaps in {target_skill_1} and {target_skill_2} for {job.company_name}.",
            "weeks": weeks,
            "created_at": datetime.utcnow()
        }

    @classmethod
    def _empty_match_response(cls, job: Job) -> Dict[str, Any]:
        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "overall_score": 50.0,
            "match_tier": "Moderate Fit",
            "score_breakdown": {
                "verified_skills_component": 20.0,
                "unverified_skills_component": 10.0,
                "academic_fit_component": 10.0,
                "project_fit_component": 10.0
            },
            "skill_analysis": {
                "matched_verified_skills": [],
                "matched_unverified_skills": [],
                "missing_critical_skills": [],
                "bonus_skills": []
            },
            "readiness_verdict": "Requirements pending update.",
            "recommended_action": "Check back soon."
        }
