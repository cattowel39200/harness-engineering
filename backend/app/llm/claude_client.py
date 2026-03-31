"""Claude API streaming client with tool use support."""
import json
from typing import AsyncGenerator
from anthropic import AsyncAnthropic

from app.config import settings


class ClaudeClient:
    """Wraps the Anthropic API for streaming chat with tool use."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_model = "claude-sonnet-4-20250514"
        self.max_tokens = 4096

    async def stream_chat(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Stream a chat response from Claude.

        Yields SSE-compatible event dicts:
          {"event": "message_start", "data": {...}}
          {"event": "content_delta", "data": {"text": "..."}}
          {"event": "tool_use", "data": {"id": "...", "name": "...", "input": {...}}}
          {"event": "message_end", "data": {"stop_reason": "...", "usage": {...}}}
          {"event": "error", "data": {"message": "..."}}
        """
        try:
            kwargs = {
                "model": self.default_model,
                "max_tokens": max_tokens or self.max_tokens,
                "system": system_prompt,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools

            async with self.client.messages.stream(**kwargs) as stream:
                yield {
                    "event": "message_start",
                    "data": {"model": self.default_model},
                }

                current_tool_use = None
                full_text = ""

                async for event in stream:
                    if event.type == "content_block_start":
                        block = event.content_block
                        if block.type == "tool_use":
                            current_tool_use = {
                                "id": block.id,
                                "name": block.name,
                                "input_json": "",
                            }

                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            full_text += delta.text
                            yield {
                                "event": "content_delta",
                                "data": {"text": delta.text},
                            }
                        elif delta.type == "input_json_delta":
                            if current_tool_use:
                                current_tool_use["input_json"] += delta.partial_json

                    elif event.type == "content_block_stop":
                        if current_tool_use:
                            try:
                                tool_input = json.loads(current_tool_use["input_json"])
                            except json.JSONDecodeError:
                                tool_input = {}
                            yield {
                                "event": "tool_use",
                                "data": {
                                    "id": current_tool_use["id"],
                                    "name": current_tool_use["name"],
                                    "input": tool_input,
                                },
                            }
                            current_tool_use = None

                    elif event.type == "message_stop":
                        pass

                # Get final message for usage stats
                final_message = await stream.get_final_message()
                yield {
                    "event": "message_end",
                    "data": {
                        "stop_reason": final_message.stop_reason,
                        "usage": {
                            "input_tokens": final_message.usage.input_tokens,
                            "output_tokens": final_message.usage.output_tokens,
                        },
                        "full_text": full_text,
                    },
                }

        except Exception as e:
            yield {
                "event": "error",
                "data": {"message": str(e)},
            }

    async def chat_sync(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict] | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """Non-streaming chat for tool result handling."""
        kwargs = {
            "model": self.default_model,
            "max_tokens": max_tokens or self.max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self.client.messages.create(**kwargs)
        return {
            "content": response.content,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }


# Singleton
claude_client = ClaudeClient()
