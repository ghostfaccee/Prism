# User guide

**[!!!] Yes, the product is still under development, and the documentation will change frequently. This section provides the basics, which are only valid for the current version of Prism.**

<a href="#authentication-and-verification">Authentication and verification</a>

## Authentication and verification
Prism uses **JWT** for authentication and **email verification** for confirm user account.
### Registration, login, verification (/v1/register)
1. The user specifies their username and password, and optionally their email address.
2. If an email address is specified, a special token is generated and an email with a link to the token is sent to the user's email address.
3. When an email is sent but the user doesn't click the link, the account is created. The is_active field is set to False by default and will remain so until the user clicks the link provided in the email. Email sending and registration are asynchronous.
4. Next, the user needs to log in to their account (`/v1/login`) to receive a JWT token. This token will be needed to confirm the account by clicking the link in the email.
5. The user then follows the link, indicating their jvt token in the header in the following format: `Authorization: Bearer {token}`
6. After that, you'll receive a verified account if you registered with an email address, and an unverified account if you didn't provide one. This isn't a problem, as you can update your account later and add an email address, after which you'll need to verify it (this is still in development ;/)

**Please note that the steps required to confirm the email specified during registration must be performed in the following order: `Registration -> Login -> Confirmation (in the JWT token header)`.**
