import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config


class GoogleAuthService:
    def __init__(self):
        self.scopes = Config.GOOGLE_SCOPES
        self.credentials_file = Config.GOOGLE_CREDENTIALS_FILE
        self.token_file = "credentials/token.json"

    def get_credentials(self):
        """Get valid user credentials from storage."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, self.scopes
                )

                # If credentials are expired but have refresh token, try to refresh
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        # Save refreshed credentials
                        with open(self.token_file, "w") as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        print(f"Failed to refresh credentials: {e}")
                        creds = None
            except Exception as e:
                print(f"Failed to load credentials: {e}")
                creds = None

        return creds

    def is_authenticated(self):
        """Check if user is authenticated."""
        try:
            creds = self.get_credentials()
            return creds and creds.valid
        except Exception:
            return False
