import uuid
from app.core import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class GitHubIntegration(Base):
    __tablename__ = 'github_integrations'

    integration_id = Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4, index = True)
    user_id = Column(UUID(as_uuid = True), ForeignKey('users.user_id'), nullable = False, unique = True, index = True)
    access_token = Column(String, nullable = False)

    user = relationship('User', back_populates = 'github_integration')
