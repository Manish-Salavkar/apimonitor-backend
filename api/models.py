# backend/app/api/models.py

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.auth.models import User
import uuid


# -------------------------
# API (Monitored Service)
# -------------------------
class API(Base):
    __tablename__ = "apis"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), default="GET")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    api_keys = relationship("APIKey", back_populates="api")
    usage_logs = relationship("UsageLog", back_populates="api")


# -------------------------
# API Key
# -------------------------
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_value = Column(String(64), unique=True, index=True, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    api_id = Column(String(36), ForeignKey("apis.id"))
    tier_id = Column(String(36), ForeignKey("tiers.id"))

    user = relationship("User")
    api = relationship("API", back_populates="api_keys")
    tier = relationship("Tier", back_populates="api_keys")

    usage_logs = relationship("UsageLog", back_populates="api_key")


# -------------------------
# Tier
# -------------------------
class Tier(Base):
    __tablename__ = "tiers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    rate_limit_rules = relationship(
        "RateLimitRules",
        uselist=False,
        back_populates="tier",
        cascade="all, delete-orphan"
    )

    api_keys = relationship("APIKey", back_populates="tier")


# -------------------------
# Rate Limit Rules
# -------------------------
class RateLimitRules(Base):
    __tablename__ = "rate_limit_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tier_id = Column(String(36), ForeignKey("tiers.id"), unique=True)

    requests_per_minute = Column(Integer, nullable=False)
    requests_per_hour = Column(Integer, nullable=True)
    requests_per_day = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    tier = relationship("Tier", back_populates="rate_limit_rules")


# -------------------------
# Usage Log
# -------------------------
class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String(36), ForeignKey("api_keys.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    api_id = Column(String(36), ForeignKey("apis.id"))

    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)

    timestamp = Column(DateTime, server_default=func.now())

    api_key = relationship("APIKey", back_populates="usage_logs")
    user = relationship("User")
    api = relationship("API", back_populates="usage_logs")


# -------------------------
# Analytics
# -------------------------
class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    api_id = Column(String(36), ForeignKey("apis.id"), nullable=False)
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=True)

    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)

    request_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    avg_response_time_ms = Column(Integer)
    max_response_time_ms = Column(Integer)

    rate_limit_exceeded_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    api = relationship("API")
    api_key = relationship("APIKey")
