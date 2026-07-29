import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4, index = True)
    username = Column(String(20), unique = True, index = True, nullable = False)
    email = Column(String(255), unique = True, nullable = True, index = True)
    hashed_password = Column(String(255), nullable = False)
    is_active = Column(Boolean, default = False) # For email verification. A user is considered active if their email is verified.
    verification_token = Column(String(255), nullable = True, unique = True, index = True) # Token for email confirmation.

    github_oauth_state = Column(String(64), nullable = True) # required to protect against csrf attacks
    github_oauth_state_expires = Column(DateTime, nullable = True) # validity period
    github_integration = relationship('GitHubIntegration', back_populates = 'user', uselist = False, cascade = 'all, delete-orphan') # 1:1 integration connection
    