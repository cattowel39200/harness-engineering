"""User model."""
from sqlalchemy import Column, String
from app.models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
