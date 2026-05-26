from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func

from .database import Base


class Repository(Base):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("external_id", name="uq_repositories_external_id"),)

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    html_url = Column(String(1024), nullable=False)
    stargazers_count = Column(Integer, nullable=False, default=0)
    forks_count = Column(Integer, nullable=False, default=0)
    open_issues_count = Column(Integer, nullable=False, default=0)
    language = Column(String(128), nullable=True)
    raw_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
