OAuth login system using Google OAuth2, FastAPI, PostgreSQL, and JWT access tokens.

Setup:
1. Copy .env.example to .env and fill in Google OAuth, JWT, and DB values.
2. DB_PASSWORD can stay empty if your local PostgreSQL user does not require a password.
3. Install dependencies:
   pip install -r requirements.txt
4. Run the API:
   uvicorn src.main:app --reload

Google OAuth redirect URI:
http://localhost:8000/auth/callback/google

Login flow:
1. Open /auth/login/google.
2. Google redirects back to /auth/callback/google.
3. The callback creates or finds the local user and returns a bearer token.
4. Send Authorization: Bearer <token> to /auth/me.

For a browser frontend, prefer storing tokens in HttpOnly secure cookies before going to production.
