"""Load and validate harness YAML definition files."""
import yaml
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from app.config import settings


# --- Pydantic models for harness structure ---

class HarnessHeader(BaseModel):
    name: str
    slug: str
    version: str = "1.0"
    description: str = ""
    domain: str = ""


class RoleConfig(BaseModel):
    identity: str
    authority_scope: list[str] = []
    language: str = "ko"


class GuardrailsConfig(BaseModel):
    blocked_actions: list[str] = []
    content_rules: list[str] = []
    max_output_tokens: int = 4096
    require_confirmation_for: list[str] = []


class ToolSchema(BaseModel):
    name: str
    description: str = ""
    input_schema: dict = Field(default_factory=dict)


class ToolsConfig(BaseModel):
    allowed: list[ToolSchema] = []
    blocked: list[str] = []


class ContextConfig(BaseModel):
    max_tokens: int = 180000
    strategy: str = "sliding_window_with_summary"
    preserve_always: list[str] = []
    summarize_after_tokens: int = 120000
    summary_instruction: str = ""


class HookDef(BaseModel):
    name: str
    description: str = ""
    trigger_on: list[str] = []
    action: str = ""


class HooksConfig(BaseModel):
    pre_tool_use: list[HookDef] = []
    post_tool_use: list[HookDef] = []


class SchemasConfig(BaseModel):
    session_input: dict = Field(default_factory=dict)
    session_output: dict = Field(default_factory=dict)


class KnowledgeConfig(BaseModel):
    files: list[str] = []
    load_strategy: str = "on_demand"  # on_demand | preload


class ExamplePair(BaseModel):
    user: str
    assistant: str


class HarnessDefinition(BaseModel):
    """Complete parsed harness definition."""
    harness: HarnessHeader
    role: RoleConfig
    guardrails: GuardrailsConfig = Field(default_factory=GuardrailsConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    schemas: SchemasConfig = Field(default_factory=SchemasConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    examples: list[ExamplePair] = []


class HarnessLoader:
    """Discovers and loads harness YAML files."""

    def __init__(self, harnesses_dir: Path | None = None):
        self.harnesses_dir = harnesses_dir or settings.harnesses_dir
        self._cache: dict[str, HarnessDefinition] = {}

    def list_harnesses(self) -> list[dict[str, str]]:
        """List all available harness files."""
        results = []
        if not self.harnesses_dir.exists():
            return results
        for f in self.harnesses_dir.glob("*.harness.yaml"):
            try:
                raw = yaml.safe_load(f.read_text(encoding="utf-8"))
                header = raw.get("harness", {})
                results.append({
                    "slug": header.get("slug", f.stem.replace(".harness", "")),
                    "name": header.get("name", f.stem),
                    "description": header.get("description", ""),
                    "file_path": str(f),
                })
            except Exception:
                continue
        return results

    def load(self, slug: str) -> HarnessDefinition:
        """Load a harness by slug. Caches the result."""
        if slug in self._cache:
            return self._cache[slug]

        file_path = self.harnesses_dir / f"{slug}.harness.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Harness not found: {slug}")

        raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        definition = HarnessDefinition(**raw)
        self._cache[slug] = definition
        return definition

    def reload(self, slug: str) -> HarnessDefinition:
        """Force reload a harness (cache invalidation)."""
        self._cache.pop(slug, None)
        return self.load(slug)

    def clear_cache(self):
        self._cache.clear()


# Singleton
harness_loader = HarnessLoader()
