"""Agent session and streaming endpoints."""
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.agent_session import AgentSession, Message
from app.core.agent_runner import agent_runner

router = APIRouter()


class CreateSessionRequest(BaseModel):
    harness_slug: str
    title: str = "New Session"


class SendMessageRequest(BaseModel):
    content: str


@router.post("")
async def create_session(req: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    """Create a new agent session with a harness."""
    session = AgentSession(
        harness_slug=req.harness_slug,
        title=req.title,
        user_id="anonymous",  # TODO: get from JWT
        context={},
        metadata_={},
    )
    db.add(session)
    await db.flush()
    return {
        "id": session.id,
        "harness_slug": session.harness_slug,
        "title": session.title,
        "status": session.status,
    }


@router.get("")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all agent sessions."""
    result = await db.execute(
        select(AgentSession).order_by(AgentSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "harness_slug": s.harness_slug,
            "title": s.title,
            "status": s.status,
            "created_at": str(s.created_at),
        }
        for s in sessions
    ]


@router.get("/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session with message history."""
    session = await db.get(AgentSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": session.id,
        "harness_slug": session.harness_slug,
        "title": session.title,
        "status": session.status,
        "context": session.context,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_name": m.tool_name,
                "created_at": str(m.created_at),
            }
            for m in messages
        ],
    }


@router.post("/{session_id}/messages")
async def send_message(
    session_id: str,
    req: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and stream the agent response via SSE."""
    session = await db.get(AgentSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Save user message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=req.content,
    )
    db.add(user_msg)
    await db.flush()

    # Load message history
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    all_messages = [
        {"role": m.role, "content": m.content}
        for m in result.scalars().all()
        if m.role in ("user", "assistant")
    ]

    # Get session context (mutable - will be updated by hooks)
    session_context = dict(session.context) if session.context else {}

    async def event_generator():
        full_text = ""

        async for event in agent_runner.run(
            harness_slug=session.harness_slug,
            messages=all_messages,
            session_context=session_context,
        ):
            event_type = event["event"]
            data = event["data"]

            if event_type == "content_delta":
                full_text += data.get("text", "")

            elif event_type == "message_end":
                # Save assistant response
                if full_text:
                    async with get_db_for_sse() as sdb:
                        assistant_msg = Message(
                            session_id=session_id,
                            role="assistant",
                            content=full_text,
                            token_count=data.get("usage", {}).get("output_tokens", 0),
                        )
                        sdb.add(assistant_msg)

                        # Update session context
                        s = await sdb.get(AgentSession, session_id)
                        if s:
                            s.context = session_context
                        await sdb.commit()

            yield {
                "event": event_type,
                "data": json.dumps(data, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


# Helper for SSE context (separate DB session)
from app.models.base import async_session as session_factory

class _SSEDBContext:
    async def __aenter__(self):
        self._session = session_factory()
        return self._session
    async def __aexit__(self, *args):
        await self._session.close()

def get_db_for_sse():
    return _SSEDBContext()
