"""Main agent orchestrator - ties together harness, Claude, hooks, and skills."""
import json
from typing import AsyncGenerator, Any

from app.core.harness_loader import HarnessDefinition, harness_loader
from app.core.hook_pipeline import hook_pipeline
from app.core.skill_registry import skill_registry
from app.llm.claude_client import claude_client
from app.llm.prompt_builder import prompt_builder


class AgentRunner:
    """Orchestrates a single agent turn: prompt → Claude → tool loop → response."""

    async def run(
        self,
        harness_slug: str,
        messages: list[dict],
        session_context: dict,
    ) -> AsyncGenerator[dict, None]:
        """Run agent with harness constraints. Yields SSE events.

        Handles the full tool-use loop:
        1. Build system prompt from harness
        2. Call Claude with tools
        3. If Claude requests a tool:
           a. Run pre-hooks (validate)
           b. Execute tool (load skill block)
           c. Run post-hooks (store output, suggest next)
           d. Send tool result back to Claude
           e. Continue streaming
        4. Return final text response
        """
        # Load harness
        harness = harness_loader.load(harness_slug)

        # Build system prompt
        system_prompt = prompt_builder.build_system_prompt(harness, session_context)
        tools = prompt_builder.build_tool_definitions(harness)

        # Build conversation messages (Claude API format)
        api_messages = self._prepare_messages(messages)

        # Agent loop (max 10 tool calls per turn to prevent infinite loops)
        max_tool_rounds = 10

        for round_num in range(max_tool_rounds):
            tool_calls_in_round = []

            # Stream Claude response
            async for event in claude_client.stream_chat(
                system_prompt=system_prompt,
                messages=api_messages,
                tools=tools,
                max_tokens=harness.guardrails.max_output_tokens,
            ):
                if event["event"] == "tool_use":
                    tool_calls_in_round.append(event["data"])
                    yield event  # Forward to client

                elif event["event"] == "error":
                    yield event
                    return

                elif event["event"] == "message_end":
                    stop_reason = event["data"].get("stop_reason")

                    if stop_reason == "tool_use" and tool_calls_in_round:
                        # Process tool calls
                        pass  # Will handle below
                    else:
                        # Final response
                        yield event
                        return

                else:
                    yield event  # Forward content_delta, message_start

            # If we got tool calls, process them
            if not tool_calls_in_round:
                return

            # Add assistant message with tool_use blocks
            assistant_content = []
            for tc in tool_calls_in_round:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                })
            api_messages.append({"role": "assistant", "content": assistant_content})

            # Execute each tool and collect results
            tool_results = []
            for tc in tool_calls_in_round:
                result = await self._execute_tool(
                    harness, tc["name"], tc["input"], session_context
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": result if isinstance(result, str) else json.dumps(result, ensure_ascii=False),
                })

                # Emit tool_result event to client
                yield {
                    "event": "tool_result",
                    "data": {
                        "tool_use_id": tc["id"],
                        "name": tc["name"],
                        "result_preview": (result[:200] + "...") if isinstance(result, str) and len(result) > 200 else result,
                    },
                }

            # Add tool results to conversation
            api_messages.append({"role": "user", "content": tool_results})

            # Continue loop - Claude will process tool results and respond

        # Max rounds reached
        yield {
            "event": "error",
            "data": {"message": "Maximum tool call rounds reached."},
        }

    async def _execute_tool(
        self,
        harness: HarnessDefinition,
        tool_name: str,
        tool_input: dict,
        session_context: dict,
    ) -> Any:
        """Execute a tool with pre/post hooks."""

        # Pre-hooks
        pre_result = await hook_pipeline.run_pre_hooks(
            harness, tool_name, tool_input, session_context
        )
        if not pre_result.allow:
            return f"[BLOCKED] {pre_result.message}"

        # Execute the tool
        if tool_name == "execute_skill_block":
            output = await self._tool_execute_skill_block(harness, tool_input)
        else:
            output = f"[Unknown tool: {tool_name}]"

        # Post-hooks
        post_result = await hook_pipeline.run_post_hooks(
            harness, tool_name, tool_input, output, session_context
        )

        # Append additional context from post-hooks
        if post_result.additional_context:
            if isinstance(output, str):
                output = output + "\n" + post_result.additional_context
            else:
                output = str(output) + "\n" + post_result.additional_context

        return output

    async def _tool_execute_skill_block(
        self, harness: HarnessDefinition, tool_input: dict
    ) -> str:
        """Load and return a skill block's content."""
        block_id = tool_input.get("block_id", "")
        domain = harness.harness.domain

        if not domain:
            return "[Error] No domain configured in harness."

        try:
            block = skill_registry.load_skill(domain, block_id)
            return (
                f"# Skill Block: {block.name}\n"
                f"Category: {block.category}\n"
                f"Requires: {', '.join(block.requires) if block.requires else 'None'}\n"
                f"Provides: {', '.join(block.provides)}\n\n"
                f"{block.content}"
            )
        except FileNotFoundError as e:
            return f"[Error] {str(e)}"

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """Convert stored messages to Claude API format."""
        api_messages = []
        for msg in messages:
            if msg.get("role") in ("user", "assistant"):
                api_messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", ""),
                })
        return api_messages


# Singleton
agent_runner = AgentRunner()
