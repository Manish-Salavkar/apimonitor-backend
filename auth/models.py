from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, func, BOOLEAN
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(BOOLEAN, default=True)

    role = relationship("Role", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")
    blacklisted_tokens = relationship("BlacklistedTokens", back_populates="user")



class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="role")


class BlacklistedTokens(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    token = Column(Text, nullable=False)
    blacklisted_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="blacklisted_tokens")