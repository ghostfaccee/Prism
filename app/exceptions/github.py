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

class LoginNotInResponseError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'Login not in response')


# == GitHubAPI Errors ===

class GitHubNotModified304Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_304_NOT_MODIFIED, f'GitHub: 304 | Not modified | Detail: {detail}')

class GitHubBadRequest400Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_400_BAD_REQUEST, f'GitHub: 400 | Bad request | Detail: {detail}')

class GitHubNotAuthentificated401Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_401_UNAUTHORIZED, f'GitHub: 401 | Not authentificated | Detail: {detail}')

class GitHubForbidden403Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_403_FORBIDDEN, f'GitHub: 403 | Forbidden | Detail: {detail}')

class GitHubResourceNotFound404Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_404_NOT_FOUND, f'GitHub: 404 | Resource not found | Detail: {detail}')

class GitHubConflict409Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_409_CONFLICT, f'GitHub: 409 | Conflict | Detail: {detail}')

class GitHubValidation422Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_422_UNPROCESSABLE_CONTENT, f'GitHub: 422 | Validation failed, or the endpoint has been spammed | Detail: {detail}')

class GitHubInternal500Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, f'GitHub: 500 | Internal error | Detail: {detail}')

class GitHubUnavailable503Error(HTTPException):
    def __init__(self, detail: str):
        return super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, f'GitHub: 503 | Service unavailable | Detail: {detail}')

class GitHubUnknownAPIError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        return super.__init__(status_code, f'Github: {status_code} | Unknown error | Detail: {detail}')