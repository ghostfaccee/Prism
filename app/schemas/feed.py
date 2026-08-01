from pydantic import BaseModel

class GitHubFeedResponse(BaseModel):
    events: list
    commits: list
    pull_requests: list
    issues: list
    total_count: int
