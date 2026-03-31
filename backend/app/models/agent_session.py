"""Agent session and message models."""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON
from app.models.base import Base, TimestampMixin, generate_uuid


class AgentSession(Base, TimestampMixin):
    __tablename__ = "agent_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    harness_slug = Column(String, nullable=False)
    title = Column(String, default="New Session")
    status = Column(String, default="active")  # active, paused, completed, failed
    context = Column(JSON, default=dict)   # accumulated skill outputs
    metadata_ = Column("metadata", JSON, default=dict)  # template selection, etc.


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("agent_sessions.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant, tool_use, tool_result
    content = Column(Text, default="")
    tool_name = Column(String, nullable=True)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    token_count = Column(Integer, default=0)


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("agent_sessions.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, default="md")  # md, docx, pdf
    file_size = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default=dict)
