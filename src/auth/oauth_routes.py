from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
from urllib.parse import urlencode, urlsplit, urlunsplit

from src.auth.jwt_handler import create_token, decode_token
from src.config import get_settings
from src.db.users import get_or_create_user, get_user_by_id


router = APIRouter()
settings = get_settings()

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/google")


def _auth_error(detail: str = "Invalid authentication credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_google_profile(user_info: dict) -> tuple[str, str, str]:
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")

    email = user_info.get('email')
    google_id = user_info.get('sub')

    if not email or not google_id:
        raise HTTPException(status_code=400, detail="Google did not return required profile fields")

    if user_info.get('email_verified') is not True:
        raise HTTPException(status_code=403, detail="Google email is not verified")

    username = user_info.get('name') or email.split('@')[0]
    return email, username, google_id


def _frontend_success_redirect(access_token: str, user_id: int) -> RedirectResponse | None:
    if not settings.frontend_success_url:
        return None

    parts = urlsplit(settings.frontend_success_url)
    fragment = urlencode({
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
    })
    redirect_url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, fragment))
    return RedirectResponse(redirect_url)


@router.get("/auth/login/google")
async def login_google(request: Request):
    """
    Redirect user to Google login page.
    User will login with their Gmail account.
    """
    redirect_uri = request.url_for('auth_callback_google')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))


@router.get("/auth/callback/google")
async def auth_callback_google(request: Request):
    """
    Google redirects here after user approves.
    We exchange the authorization code for user data.
    """
    try:
        # Get authorization token from Google
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to authorize with Google") from e

    email, username, google_id = _extract_google_profile(token.get('userinfo'))

    # Get or create user in our database
    try:
        user_id = get_or_create_user(email, username, google_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    if not user_id:
        raise HTTPException(status_code=500, detail="Could not create/get user")

    # Create JWT token
    access_token = create_token(user_id)

    frontend_redirect = _frontend_success_redirect(access_token, user_id)
    if frontend_redirect:
        return frontend_redirect

    return JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id
    })


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency: Extract and validate user from JWT token.
    Used to protect endpoints.
    """
    payload = decode_token(token)

    if not payload:
        raise _auth_error("Invalid or expired token")

    raw_user_id = payload.get("sub") or payload.get("user_id")
    try:
        user_id = int(raw_user_id)
    except (TypeError, ValueError):
        raise _auth_error()

    user = get_user_by_id(user_id)

    if not user:
        raise _auth_error()

    return user


@router.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint: Get current logged-in user details.
    Returns only: username and email.
    """
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }


@router.post("/auth/logout")
def logout():
    """
    Logout endpoint.
    Frontend should delete the token from localStorage.
    """
    return {"message": "Logged out successfully. Please delete token from browser."}
