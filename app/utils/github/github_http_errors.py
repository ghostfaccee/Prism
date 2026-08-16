from httpx import Response
from app.exceptions import github as github_exc

def handle_github_status_code(response: Response) -> None:
    if 200 <= response.status_code < 300:
        return
    
    if response.text:
        detail = response.json().get('message', response.text)
    else:
        detail = response.json().get('message', 'No detail')

    if response.status_code == 304:
        raise github_exc.GitHubNotModified304Error(detail)
    elif response.status_code == 400:
        raise github_exc.GitHubBadRequest400Error(detail)
    elif response.status_code == 401:
        raise github_exc.GitHubNotAuthentificated401Error(detail)
    elif response.status_code == 403:
        raise github_exc.GitHubForbidden403Error(detail)
    elif response.status_code == 404:
        raise github_exc.GitHubResourceNotFound404Error(detail)
    elif response.status_code == 409:
        raise github_exc.GitHubConflict409Error(detail)
    elif response.status_code == 422:
        raise github_exc.GitHubValidation422Error(detail)
    elif response.status_code == 500:
        raise github_exc.GitHubInternal500Error(detail)
    elif response.status_code == 503:
        raise github_exc.GitHubUnavailable503Error(detail)
    else:
        raise github_exc.GitHubUnknownAPIError(response.status_code, detail)