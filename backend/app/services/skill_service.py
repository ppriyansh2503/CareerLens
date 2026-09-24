import re
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.skill import Skill

def normalize_skill_name(name: str) -> str:
    """
    Standardize skill name for consistent, case-insensitive comparison.
    Strips all non-alphanumeric characters and converts to lowercase.
    e.g.:
      'Git / GitHub' -> 'gitgithub'
      'git/github'   -> 'gitgithub'
      'Next.js'      -> 'nextjs'
      'CI/CD Pipelines' -> 'cicdpipelines'
      'Go (Golang)'  -> 'gogolang'
      'Python'       -> 'python'
    """
    if not name:
        return ""
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def get_or_create_skill(db: Session, skill_name: str, category: str = "technical") -> Skill:
    """
    Idempotently retrieves an existing skill by normalized_name or name (case-insensitive),
    or creates a new skill if it does not exist.
    Handles uniqueness constraints and database rollbacks gracefully.
    """
    clean_name = skill_name.strip()
    norm_name = normalize_skill_name(clean_name)
    if not norm_name:
        raise ValueError("Skill name cannot be empty")

    # 1. Search for existing skill by normalized_name or case-insensitive name
    existing_skill = db.query(Skill).filter(
        or_(
            Skill.normalized_name == norm_name,
            func.lower(Skill.name) == clean_name.lower()
        )
    ).first()

    if existing_skill:
        return existing_skill

    # 2. Skill doesn't exist, create it idempotently
    try:
        new_skill = Skill(
            name=clean_name,
            normalized_name=norm_name,
            category=category
        )
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
        return new_skill
    except IntegrityError:
        # If another concurrent insert happened or uniqueness collided, rollback and fetch
        db.rollback()
        existing_skill = db.query(Skill).filter(
            or_(
                Skill.normalized_name == norm_name,
                func.lower(Skill.name) == clean_name.lower()
            )
        ).first()
        if existing_skill:
            return existing_skill
        raise
