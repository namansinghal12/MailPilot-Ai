from app.services import auth_service, google_oauth


def test_google_oauth_scopes_are_consistent():
    assert google_oauth.GOOGLE_SCOPES == auth_service.GOOGLE_SCOPES
    assert "https://www.googleapis.com/auth/gmail.modify" in google_oauth.GOOGLE_SCOPES
