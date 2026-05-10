OAuth Login System
==================

This project is a Google OAuth2 login system using FastAPI, PostgreSQL, and JWT access tokens.

The backend can run by itself as an API. The frontend is optional and lives in the frontend/ folder.


What Problem This Solves
========================

Normally, if you build login yourself, you must store user passwords safely, reset forgotten passwords, protect against leaked passwords, and handle many security details.

With Google OAuth login, your app does not ask for the user's password.

Instead:

1. The user signs in on Google's website.
2. Google confirms the user's identity.
3. Google sends your backend basic user information.
4. Your backend creates or finds the local user.
5. Your backend gives the frontend a JWT token for your own app.

So Google handles the Google account login, and your app handles its own app session after that.


OAuth2 In Easy Language
=======================

OAuth2 is a permission system.

Imagine a user wants to use your app, and your app needs to know who they are. Instead of asking for the user's Google password, your app asks Google:

"Can this user allow my app to know their email and profile?"

Google then asks the user. If the user agrees, Google gives your app a temporary code. Your backend exchanges that code with Google and receives trusted user information.

Important words:

- User:
  The person trying to log in.

- Client:
  Your application. In this project, the FastAPI backend is the OAuth client.

- Authorization Server:
  Google. It shows the login/consent screen and decides whether the login is valid.

- Redirect URI:
  The backend URL where Google sends the user after login.
  In this project:
  http://localhost:8000/auth/callback/google

- Authorization Code:
  A short-lived code Google sends to your backend after login.

- Access Token:
  A token used to access protected resources.

- ID Token / User Info:
  Google-verified information about the user, such as email, name, and Google user ID.

- JWT:
  A signed token created by your backend. The frontend sends it back to your backend when calling protected routes.


OAuth2 vs Login
===============

OAuth2 is mainly about authorization, which means permission.

Login is authentication, which means proving who the user is.

This project uses Google OAuth2 with the openid scope. That means it is also using OpenID Connect behavior, which lets your app safely use Google login for authentication.

The scopes used here are:

openid email profile

That means the app asks Google only for basic identity data:

- Google user ID
- email
- email verified status
- profile/name

It does not ask for Gmail messages, Drive files, Calendar data, or anything sensitive like that.


How This Project Works
======================

Main backend files:

- src/main.py
  Creates the FastAPI app, adds session middleware, adds optional CORS, includes the auth routes, and creates/verifies the users table on startup.

- src/config.py
  Loads settings from .env and checks that required values exist.

- src/auth/oauth_routes.py
  Contains Google login routes, callback route, JWT validation, /auth/me, and logout.

- src/auth/jwt_handler.py
  Creates and decodes JWT access tokens.

- src/db/connection.py
  Opens a PostgreSQL connection.

- src/db/users.py
  Creates the users table and finds or creates users after Google login.

- frontend/
  Optional browser UI. The backend does not depend on this folder.


Login Flow In This App
======================

1. User opens the frontend or goes directly to:

   http://localhost:8000/auth/login/google

2. Backend redirects the user to Google.

3. Google shows the user a login/consent screen.

4. User signs in with Google.

5. Google redirects back to:

   http://localhost:8000/auth/callback/google

6. Backend exchanges Google's authorization response for user information.

7. Backend checks that Google returned:

   - email
   - verified email status
   - Google user ID

8. Backend finds or creates a row in the users table.

9. Backend creates a JWT token for this app.

10. Backend returns the token as JSON, or redirects to the frontend if FRONTEND_SUCCESS_URL is set.

11. Frontend stores the token and sends it when calling protected backend routes.

12. Backend validates the token before returning protected data.


Simple Flow Diagram
===================

Browser/frontend
    |
    | 1. Open /auth/login/google
    v
FastAPI backend
    |
    | 2. Redirect to Google
    v
Google login page
    |
    | 3. User signs in
    v
Google redirects to /auth/callback/google
    |
    | 4. Backend verifies Google response
    v
PostgreSQL users table
    |
    | 5. Backend creates JWT
    v
Frontend receives token
    |
    | 6. Frontend calls /auth/me with Authorization header
    v
Protected backend data


Authorization Header
====================

After login, the frontend receives an access token.

For protected API calls, the frontend sends:

Authorization: Bearer <access_token>

The backend reads that token, verifies the signature, checks expiry, gets the user ID, and loads the user from the database.

If the token is invalid or expired, the backend returns 401 Unauthorized.


Database
========

The users table stores local app users:

- id
- email
- username
- google_id
- created_at

The important value is google_id. It comes from Google's sub field and is stable for that Google account.

The app uses google_id first because it is safer than trusting email alone.


Environment Variables
=====================

Copy .env.example to .env and fill the values:

GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

SECRET_KEY=replace-with-at-least-32-random-characters
SESSION_SECRET_KEY=replace-with-at-least-32-random-characters

DB_NAME=oauth_login
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

CORS_ORIGINS=http://localhost:3000
FRONTEND_SUCCESS_URL=http://localhost:3000/
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=lax

DB_PASSWORD can stay empty if your local PostgreSQL user does not require a password.


Google OAuth Setup
==================

In Google Cloud Console, create an OAuth client.

Use application type:

Web application

Add this authorized redirect URI:

http://localhost:8000/auth/callback/google

Then copy the generated client ID and client secret into your .env file.

Do not commit your real .env file to GitHub.


Run Backend Only
================

Install dependencies:

pip install -r requirements.txt

Run the API:

uvicorn src.main:app --reload

Backend URL:

http://localhost:8000

Health check:

http://localhost:8000/health


Run Optional Frontend
=====================

The frontend is separate. You can ignore it if you only want the backend API.

To use it, set these values in .env:

CORS_ORIGINS=http://localhost:3000
FRONTEND_SUCCESS_URL=http://localhost:3000/

Then run:

cd frontend
python3 -m http.server 3000

Open:

http://localhost:3000


Main API Routes
===============

GET /auth/login/google

Starts Google login.


GET /auth/callback/google

Google redirects here after login. The backend validates the Google response, creates or finds the user, and returns or redirects with a JWT token.


GET /auth/me

Protected route. Requires:

Authorization: Bearer <access_token>

Returns the logged-in user's username and email.


POST /auth/logout

Simple logout helper. The frontend should delete the token.

Right now, logout does not invalidate old JWTs on the server. For production, use refresh tokens, server-side sessions, or a token denylist if you need immediate logout.


Security Notes
==============

- Never store or push real secrets to GitHub.
- SECRET_KEY and SESSION_SECRET_KEY must be long random strings.
- Google client secret must stay on the backend only.
- The frontend should never contain GOOGLE_CLIENT_SECRET.
- For production, use HTTPS.
- For production browser apps, HttpOnly secure cookies are safer than localStorage.
- Keep requested Google scopes minimal. This app only asks for openid, email, and profile.
- If the app later asks for Gmail, Drive, Calendar, or other sensitive data, Google verification may be required.


Short Summary
=============

Google proves who the user is.
Your backend creates or finds the local user.
Your backend creates a JWT.
The frontend sends that JWT to access protected backend routes.
The database stores the local user record, not the Google password.
