# User Authentication

We explain a simplified version of the **OpenID Connect** (OIDC) protocol following this [tutorial](https://www.oauth.com/oauth2-servers/signing-in-with-google/). OIDC is a protocol for authentication (who are you?) built on top of **OAuth 2.0**, which is a protocol for authorization (what are you allowed to do?).

Suppose we use Google's ODIC implementation (typically, we do not want build our own implementation, because then we have to deal with secure password storage, multi-factor authentication, password reset and [more](https://security.stackexchange.com/questions/272217/best-login-flow-for-username-and-password-authentication)).

First, we have to register our application in the Google API console. During registration, we provide a callback URL, which is where Google will send responses. After registration, we can view our application's client ID and client secret.

When a user clicks the login link on our website, the user's client sends a request to our application server. In handling this request, our application server builds an authorization request to https://accounts.google.com/o/oauth2/v2/auth and sends it back as a redirect response to the user's client. The authorization request includes the application's client ID.

The user now sees Google's login page. Suppose the user logs in. If the login is successful, then Google sends back a redirect response that takes the user to the page specified by our callback URL. The response includes an authorization code.

Our application server extracts this authorization code. It then sends a token request to https://www.googleapis.com/oauth2/v4/token. The request includes the client ID, the client secret and the authorization code.

If successful, Google responds with an access token and an ID token. The application server can now send requests with the access token to Google APIs. The ID token is a **JSON Web Token** (JWT) that contains user information. A JWT is a crytographically signed JSON object. In this case, the JWT has been signed by Google.

Here's the  workflow ([source](
https://web.archive.org/web/20240101013351/https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow)):

![Authorization Code Flow](https://web.archive.org/web/20240101013351im_/https://images.ctfassets.net/cdy7uua7fh8z/2nbNztohyR7uMcZmnUt0VU/2c017d2a2a2cdd80f097554d33ff72dd/auth-sequence-auth-code.png)

"Auth0 Tenant" is the Google Authorization Server. "Your API" is the Google API. "Regular Web App" is the application server. Step 2 shows the application sending a request to the authorization server and the authorization server sending a redirect response back to the client. However, the tutorial describes it as the application server building a request to the authorization server and the application server returning it as a redirect response to the client.

We can now include the ID token in requests that need to be authenticated. However, we need to transmit these tokens over HTTPS (like all the requests and responses in the workflow above). We also need to validate the ID token. Validation includes, for example, checking the digital signature and that the token has not expired.

As an aside, the authorization workflow with OAuth 2.0 looks very similar to the authentication workflow with ODIC described here. However, instead of a login page, the user sees a page where they can click "Authorize" and instead of the response to the token request including an access token and an ID token, it only includes an access token.

We have left out several details. For example, we should also include the following in the initial authorization request:
* Cross-Site Request Forgery (CSRF) token: E.g., a hash of a random number. Google will return the CSRF token in its response and we can check that it matches the token we generated to prevent [CSRF attacks](https://stackoverflow.com/questions/5207160/what-is-a-csrf-token-what-is-its-importance-and-how-does-it-work).
* nonce: a random number used to prevent [replay attacks](https://stackoverflow.com/questions/38257221/exactly-how-does-a-nonce-and-client-nonce-prevent-a-replay). 
* scope: defines what the access token will enable us to do

For more information, see Google's [description](https://web.archive.org/web/20231231013805/https://developers.google.com/identity/openid-connect/openid-connect) of its ODIC implementation.