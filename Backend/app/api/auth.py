import requests

from google.oauth2.credentials import Credentials



import secrets

from passlib.context import CryptContext

from pydantic import BaseModel, EmailStr



from fastapi import APIRouter, HTTPException, Request, Depends

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from googleapiclient.discovery import build



from app.core.config import settings

from app.core.security import create_access_token

from app.database.session import get_db

from app.models.user import User

from app.services.google_oauth import create_google_flow





router = APIRouter(

    prefix="/api/auth",

    tags=["Authentication"],

)



pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto",

)



class RegisterRequest(BaseModel):

    name: str

    email: EmailStr

    password: str





class LoginRequest(BaseModel):

    email: EmailStr

    password: str





@router.post("/register")

def register(

    data: RegisterRequest,

    db: Session = Depends(get_db),

):

    existing_user = (

        db.query(User)

        .filter(User.email == data.email)

        .first()

    )



    if existing_user:

        raise HTTPException(

            status_code=409,

            detail="An account with this email already exists",

        )



    if len(data.password) < 8:

        raise HTTPException(

            status_code=400,

            detail="Password must be at least 8 characters",

        )



    password_hash = pwd_context.hash(

        data.password

    )



    user = User(

        name=data.name,

        email=data.email,

        password_hash=password_hash,

        is_active=True,

    )



    db.add(user)

    db.commit()

    db.refresh(user)



    access_token = create_access_token(

        {

            "sub": user.id,

            "email": user.email,

        }

    )



    response = {

        "message": "Account created successfully",

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "profile_picture": user.profile_picture,

            "profession": user.profession,

        },

    }



    # We'll use the same HTTP-only cookie approach.

    from fastapi.responses import JSONResponse



    json_response = JSONResponse(

        content=response

    )



    json_response.set_cookie(

        key="mailpilot_access_token",

        value=access_token,

        httponly=True,

        secure=False,

        samesite="lax",

        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,

    )



    return json_response



@router.post("/login")

def login(

    data: LoginRequest,

    db: Session = Depends(get_db),

):

    user = (

        db.query(User)

        .filter(User.email == data.email)

        .first()

    )



    if not user or not user.password_hash:

        raise HTTPException(

            status_code=401,

            detail="Invalid email or password",

        )



    if not pwd_context.verify(

        data.password,

        user.password_hash,

    ):

        raise HTTPException(

            status_code=401,

            detail="Invalid email or password",

        )



    if not user.is_active:

        raise HTTPException(

            status_code=403,

            detail="User account is inactive",

        )



    access_token = create_access_token(

        {

            "sub": user.id,

            "email": user.email,

        }

    )



    from fastapi.responses import JSONResponse



    response = JSONResponse(

        content={

            "message": "Login successful",

            "user": {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "profile_picture": user.profile_picture,

                "profession": user.profession,

            },

        }

    )



    response.set_cookie(

        key="mailpilot_access_token",

        value=access_token,

        httponly=True,

        secure=False,

        samesite="lax",

        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,

    )



    return response





@router.get("/google/login")

def google_login():

    flow = create_google_flow()



    state = secrets.token_urlsafe(32)



    if not flow.code_verifier:

        flow.code_verifier = secrets.token_urlsafe(64)



    code_verifier = flow.code_verifier



    authorization_url, _ = flow.authorization_url(

    access_type="offline",

    include_granted_scopes="true",

    prompt="consent",

    state=state,

)





    response = RedirectResponse(url=authorization_url)



    response.set_cookie(

        key="oauth_state",

        value=state,

        max_age=600,

        httponly=True,

        secure=False,

        samesite="lax",

    )



    response.set_cookie(

        key="oauth_code_verifier",

        value=code_verifier,

        max_age=600,

        httponly=True,

        secure=False,

        samesite="lax",

    )



    return response





@router.get("/google/callback")

def google_callback(

    request: Request,

    code: str | None = None,

    state: str | None = None,

    error: str | None = None,

    db: Session = Depends(get_db),

):

    if error:

        raise HTTPException(

            status_code=400,

            detail=f"Google OAuth error: {error}",

        )



    if not code:

        raise HTTPException(

            status_code=400,

            detail="Authorization code missing",

        )



    saved_state = request.cookies.get("oauth_state")



    if not saved_state or not state or not secrets.compare_digest(

        saved_state,

        state,

    ):

        raise HTTPException(

            status_code=400,

            detail="Invalid OAuth state",

        )



    code_verifier = request.cookies.get("oauth_code_verifier")



    if not code_verifier:

        raise HTTPException(

            status_code=400,

            detail="OAuth code verifier missing",

        )



    try:
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            },
            timeout=15,
        )

        token_data = token_response.json()

        if not token_response.ok:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Google token exchange failed: "
                    f"{token_data.get('error_description') or token_data.get('error') or token_data}"
                ),
            )

        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="Google access token was not returned",
            )

        credentials = Credentials(
            token=access_token,
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/gmail.modify",
            ],
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange Google authorization code: {exc}",
        )





    if not credentials.token:

        raise HTTPException(

            status_code=400,

            detail="Google access token was not returned",

        )



    # ---------------------------------------------------------

    # GET REAL GOOGLE USER INFORMATION

    # ---------------------------------------------------------



    try:

        oauth2_service = build(

            "oauth2",

            "v2",

            credentials=credentials,

        )



        google_user = (

            oauth2_service.userinfo()

            .get()

            .execute()

        )



    except Exception as exc:

        raise HTTPException(

            status_code=400,

            detail=f"Failed to fetch Google user information: {exc}",

        )



    google_id = google_user.get("id")

    email = google_user.get("email")

    name = google_user.get("name") or email

    picture = google_user.get("picture")



    if not google_id or not email:

        raise HTTPException(

            status_code=400,

            detail="Google account information is incomplete",

        )



    # ---------------------------------------------------------

    # FIND OR CREATE USER IN SUPABASE

    # ---------------------------------------------------------



    user = (

        db.query(User)

        .filter(User.google_id == google_id)

        .first()

    )



    if not user:

        user = (

            db.query(User)

            .filter(User.email == email)

            .first()

        )



    if user:

        user.google_id = google_id

        user.name = name

        user.profile_picture = picture



        # Google may not return a refresh token every time.

        if credentials.refresh_token:

            user.google_refresh_token = credentials.refresh_token



    else:

        user = User(

            name=name,

            email=email,

            google_id=google_id,

            google_refresh_token=credentials.refresh_token,

            profile_picture=picture,

            is_active=True,

        )



        db.add(user)



    db.commit()

    db.refresh(user)



    # ---------------------------------------------------------

    # CREATE MAILPILOT JWT

    # ---------------------------------------------------------



    access_token = create_access_token(

        {

            "sub": user.id,

            "email": user.email,

        }

    )



    # ---------------------------------------------------------

    # STORE SESSION IN HTTP-ONLY COOKIE

    # ---------------------------------------------------------



    response = RedirectResponse(

    url=f"{settings.FRONTEND_URL}/dashboard"

)



    response.set_cookie(

        key="mailpilot_access_token",

        value=access_token,

        httponly=True,

        secure=False,

        samesite="lax",

        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,

    )



    response.delete_cookie("oauth_state")

    response.delete_cookie("oauth_code_verifier")



    return response





from app.dependencies.auth import get_current_user



class OnboardingRequest(BaseModel):

    role: str





@router.get("/me")

def get_current_user_endpoint(

    current_user: User = Depends(get_current_user),

):

    return {

        "id": current_user.id,

        "name": current_user.name,

        "email": current_user.email,

        "profile_picture": current_user.profile_picture,

        "profession": current_user.profession,

    }





@router.post("/onboarding")

def complete_onboarding(

    data: OnboardingRequest,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db),

):

    current_user.profession = data.role

    db.commit()

    db.refresh(current_user)

    return {

        "id": current_user.id,

        "name": current_user.name,

        "email": current_user.email,

        "profile_picture": current_user.profile_picture,

        "profession": current_user.profession,

    }





@router.post("/logout")

def logout():

    from fastapi.responses import JSONResponse

    response = JSONResponse(

        content={

            "message": "Logged out successfully"

        }

    )



    response.delete_cookie(

        key="mailpilot_access_token",

        httponly=True,

        secure=False,

        samesite="lax",

    )



    return response
