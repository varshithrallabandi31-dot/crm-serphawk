"""
Database Models and Engine Setup for Cold Outreach CRM
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from sqlalchemy import Column, String, Index
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with SSL mode for Neon PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


class Company(SQLModel, table=True):
    """
    Company model - stores prospect information
    """
    __tablename__ = "companies"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    company_name: str = Field(max_length=255)
    website_url: str = Field(
        max_length=500,
        sa_column=Column(String(500), unique=True, index=True, nullable=False)
    )
    primary_email: str = Field(max_length=255)
    email_sender: str = Field(default="padilla@dapros.com", max_length=255)
    email_sent_status: bool = Field(default=False)
    recommended_services: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to EmailLog
    email_logs: List["EmailLog"] = Relationship(back_populates="company")


class EmailLog(SQLModel, table=True):
    """
    EmailLog model - tracks all sent emails for rate limiting
    """
    __tablename__ = "email_logs"
    __table_args__ = (
        Index('ix_email_logs_sender_sent_at', 'sender_email', 'sent_at'),
    )
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    company_id: uuid.UUID = Field(foreign_key="companies.id")
    sender_email: str = Field(max_length=255)
    sent_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Relationship back to Company
    company: Optional[Company] = Relationship(back_populates="email_logs")


def create_db_and_tables():
    """
    Create all database tables (drops existing tables first to ensure schema matches)
    """
    # Create all tables if they don't exist
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency to get database session
    """
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created successfully!")
