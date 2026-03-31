"""Domain skill discovery and block loading."""
import json
import yaml
from pathlib import Path
from typing import Any
from pydantic import BaseModel

from app.config import settings


class SkillBlock(BaseModel):
    """Parsed skill block from markdown."""
    id: str
    name: str
    category: str
    requires: list[str] = []
    provides: list[str] = []
    tags: list[str] = []
    description: str = ""
    content: str = ""  # Full markdown body


class DomainManifest(BaseModel):
    """Domain plugin manifest."""
    slug: str
    name: str
    description: str = ""
    version: str = "1.0"


class SkillRegistry:
    """Discovers domains and loads skill blocks."""

    def __init__(self, domains_dir: Path | None = None):
        self.domains_dir = domains_dir or settings.domains_dir
        self._skillweb_cache: dict[str, dict] = {}

    def list_domains(self) -> list[dict]:
        """List all discovered domains."""
        results = []
        if not self.domains_dir.exists():
            return results
        for d in self.domains_dir.iterdir():
            if d.is_dir():
                manifest_path = d / "domain.yaml"
                if manifest_path.exists():
                    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                    results.append(raw)
                else:
                    results.append({
                        "slug": d.name,
                        "name": d.name,
                        "description": "",
                    })
        return results

    def get_skillweb(self, domain_slug: str) -> dict:
        """Load the skillweb.json for a domain."""
        if domain_slug in self._skillweb_cache:
            return self._skillweb_cache[domain_slug]

        path = self.domains_dir / domain_slug / "skillweb.json"
        if not path.exists():
            return {"blocks": {}, "templates": {}}

        data = json.loads(path.read_text(encoding="utf-8"))
        self._skillweb_cache[domain_slug] = data
        return data

    def list_skills(self, domain_slug: str) -> list[dict]:
        """List skill block summaries from skillweb.json."""
        web = self.get_skillweb(domain_slug)
        results = []
        for block_id, block_info in web.get("blocks", {}).items():
            results.append({
                "id": block_id,
                "description": block_info.get("description", ""),
                "category": block_info.get("category", ""),
                "requires": block_info.get("requires", []),
                "provides": block_info.get("provides", []),
                "tags": block_info.get("tags", []),
            })
        return results

    def load_skill(self, domain_slug: str, block_id: str) -> SkillBlock:
        """Load a full skill block by reading its markdown file."""
        web = self.get_skillweb(domain_slug)
        block_info = web.get("blocks", {}).get(block_id)
        if not block_info:
            raise FileNotFoundError(f"Skill block not found: {block_id}")

        # Resolve file path: blocks/ → skills/ (migration)
        file_rel = block_info.get("file", f"blocks/{block_id}.md")
        file_rel = file_rel.replace("blocks/", "skills/")
        file_path = self.domains_dir / domain_slug / file_rel

        if not file_path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        raw = file_path.read_text(encoding="utf-8")

        # Parse YAML frontmatter
        frontmatter = {}
        content = raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}
                content = parts[2].strip()

        return SkillBlock(
            id=block_id,
            name=frontmatter.get("name", block_id),
            category=frontmatter.get("category", block_info.get("category", "")),
            requires=frontmatter.get("requires", block_info.get("requires", [])),
            provides=frontmatter.get("provides", block_info.get("provides", [])),
            tags=block_info.get("tags", []),
            description=block_info.get("description", ""),
            content=content,
        )

    def list_templates(self, domain_slug: str) -> list[dict]:
        """List program templates from skillweb.json."""
        web = self.get_skillweb(domain_slug)
        results = []
        for tpl_id, tpl_info in web.get("templates", {}).items():
            results.append({
                "id": tpl_id,
                "description": tpl_info.get("description", ""),
                "blocks": tpl_info.get("blocks", []),
                "tags": tpl_info.get("tags", []),
            })
        return results

    def check_prerequisites(self, domain_slug: str, block_id: str,
                            completed_blocks: list[str]) -> tuple[bool, list[str]]:
        """Check if a block's prerequisites are met.

        Returns (is_ready, missing_blocks).
        """
        web = self.get_skillweb(domain_slug)
        block_info = web.get("blocks", {}).get(block_id, {})
        requires = block_info.get("requires", [])
        missing = [r for r in requires if r not in completed_blocks]
        return (len(missing) == 0, missing)

    def get_next_blocks(self, domain_slug: str,
                        completed_blocks: list[str]) -> list[str]:
        """Get blocks whose prerequisites are now fully met."""
        web = self.get_skillweb(domain_slug)
        ready = []
        for block_id, block_info in web.get("blocks", {}).items():
            if block_id in completed_blocks:
                continue
            requires = block_info.get("requires", [])
            if all(r in completed_blocks for r in requires):
                ready.append(block_id)
        return ready


# Singleton
skill_registry = SkillRegistry()
