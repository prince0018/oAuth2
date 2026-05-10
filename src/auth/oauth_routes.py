from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv
from src.auth.jwt_handler import create_token, decode_token
from src.db.users import get_or_create_user, get_user_by_id

load_dotenv()

router = APIRouter()

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/google")


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
        raise HTTPException(status_code=400, detail=f"Failed to authorize: {str(e)}")
    
    # Extract user info from token
    user_info = token.get('userinfo')
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    # Extract only email and username from Google
    email = user_info.get('email')
    username = user_info.get('name', email.split('@')[0])  # Use name or part of email
    google_id = user_info.get('sub')  # Google's unique user ID
    
    # Get or create user in our database
    user_id = get_or_create_user(email, username, google_id)
    
    if not user_id:
        raise HTTPException(status_code=500, detail="Could not create/get user")
    
    # Create JWT token
    access_token = create_token(user_id)
    
    # Return token to frontend (or redirect with token)
    # For now, return JSON response
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
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
