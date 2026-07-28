from pydantic import BaseModel

class GitHubTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    scope: str

