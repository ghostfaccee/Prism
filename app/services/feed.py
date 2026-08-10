
import asyncio
from app.core import logger
from uuid import UUID
from app.schemas import GitHubFeedResponse
from app.services import GitHubService

class GitHubFeedService:
    def __init__(self, github_service: GitHubService) -> None:
        self.service = github_service

    @staticmethod
    def _handle_exception(data: list, data_type: str) -> None:
        if isinstance(data, Exception):
            logger.warning(f'Failed to fetch {data_type}')
            return []
        return data
    
    async def get_user_feed(self, user_id: UUID) -> GitHubFeedResponse:
        '''Collects a complete user activity feed on GitHub'''
        await self.service._get_ensure_current_github_username(user_id) # update the username in advance if it has been updated
        events_task = self.service.get_user_events(user_id)
        repos_task = self.service.get_user_repositories(user_id)
        events, repos = await asyncio.gather(events_task, repos_task)
        repos = repos[:3]
        async def fetch_repo_data(repo: dict) -> dict:
            repo_name = repo['name']
            commits_task = self.service.get_github_commits(user_id, repo_name)
            pulls_task = self.service.get_repository_pulls(user_id, repo_name)
            issues_task = self.service.get_repository_issues(user_id, repo_name)
            commits, pulls, issues = await asyncio.gather(commits_task, pulls_task, issues_task, return_exceptions = True)
            return {
                'commits': self._handle_exception(commits, 'commits'), 
                'pulls': self._handle_exception(pulls, 'pulls'), 
                'issues': self._handle_exception(issues, 'issues')
            }
        res = await asyncio.gather(*[fetch_repo_data(repo) for repo in repos])
        commits, pulls, issues = [], [], []
        for r in res:
            commits.extend(r['commits'])
            pulls.extend(r['pulls'])
            issues.extend(r['issues'])
        return GitHubFeedResponse(
            events = events,
            commits = commits,
            pull_requests = pulls,
            issues = issues,
            total_count = len(events) + len(commits) + len(pulls) + len(issues)
        )
    