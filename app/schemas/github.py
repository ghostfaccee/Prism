from pydantic import BaseModel
from typing import Optional

class GitHubTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    scope: str

class GitHubUserInfo(BaseModel):
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    public_repos: Optional[int] = None
    followers: Optional[int] = None
    following: Optional[int] = None

class GitHubCallbackResponse(BaseModel):
    detail: str = 'GitHub account successfully linked'
    token_type: str = 'bearer'
    scope: str