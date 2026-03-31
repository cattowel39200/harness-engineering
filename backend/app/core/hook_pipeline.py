"""Pre/Post tool use hook pipeline for guardrails and automation."""
from typing import Any
from app.core.harness_loader import HarnessDefinition, HookDef
from app.core.skill_registry import skill_registry


class HookResult:
    """Result of a hook execution."""
    def __init__(self, allow: bool = True, message: str = "",
                 modified_input: dict | None = None,
                 additional_context: str = ""):
        self.allow = allow
        self.message = message
        self.modified_input = modified_input
        self.additional_context = additional_context


class HookPipeline:
    """Executes pre/post tool use hooks defined in harness."""

    async def run_pre_hooks(
        self,
        harness: HarnessDefinition,
        tool_name: str,
        tool_input: dict,
        session_context: dict,
    ) -> HookResult:
        """Run all pre-tool-use hooks. Returns whether to proceed."""

        # 1. Check blocked tools
        if tool_name in harness.tools.blocked:
            return HookResult(
                allow=False,
                message=f"Tool '{tool_name}' is blocked by harness guardrails."
            )

        # 2. Check confirmation requirement
        if tool_name in harness.guardrails.require_confirmation_for:
            # In a real system, this would pause and ask the user
            # For now, add a note to the context
            pass

        # 3. Run harness-defined pre hooks
        for hook_def in harness.hooks.pre_tool_use:
            if tool_name in hook_def.trigger_on or not hook_def.trigger_on:
                result = await self._execute_pre_hook(
                    hook_def, tool_name, tool_input, session_context, harness
                )
                if not result.allow:
                    return result

        return HookResult(allow=True)

    async def run_post_hooks(
        self,
        harness: HarnessDefinition,
        tool_name: str,
        tool_input: dict,
        tool_output: Any,
        session_context: dict,
    ) -> HookResult:
        """Run all post-tool-use hooks. Can inject additional context."""

        additional = []

        for hook_def in harness.hooks.post_tool_use:
            if tool_name in hook_def.trigger_on or not hook_def.trigger_on:
                result = await self._execute_post_hook(
                    hook_def, tool_name, tool_input, tool_output, session_context, harness
                )
                if result.additional_context:
                    additional.append(result.additional_context)

        return HookResult(
            allow=True,
            additional_context="\n".join(additional) if additional else ""
        )

    async def _execute_pre_hook(
        self,
        hook_def: HookDef,
        tool_name: str,
        tool_input: dict,
        session_context: dict,
        harness: HarnessDefinition,
    ) -> HookResult:
        """Execute a single pre-hook based on its name."""

        if hook_def.name == "validate_block_prerequisites":
            return await self._hook_validate_prerequisites(
                tool_input, session_context, harness
            )

        # Default: allow
        return HookResult(allow=True)

    async def _execute_post_hook(
        self,
        hook_def: HookDef,
        tool_name: str,
        tool_input: dict,
        tool_output: Any,
        session_context: dict,
        harness: HarnessDefinition,
    ) -> HookResult:
        """Execute a single post-hook based on its name."""

        if hook_def.name == "store_block_output":
            return await self._hook_store_output(
                tool_input, tool_output, session_context, harness
            )

        if hook_def.name == "suggest_next_block":
            return await self._hook_suggest_next(
                session_context, harness
            )

        return HookResult(allow=True)

    # --- Built-in hook implementations ---

    async def _hook_validate_prerequisites(
        self, tool_input: dict, session_context: dict, harness: HarnessDefinition
    ) -> HookResult:
        """Check if block prerequisites are met before execution."""
        block_id = tool_input.get("block_id", "")
        domain = harness.harness.domain
        if not domain or not block_id:
            return HookResult(allow=True)

        completed = session_context.get("completed_blocks", [])
        is_ready, missing = skill_registry.check_prerequisites(domain, block_id, completed)

        if not is_ready:
            missing_str = ", ".join(missing)
            return HookResult(
                allow=False,
                message=(
                    f"Cannot execute '{block_id}': missing prerequisites [{missing_str}]. "
                    f"Please complete those blocks first."
                )
            )
        return HookResult(allow=True)

    async def _hook_store_output(
        self, tool_input: dict, tool_output: Any, session_context: dict,
        harness: HarnessDefinition
    ) -> HookResult:
        """Store block output in session context."""
        block_id = tool_input.get("block_id", "")
        if block_id:
            completed = session_context.setdefault("completed_blocks", [])
            if block_id not in completed:
                completed.append(block_id)

            # Store a summary of the output
            outputs = session_context.setdefault("block_outputs", {})
            if isinstance(tool_output, str):
                outputs[block_id] = tool_output[:1000]  # Truncate for context
            else:
                outputs[block_id] = str(tool_output)[:1000]

        return HookResult(allow=True)

    async def _hook_suggest_next(
        self, session_context: dict, harness: HarnessDefinition
    ) -> HookResult:
        """Suggest next executable blocks based on DAG."""
        domain = harness.harness.domain
        if not domain:
            return HookResult(allow=True)

        completed = session_context.get("completed_blocks", [])
        next_blocks = skill_registry.get_next_blocks(domain, completed)

        if next_blocks:
            blocks_str = ", ".join(next_blocks)
            return HookResult(
                allow=True,
                additional_context=(
                    f"\n[System] Next available blocks: {blocks_str}. "
                    f"Suggest these to the user as next steps."
                )
            )
        return HookResult(allow=True)


# Singleton
hook_pipeline = HookPipeline()
