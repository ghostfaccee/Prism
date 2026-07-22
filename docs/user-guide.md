# User guide

**[!!!] Yes, the product is still under development, and the documentation will change frequently. This section provides the basics, which are only valid for the current version of Prism.**

<a href="#authentication-and-verification">Authentication and verification</a>

## Authentication and Verification
Prism uses **JWT** for authentication and **email verification** to confirm the user account.

### Registration, Login, Verification (/v1/register)
1. The user provides their username and password, and, if necessary, their email address.

2. If an email address is provided, a special token is generated (used for the /v1/verification/{token} endpoint), and an email with a link to verify the token is sent to the user's email address.

3. If the email is sent but the user does not click the link, the account is created. The is_active field is set to False by default and will remain so until the user clicks the link provided in the email. Email sending and registration are asynchronous.

4. After registration, the user logs in (/v1/login) and receives a JWT token. When clicking a link in the email, this token is transmitted in the Authorization header so the server can identify the user and activate the account.

5. The user then clicks the link, specifying their JWT token in the header in the following format: `Authorization: Bearer {token}`

6. You will then receive a confirmed account if you registered with an email address, and an unconfirmed account if you did not provide one. This is not a problem, as you can update your account at the /v1/me endpoint (patch request) and specify your new email address there, after which you will receive an email with a confirmation link.

**Please note that the steps required to confirm the email address specified during registration must be completed in the following order: `Registration (/v1/register) -> Login (/v1/login) -> Confirmation (link in email) (in the JWT token header)`.**

