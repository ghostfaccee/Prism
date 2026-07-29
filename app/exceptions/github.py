from fastapi import HTTPException, status

class GitHubIntegrationDoesNotExistsError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'GitHub integration does not exists')

class GitHubIntegrationExistsError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'Github integration already exists')

class GitHubError(HTTPException):
    def __init__(self, data: dict):
        return super().__init__(status.HTTP_400_BAD_REQUEST, f'GitHub error: {data.get('error_description', 'unknown error')}')

class InvalidOrExpiredGitHubTokenError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired GitHub token')
