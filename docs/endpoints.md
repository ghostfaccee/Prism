# Endpoints

**Prism** is an API that collects data from various services and displays a feed of interesting events to the user. This section contains all the endpoints necessary for comfortable use. You can also view the api documentation at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc` if prism is already running. Enjoy your experience :).

<details>
  <summary>Menu</summary>
  <ol>
    <li>
      <a href="#v1-endpoints">v1 endpoints</a>
      <ul>
        <li><a href="#v1---main-page--get">Main Page (/v1/) | GET</a></li>
        <li><a href="#v1authregister---register--post">Register (/v1/register) | POST</a></li>
        <li><a href="#v1authlogin---login--post">Login (/v1/login) | POST</a></li>
        <li><a href="#v1verifytoken---verification--get">Verification (/v1/verify/{token} | GET</a></li>
        <li><a href="#v1me---get-current-user--get">Get current user (/v1/me) | GET</a></li>
        <li><a href="#v1me---update-current-user--patch">Update current user (/v1/me) | PATCH</a></li>
        <li><a href="#v1me---deleting-the-current-user--delete">Delete current user (/v1/me) | DELETE</a></li>
        <li><a href="#v1mepassword---change-password--patch">Change password (/v1/me/password) | PATCH</a></li>
        <li><a href="#v1userusernameusername---get-user--get">Get user by username (/v1/user/username/{username}) | GET</a></li>
        <li><a href="#v1useruuiduser_uuid---get-user--get">Get user by uuid (/v1/user/uuid/{uuid}) | GET</a></li>
        <li><a href="#v1githublogin---github-login--get">GitHub Login (/v1/github/login) | GET</a></li>
        <li><a href="#v1githubcallback---github-redirect--get">GitHub callback (/v1/github/callback) | GET</a></li>
        <li><a href="#v1githubme---get-github-user-info--get">Get GitHub linked user (/v1/github/me) | GET</a></li>
        <li><a href="#v1githubevents---get-user-events--get">Get GitHub user events (/v1/github/events) | GET</a></li>
        <li><a href="#v1githubrepositories---get-user-repositories--get">Get GitHub user repositories (/v1/github/repositories) | GET</a></li>
        <li><a href="#v1githubrepocommits---get-commits-from-repository--get">Get GitHub user commits from repository (/v1/github/{repo}/commits) | GET</a></li>
        <li><a href="#v1githubrepopulls---get-pulls-from-repository--get">Get GitHub repository pulls (/v1/github/{repo}/pulls) | GET</a></li>
        <li><a href="#v1githubrepoissues---get-repository-issues--get">Get GitHub repository issues (/v1/github/{repo}/issues) | GET</a></li>
        <li><a href="#v1githubfeed---github-feed--get">Get GitHub feed (/v1/github/feed) | GET</a></li>
      </ul>
    </li>
  </ol>
</details>

## `v1` endpoints
### `/v1/` - Main Page | GET
Just a stub that returns the following json:
```json
{
    "detail" : "Welcome to Prism :)"
}
```
### `/v1/auth/register` - Register | POST
Registers a new user

* Input data format: json (jwt token is not required in the header)
```json
{
    "username" : "<your username (required)>",
    "password" : "<your password (required)>",
    "email" : "<your email (not required, default </null>)>"
}
```

* Output data format: json. 
* Default status: 201 created
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```
The `is_active` field indicates whether your account is verified. The detailed process of account verification and how it works is described in the user_guide.md documentation in the docs directory.

### `/v1/auth/login` - Login | POST

* Input data format: json (jwt token is not required in the header)
```json
{
    "username" : "<your username (required)>",
    "password" : "<your password (required)>"
}
```

* Output data format: json. 
* Default status: 200 ok
```json
{
    "access_token" : "<your jwt token>",
    "token_type" : "<your token type (bearer)>"
}
```

### `/v1/verify/{token}` - Verification | GET
The endpoint that verifies an account. When accessed, the is_active field becomes true, and user options are expanded. You can change the account verification endpoint as follows: in the app/api/v1/endpoints/ directory, edit the verification.py file, and in the .env file, edit the VERIFICATION_LINK variable; the default path is already specified in the .env.example file.

`token` - A token that is associated with the user when they provide their email address. It is required so that when a link in the email is clicked, the service can clearly identify the user and set the is_active field to true. The link in the email already contains a verification token. When clicked, this token is automatically passed to the request. The JWT token in the header is required as an additional security measure.

* Input data format: None (jwt token is required in the headers)

```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "detail": "Email verified successfully"
}
```

### `/v1/me` - Get current user | GET
Returns the current user who presented the jwt token.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```

### `/v1/me` - Update current user | PATCH
Updates the username and email, the password is changed at the endpoint /v1/me/change_password. Requires a jwt token.

* Input data format: json (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```
```json
{
  "username": "your username (optional)",
  "email": "your email (optional)"
}
```
If no data is specified during the update, the user data will not be changed.

* Output data format: json
* Default status: 200 ok
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```

### `/v1/me` - Deleting the current user | DELETE
Deletes a user account. Requires a jwt token.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: None
* Default status: 204 no content

### `/v1/me/password` - Change password | PATCH
Updates the password. Requires a jwt token.

* Input data format: json (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```
```json
{
  "old_pass": "<your old password (required)>",
  "new_pass": "<your new password (required)>"
}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```

### `/v1/user/username/{username}` - Get user | GET
Allows you to globally find a user by their username.

`username` - username : /

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```

### `/v1/user/uuid/{user_uuid}` - Get user | GET
Allows you to globally find a user by their uuid.

`user_uuid` - user uuid : /

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "user_id": "<your uuid>",
  "username": "<your username>",
  "email": "<your email>",
  "is_active": <true/false>
}
```

### `/v1/github/login` - GitHub Login | GET
Redirects the user to the GitHub login page.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: None
* Default status: 307 temporary redirect

### `/v1/github/callback` - GitHub Redirect | GET
Accepts the code from GitHub, exchanges it for a token, and stores it in the database.

**Parameters:**
* `code` - The very code that is exchanged for an access token
* `state` - The parameter required to protect against CSRF attacks.
---
* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "detail": "<message>",
  "token_type": "<token type>",
  "scope": "<scope>"
}
```

### `/v1/github/me` - Get GitHub user info | GET
Gets information about the user's GitHub account, if they have linked it.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json
* Default status: 200 ok
```json
{
  "login": "<login>",
  "name": "<name>",
  "email": "<email>",
  "avatar_url": "<avatar url>",
  "bio": "<bio>",
  "public_repos": <public respositories>,
  "followers": <followers>,
  "following": <following>
}
```

### `/v1/github/events` - Get user events | GET
Returns a list of events on GitHub.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
[
  {
    "id": "<id>",
    "type": "<type>",
    "actor": {
        "id": <id>,
        "login": "<login>",
        "display_login": "<display login>",
        "gravatar_id": "<gravatar id>",
        "url": "<url>",
        "avatar_url": "<avatar url>"
    },
    "repo": {
        "id": <id>,
        "name": "<name>",
        "url": "<url>"
    },
    "payload": {
        "repository_id": <repository id>,
        "push_id": <push id>,
        "ref": "<ref>",
        "head": "<head>",
        "before": "<before>"
    },
    "public": <true/false>,
    "created_at": "<created at>"
  }, // etc...
]
```

### `/v1/github/repositories` - Get user repositories | GET
Returns a list of user repositories on GitHub.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
[
  {
    "id": <id>,
    "node_id": "<node_id>",
    "name": "<name>",
    "full_name": "<full name>",
    "private": <true/false>,
    "owner": {
        "login": "<login>",
        "id": <id>,
        "node_id": "<node id>",
        "avatar_url": "<avatar url>",
        "gravatar_id": "<gravatar id>",
        "url": "<url>",
        "html_url": "<html url>",
        "followers_url": "<followers url>",
        "following_url": "<following url>",
        "gists_url": "<gists url>",
        "starred_url": "<starred url>",
        "subscriptions_url": "<subscriptions url>",
        "organizations_url": "<organizations url>",
        "repos_url": "<repos url>",
        "events_url": "<events url>",
        "received_events_url": "<receives events url>",
        "type": "<type>",
        "user_view_type": "<user view type>",
        "site_admin": <true/false>
    },
    "html_url": "<html url>",
    "description": <description/</null>>,
    "fork": <true/false>,
    "url": "<url>",
    "forks_url": "<forks url>",
    "keys_url": "<keys url>",
    "collaborators_url": "<collaborations url>",
    "teams_url": "<teams url>",
    "hooks_url": "<hooks url>",
    "issue_events_url": "<issues url>",
    "events_url": "<events url>",
    "assignees_url": "<assignees url>",
    "branches_url": "<branches url>",
    "tags_url": "<tags url>",
    "blobs_url": "<blobs url>",
    "git_tags_url": "<git tags url>",
    "git_refs_url": "<git refs url>",
    "trees_url": "<trees url>",
    "statuses_url": "<statuses url>",
    "languages_url": "<languages url>",
    "stargazers_url": "<stargazers url>",
    "contributors_url": "<contibutors url>",
    "subscribers_url": "<subscribers url>",
    "subscription_url": "<subscription url>",
    "commits_url": "<commits url>",
    "git_commits_url": "<git commits url>",
    "comments_url": "<comments url>",
    "issue_comment_url": "<issue comment url>",
    "contents_url": "<contents url>",
    "compare_url": "<compare url>",
    "merges_url": "<merges url>",
    "archive_url": "<archive url>",
    "downloads_url": "<downloads url>",
    "issues_url": "<issues url>",
    "pulls_url": "<pulls url>",
    "milestones_url": "<milestones url>",
    "notifications_url": "<notifications url>",
    "labels_url": "<labels url>",
    "releases_url": "<releases url>",
    "deployments_url": "<deployments url>",
    "created_at": "<created at>",
    "updated_at": "<updated at>",
    "pushed_at": "<pushed at>",
    "git_url": "<git url>",
    "ssh_url": "<ssh url>",
    "clone_url": "<clone url>",
    "svn_url": "<svn url>",
    "homepage": <homepage/</null>>,
    "size": <size>,
    "stargazers_count": <stargazers count>,
    "watchers_count": <watchers count>,
    "language": "<language>",
    "has_issues": <true/false>,
    "has_projects": <true/false>,
    "has_downloads": <true/false>,
    "has_wiki": <true/false>,
    "has_pages": <true/false>,
    "has_discussions": <true/false>,
    "forks_count": <forks count>,
    "mirror_url": <mirror url/</null>>,
    "archived": <true/false>,
    "disabled": <true/false>,
    "open_issues_count": <open issues count>,
    "license": <license/</null>>,
    "allow_forking": <true/false>,
    "is_template": <true/false>,
    "web_commit_signoff_required": <true/false>,
    "has_pull_requests": <true/false>,
    "pull_request_creation_policy": "<pull request creation policy>",
    "topics": <topics>,
    "visibility": "<visibility>",
    "forks": <forks>,
    "open_issues": <open issues>,
    "watchers": <watchers>,
    "default_branch": "<default branch>",
    "permissions": {
        "admin": <true/false>,
        "maintain": <true/false>,
        "push": <true/false>,
        "triage": <true/false>,
        "pull": <true/false>
    }
  }, // etc...
]
```

### `/v1/github/{repo}/commits` - Get commits from repository | GET
Returns a list of commits.

* `repo` - repository name (example: prism)

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
[
  {
    "sha": "<sha>",
    "node_id": "<node id>",
    "commit": {
        "author": {
            "name": "<name>",
            "email": "<email>",
            "date": "<date."
        },
        "committer": {
            "name": "<name>",
            "email": "<email>",
            "date": "<date>"
        },
        "message": "<message>",
        "tree": {
            "sha": "<sha>",
            "url": "<url>"
        },
        "url": "<url>",
        "comment_count": <comment count>,
        "verification": {
            "verified": <true/false>,
            "reason": "<reason>",
            "signature": <signature>,
            "payload": <payload>,
            "verified_at": <verified at>
        }
    },
    "url": "<url>",
    "html_url": "<html url>",
    "comments_url": "<comment url>",
    "author": {
        "login": "<login>",
        "id": <id>,
        "node_id": "<node id>",
        "avatar_url": "<avatar url>",
        "gravatar_id": "<gravatar url>",
        "url": "<url>",
        "html_url": "<html url>",
        "followers_url": "<followers url>",
        "following_url": "<following url>",
        "gists_url": "<gists url>",
        "starred_url": "<starred url>",
        "subscriptions_url": "<subscriptions url>",
        "organizations_url": "<organizations url>",
        "repos_url": "<repos url>",
        "events_url": "<events url>",
        "received_events_url": "<received events url>",
        "type": "<type>",
        "user_view_type": "<user view type>",
        "site_admin": <true/false>
    },
    "committer": {
        "login": "<login>",
        "id": <id>,
        "node_id": "<node id>",
        "avatar_url": "<avatar url>",
        "gravatar_id": "<gravatar id>",
        "url": "<url>",
        "html_url": "<html url>",
        "followers_url": "<followers url>",
        "following_url": "<following url>",
        "gists_url": "<gists url>",
        "starred_url": "<starred url>",
        "subscriptions_url": "<subscriptions url>",
        "organizations_url": "<organizations url>",
        "repos_url": "<repositories url>",
        "events_url": "<events url>",
        "received_events_url": "<received events url>",
        "type": "<type>",
        "user_view_type": "<user view type>",
        "site_admin": <true/false>
    },
    "parents": [
        {
            "sha": "<sha>",
            "url": "<url>",
            "html_url": "<html url>"
        }
    ]
  }, // etc...
]    
```


### `/v1/github/{repo}/pulls - Get pulls from repository | GET
Returns a list of pulls.

* `repo` - repository name (example: prism)

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
[
    {
        "url": "<url>",
        "id": <id>,
        "node_id": "<node id>",
        "html_url": "<html url>",
        "diff_url": "<diff url>",
        "patch_url": "<patch url>",
        "issue_url": "<issue url>",
        "number": <number>,
        "state": "<state>",
        "locked": <true/false>,
        "title": "<title>",
        "user": {
            "login": "<user>",
            "id": <id>,
            "node_id": "<node id>",
            "avatar_url": "<avatar url>",
            "gravatar_id": "<gravatar url>",
            "url": "<url>",
            "html_url": "<html url>",
            "followers_url": "<followers url>",
            "following_url": "<following url>",
            "gists_url": "<gists url>",
            "starred_url": "<starred url>",
            "subscriptions_url": "<subscriptions url>",
            "organizations_url": "<organizations url>",
            "repos_url": "<repos url>",
            "events_url": "<events url>",
            "received_events_url": "<reveived events url>",
            "type": "<type>",
            "user_view_type": "<user view type>",
            "site_admin": <true/false>
        },
        "body": <body>,
        "created_at": "<created at>",
        "updated_at": "<updated at>",
        "closed_at": "<closed at>",
        "merged_at": <merged at>,
        "merge_commit_sha": <merge commit sha>,
        "assignees": <assignees>,
        "requested_reviewers": <requested reviewers>,
        "requested_teams": <requested teams>,
        "labels": <labels>,
        "milestone": <milestone>,
        "draft": <true/false>,
        "commits_url": "<commits url>",
        "review_comments_url": "<review comments url>",
        "review_comment_url": "<review comment url>",
        "comments_url": "<comments url>",
        "statuses_url": "<statuses url>",
        "head": {
            "label": "<label>",
            "ref": "<ref>",
            "sha": "<sha>",
            "user": {
                "login": "<login>",
                "id": <id>,
                "node_id": "<node id>",
                "avatar_url": "<avatar url>",
                "gravatar_id": "<gravatar id>",
                "url": "<url>",
                "html_url": "<html url>",
                "followers_url": "<followers url>",
                "following_url": "<following url>",
                "gists_url": "<gists url>",
                "starred_url": "<starred url>",
                "subscriptions_url": "<subscriptions url>",
                "organizations_url": "<organizations url>",
                "repos_url": "<repositories url>",
                "events_url": "<events url>",
                "received_events_url": "<received events url>",
                "type": "<type>",
                "user_view_type": "<user view type>",
                "site_admin": <true/false>
            },
            "repo": {
                "id": <id>,
                "node_id": "<node id>",
                "name": "<name>",
                "full_name": "<full name>",
                "private": <true/false>,
                "owner": {
                    "login": "<login>",
                    "id": <id>,
                    "node_id": "<node id>",
                    "avatar_url": "<avatar url>",
                    "gravatar_id": "<gravatar id>",
                    "url": "<url>",
                    "html_url": "<html url>",
                    "followers_url": "<followers url>",
                    "following_url": "<following url>",
                    "gists_url": "<gists url>",
                    "starred_url": "<starred url>",
                    "subscriptions_url": "<subscriptions url>",
                    "organizations_url": "<organizations url>",
                    "repos_url": "<repos url>",
                    "events_url": "<events url>",
                    "received_events_url": "<received events url>",
                    "type": "<type>",
                    "user_view_type": "<user view type>",
                    "site_admin": <true/false>
                },
                "html_url": "<html url>",
                "description": <description/</null>>,
                "fork": <true/false>,
                "url": "<url>",
                "forks_url": "<forks url>",
                "keys_url": "<keys url>",
                "collaborators_url": "<collaborators url>",
                "teams_url": "<teams url>",
                "hooks_url": "<hooks url>",
                "issue_events_url": "<issue events url>",
                "events_url": "<events url>",
                "assignees_url": "<assignees url>",
                "branches_url": "<branches url>",
                "tags_url": "<tags url>",
                "blobs_url": "<blobs url>",
                "git_tags_url": "<git tags url>",
                "git_refs_url": "<git refs url>",
                "trees_url": "<trees url>",
                "statuses_url": "<statuses url>",
                "languages_url": "<languages url>",
                "stargazers_url": "<stagazers url>",
                "contributors_url": "<contributors url>",
                "subscribers_url": "<subscribers url>",
                "subscription_url": "<subscription url>",
                "commits_url": "<commits url>",
                "git_commits_url": "<git commits url>",
                "comments_url": "<comments url>",
                "issue_comment_url": "<issue comment url>",
                "contents_url": "<contents url>",
                "compare_url": "<compare url>",
                "merges_url": "<merges url>",
                "archive_url": "<archive url>",
                "downloads_url": "<downloads url>",
                "issues_url": "<issues url>",
                "pulls_url": "<pulls url>",
                "milestones_url": "<milestones url>",
                "notifications_url": "<notifications url>",
                "labels_url": "<labels url>",
                "releases_url": "<releases url>",
                "deployments_url": "<deployments url>",
                "created_at": "<created at>",
                "updated_at": "<updated at>",
                "pushed_at": "<pushed at>",
                "git_url": "<git url>",
                "ssh_url": "<ssh url>",
                "clone_url": "<clone url>",
                "size": <size>,
                "stargazers_count": <stargazers count>,
                "watchers_count": <watchers count>,
                "language": <language/</null>>,
                "has_issues": <true/false>,
                "has_projects": <true/false>,
                "has_downloads": <true/false>,
                "has_wiki": <true/false>,
                "has_pages": <true/false>,
                "has_discussions": <true/false>,
                "forks_count": <forks count>,
                "mirror_url": <mirror url>,
                "archived": <true/false>,
                "disabled": <true/false>,
                "open_issues_count": <open issues count>,
                "license": <license/</null>>,
                "allow_forking": <true/false>,
                "is_template": <true/false>,
                "web_commit_signoff_required": <true/false>,
                "has_pull_requests": <true/false>,
                "pull_request_creation_policy": "<pull request creation policy>",
                "topics": <topics>,
                "visibility": "<visibility>",
                "forks": <forks>,
                "open_issues": <open issues>,
                "watchers": <watchers>,
                "default_branch": "<default branch>"
            }
        },
        "base": {
            "label": "<label>",
            "ref": "<ref>",
            "sha": "<sha>",
            "user": {
                "login": "<login>",
                "id": <id>,
                "node_id": "<node id>",
                "avatar_url": "<avatar url>",
                "gravatar_id": "<gravatar id",
                "url": "<url>",
                "following_url": "<following url>",
                "gists_url": "<gists url>",
                "starred_url": "<starred url>",
                "subscriptions_url": "<subscriptions url>",
                "organizations_url": "<organizations url>",
                "repos_url": "<repositories url>",
                "events_url": "<events url>",
                "received_events_url": "<received events url>",
                "type": "<type>",
                "user_view_type": "<user view type>",
                "site_admin": <true/false>
            },
            "repo": {
                "id": <id>,
                "node_id": "<node id>",
                "name": "<name>",
                "full_name": "<full name>",
                "private": <true/false>,
                "owner": {
                    "login": "<login>",
                    "id": <id>,
                    "node_id": "<node id>",
                    "avatar_url": "<avatar url>",
                    "gravatar_id": "<gravatar id>",
                    "url": "<url>", 
                    "following_url": "<following url>",
                    "gists_url": "<gists url>",
                    "starred_url": "<starred url>",
                    "subscriptions_url": "<subscriptions url>",
                    "organizations_url": "<organizations url>",
                    "repos_url": "<repositories url>",
                    "events_url": "<events url>",
                    "received_events_url": "<received events url>",
                    "type": "<type>",
                    "user_view_type": "<user view type>",
                    "site_admin": <true/false>
                },
                "html_url": "<html url>",
                "fork": <true/false>,
                "url": "<url>",
                "forks_url": "<forks url>",
                "keys_url": "<keys url>",
                "collaborators_url": "<collaborators url>",
                "teams_url": "<teams url>",
                "hooks_url": "<hooks url>",
                "issue_events_url": "<issue events url>",
                "events_url": "<events url>",
                "assignees_url": "<assignees url>",
                "branches_url": "<branches url>",
                "tags_url": "<tags url>",
                "blobs_url": "<blobs url>",
                "git_tags_url": "<git tags url>",
                "git_refs_url": "<git refs url>",
                "trees_url": "<trees url>",
                "statuses_url": "<statuses url>",
                "languages_url": "<languages url>",
                "stargazers_url": "<stargazers url>",
                "contributors_url": "<contributors url>",
                "subscribers_url": "<subscribers url>",
                "subscription_url": "<subsription url>",
                "commits_url": "<commits url>",
                "git_commits_url": "<git commits url>",
                "comments_url": "<comments url>",
                "issue_comment_url": "<issue comment url>",
                "contents_url": "<contents url>",
                "compare_url": "<compare url>",
                "merges_url": "<merges url>",
                "archive_url": "<archive url>",
                "downloads_url": "<downloads url>",
                "issues_url": "<issues url>",
                "pulls_url": "<pulls url>",
                "milestones_url": "<milestones url>",
                "notifications_url": "<notifications url>",
                "labels_url": "<labels url>",
                "releases_url": "<releases url>",
                "deployments_url": "<deployments url>",
                "created_at": "<created at>",
                "updated_at": "<updated at>",
                "pushed_at": "<pushed at>",
                "git_url": "<git url>",
                "ssh_url": "<ssh url>",
                "clone_url": "<clone url>",
                "size": <size>,
                "stargazers_count": <stargazers count>,
                "watchers_count": <watchers count>,
                "language": <language/</null>>,
                "has_issues": <true/false>,
                "has_projects": <true/false>,
                "has_downloads": <true/false>,
                "has_wiki": <true/false>,
                "has_pages": <true/false>,
                "has_discussions": <true/false>,
                "forks_count": <forks count>,
                "mirror_url": <mirror url/</null>>,
                "archived": <true/false>,
                "disabled": <true/false>,
                "open_issues_count": <open issues count>,
                "license": <license/</null>>,
                "allow_forking": <true/false>,
                "is_template": <true/false>,
                "web_commit_signoff_required": <true/false>,
                "has_pull_requests": <true/false>,
                "pull_request_creation_policy": "<pull request creation policy>",
                "topics": <topics>,
                "visibility": "<visibility>",
                "forks": <forks>,
                "open_issues": <open issues>,
                "watchers": <watchers>,
                "default_branch": "<default branch>"
            }
        },
        "_links": {
            "self": {
                "href": "<href>"
            },
            "html": {
                "href": "<href>"
            },
            "issue": {
                "href": "<href>"
            },
            "comments": {
                "href": "<href>"
            },
            "review_comments": {
                "href": "<href>"
            },
            "review_comment": {
                "href": "<href>"
            },
            "commits": {
                "href": "<href>"
            },
            "statuses": {
                "href": "<href>"
            }
        },
        "author_association": "<author association>",
        "auto_merge": <auto merge/</null>>,
        "assignee": <assignee/</null>>,
        "active_lock_reason": <active lock reason/</null>>
    }
]
```

### `/v1/github/{repo}/issues - Get repository issues | GET
Return a list of issues.

* `repo` - repository name (example: prism)

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
[
    {
        "url": "<url>",
        "repository_url": "<repository url>",
        "labels_url": "<labels url>",
        "comments_url": "<comments url>",
        "events_url": "<events url>",
        "html_url": "<html url>",
        "id": <id>,
        "node_id": "<node id>",
        "number": <number>,
        "title": "<title>",
        "user": {
            "login": "<login>",
            "id": <id>,
            "node_id": "<node id>",
            "avatar_url": "<avatar url>",
            "gravatar_id": "<gravatar id>",
            "url": "<url>",
            "html_url": "<html url>",
            "followers_url": "<followers url>",
            "following_url": "<following url>",
            "gists_url": "<gists url>",
            "starred_url": "<starred url>",
            "subscriptions_url": "<subscriptions url>",
            "organizations_url": "<organizations url>",
            "repos_url": "<repos url>",
            "events_url": "<events url>",
            "received_events_url": "<received events url>",
            "type": "<type>",
            "user_view_type": "<user view type>",
            "site_admin": <true/false>
        },
        "labels": <labels>,
        "state": "<state>",
        "locked": <true/false>,
        "assignees": <assignees>,
        "milestone": <milestone/</null>>,
        "comments": <comments>,
        "created_at": "created at",
        "updated_at": "updated at",
        "closed_at": "closed at",
        "assignee": <assignee/</null>>,
        "author_association": "<author association>",
        "active_lock_reason": <active lock reason/</null>>,
        "draft": <true/false>,
        "pull_request": {
            "url": "<url>",
            "html_url": "<html url>",
            "diff_url": "<diff url>",
            "patch_url": "<patch url>",
            "merged_at": <merged at/</null>>
        },
        "body": <body/</null>>,
        "closed_by": {
            "login": "<login>",
            "id": <id>,
            "node_id": "<node id>",
            "avatar_url": "<avatar url>",
            "gravatar_id": "<gravatar id>",
            "url": "<url>",
            "html_url": "<html url>",
            "followers_url": "<followers url>",
            "following_url": "<following url>",
            "gists_url": "<gists url>",
            "starred_url": "<starred url>",
            "subscriptions_url": "<subscriptions url>",
            "organizations_url": "<organizations url>",
            "repos_url": "<repos url>",
            "events_url": "<events url>",
            "received_events_url": "<received events url>",
            "type": "<type>",
            "user_view_type": "<user view type>",
            "site_admin": <true/false>
        },
        "reactions": {
            "url": "<url>",
            "total_count": <total count>,
            "+1": <+1>,
            "-1": <-1>,
            "laugh": <laugh>,
            "hooray": <hooray>,
            "confused": <confused>,
            "heart": <heart>,
            "rocket": <rocket>,
            "eyes": <eyes>
        },
        "timeline_url": "<timeline url>",
        "performed_via_github_app": <performed via github app/null>,
        "state_reason": <state reason/null>
    }
]
```

### `/v1/github/feed` - GitHub feed | GET
Returns the GitHub feed.

* Input data format: None (jwt token is required in headers)
```headers
Authorization: Bearer {your jwt token}
```

* Output data format: json **(!!! Please note that this response is valid only as of August 5, 2026. Check the GitHub API if you want to know the current response exactly.)**
* Default status: 200 ok
```json
{
  "events": [
    "<events (the structure is already indicated above)>"
  ],
  "commits": [
    "<commits (the structure is already indicated above)>"
  ],
  "pull_requests": [
    "<pulls (the structure is already indicated above)>"
  ],
  "issues": [
    "<issues (the structure is already indicated above)>"
  ],
  "total_count": <total count>
}
```
