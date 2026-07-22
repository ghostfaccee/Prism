# Endpoints

**Prism** is an API that collects data from various services and displays a feed of interesting events to the user. This section contains all the endpoints necessary for comfortable use. You can also view the api documentation at `http://127.0.0.1:8000/docs` if prism is already running. Enjoy your experience :).

## `v1` endpoints
### `/v1/` - Main Page
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
    "username" : "<your username (requiered)>",
    "password" : "<your password (required)>",
    "email" : "<your email (not required, default null)>"
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
