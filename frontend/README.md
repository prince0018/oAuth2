# Frontend

This folder contains the optional frontend for the OAuth login system.

The backend can still run without this folder. Use the frontend only when you want a browser UI.

## Run

From the project root:

```bash
cd frontend
python3 -m http.server 3000
```

Then open:

```text
http://localhost:3000
```

## Backend Settings

In the backend `.env`, use:

```env
CORS_ORIGINS=http://localhost:3000
FRONTEND_SUCCESS_URL=http://localhost:3000/
```

Your Google OAuth client must allow this backend callback URI:

```text
http://localhost:8000/auth/callback/google
```
