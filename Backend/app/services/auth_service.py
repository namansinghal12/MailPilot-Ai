from google_auth_oauthlib.flow import Flow

from app.core.config import settings
from app.services.google_oauth import GOOGLE_SCOPES


def create_google_flow() -> Flow:
    from app.services.google_oauth import create_google_flow as _create_google_flow

    return _create_google_flow()