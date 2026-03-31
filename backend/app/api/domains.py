"""Domain plugin endpoints."""
from fastapi import APIRouter, HTTPException
from app.core.skill_registry import skill_registry

router = APIRouter()


@router.get("")
async def list_domains():
    """List all discovered domains."""
    return skill_registry.list_domains()


@router.get("/{slug}")
async def get_domain(slug: str):
    """Get domain overview with skillweb."""
    domains = skill_registry.list_domains()
    domain = next((d for d in domains if d.get("slug") == slug), None)
    if not domain:
        raise HTTPException(404, f"Domain not found: {slug}")

    return {
        **domain,
        "skills": skill_registry.list_skills(slug),
        "templates": skill_registry.list_templates(slug),
    }


@router.get("/{slug}/skills")
async def list_skills(slug: str):
    """List skill block summaries."""
    return skill_registry.list_skills(slug)


@router.get("/{slug}/skills/{block_id}")
async def get_skill(slug: str, block_id: str):
    """Get full skill block content."""
    try:
        block = skill_registry.load_skill(slug, block_id)
        return block.model_dump()
    except FileNotFoundError:
        raise HTTPException(404, f"Skill not found: {block_id}")


@router.get("/{slug}/templates")
async def list_templates(slug: str):
    """List program templates."""
    return skill_registry.list_templates(slug)
