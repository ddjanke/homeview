from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    render_template,
)
from app.services.auth import GoogleAuthService
from config import Config
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login")
def login():
    """Initiate Google OAuth2 login."""
    try:
        auth_service = GoogleAuthService()

        # Check if already authenticated
        if auth_service.is_authenticated():
            return redirect(url_for("main.dashboard"))

        # Create OAuth2 flow
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            Config.GOOGLE_CREDENTIALS_FILE, scopes=Config.GOOGLE_SCOPES
        )
        flow.redirect_uri = url_for("auth.callback", _external=True)

        # Get authorization URL
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )

        # Store state in session
        session["oauth_state"] = state

        return redirect(authorization_url)

    except Exception as e:
        return jsonify({"success": False, "error": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/callback")
def callback():
    """Handle OAuth2 callback."""
    try:
        # Get authorization code from callback
        code = request.args.get("code")
        state = request.args.get("state")

        if not code:
            return (
                jsonify({"success": False, "error": "No authorization code received"}),
                400,
            )

        # Verify state
        if state != session.get("oauth_state"):
            return jsonify({"success": False, "error": "Invalid state parameter"}), 400

        # Exchange code for credentials
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            Config.GOOGLE_CREDENTIALS_FILE, scopes=Config.GOOGLE_SCOPES
        )
        flow.redirect_uri = url_for("auth.callback", _external=True)

        # Exchange code for token
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Save credentials
        token_file = "credentials/token.json"
        os.makedirs(os.path.dirname(token_file), exist_ok=True)

        with open(token_file, "w") as token:
            token.write(credentials.to_json())

        # Clear session state
        session.pop("oauth_state", None)

        return redirect(url_for("main.dashboard"))

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Authentication failed: {str(e)}"}),
            500,
        )


@auth_bp.route("/logout")
def logout():
    """Logout and clear credentials."""
    try:
        # Remove token file
        token_file = "credentials/token.json"
        if os.path.exists(token_file):
            os.remove(token_file)

        # Clear session
        session.clear()

        return jsonify({"success": True, "message": "Logged out successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": f"Logout failed: {str(e)}"}), 500


@auth_bp.route("/status")
def status():
    """Check authentication status."""
    try:
        auth_service = GoogleAuthService()
        is_authenticated = auth_service.is_authenticated()

        return jsonify({"success": True, "authenticated": is_authenticated})

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Status check failed: {str(e)}"}),
            500,
        )
