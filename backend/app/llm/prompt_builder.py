"""Assemble system prompts from harness definitions."""
from app.core.harness_loader import HarnessDefinition


class PromptBuilder:
    """Builds Claude system prompts from harness definitions."""

    def build_system_prompt(self, harness: HarnessDefinition,
                            session_context: dict | None = None) -> str:
        """Assemble the full system prompt from harness sections."""
        parts = []

        # 1. Role identity
        parts.append(f"# Role\n{harness.role.identity.strip()}")

        if harness.role.authority_scope:
            scope = "\n".join(f"- {s}" for s in harness.role.authority_scope)
            parts.append(f"\n## Authority Scope\n{scope}")

        # 2. Guardrails (hard constraints - placed early for stronger influence)
        if harness.guardrails.blocked_actions:
            blocked = "\n".join(f"- {a}" for a in harness.guardrails.blocked_actions)
            parts.append(f"\n# Hard Constraints (NEVER do these)\n{blocked}")

        if harness.guardrails.content_rules:
            rules = "\n".join(f"- {r}" for r in harness.guardrails.content_rules)
            parts.append(f"\n# Content Rules (ALWAYS follow)\n{rules}")

        # 3. Language directive
        if harness.role.language:
            parts.append(f"\n# Language\nAlways respond in: {harness.role.language}")

        # 4. Session context (accumulated outputs from previous blocks)
        if session_context:
            completed = session_context.get("completed_blocks", [])
            if completed:
                blocks_str = ", ".join(completed)
                parts.append(f"\n# Session State\nCompleted blocks: {blocks_str}")

            outputs = session_context.get("block_outputs", {})
            if outputs:
                parts.append("\n# Accumulated Outputs")
                for block_id, output_summary in outputs.items():
                    summary = output_summary if isinstance(output_summary, str) else str(output_summary)[:500]
                    parts.append(f"## {block_id}\n{summary}")

        # 5. Examples (few-shot)
        if harness.examples:
            parts.append("\n# Examples")
            for ex in harness.examples[:3]:  # Limit to 3 examples
                parts.append(f"User: {ex.user}\nAssistant: {ex.assistant}\n")

        return "\n".join(parts)

    def build_tool_definitions(self, harness: HarnessDefinition) -> list[dict]:
        """Convert harness tool definitions to Claude API format."""
        tools = []

        # Add execute_skill_block tool (always available for domain agents)
        tools.append({
            "name": "execute_skill_block",
            "description": (
                "Execute a skill block from the domain's skill web. "
                "Reads the block's rules, frameworks, and templates, then returns "
                "the full content for you to follow and produce the analysis/document. "
                "Always check prerequisites before calling."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "block_id": {
                        "type": "string",
                        "description": "The skill block ID (e.g., 'market-analysis', 'business-model')"
                    },
                    "user_context": {
                        "type": "string",
                        "description": "Additional context from user's request relevant to this block"
                    }
                },
                "required": ["block_id"]
            }
        })

        # Add harness-defined tools
        for tool in harness.tools.allowed:
            if tool.name == "execute_skill_block":
                continue  # Already added
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema or {
                    "type": "object",
                    "properties": {}
                },
            })

        return tools


# Singleton
prompt_builder = PromptBuilder()
