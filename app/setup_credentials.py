"""
Script to generate credentials.json from environment variables.
This should be run at application startup to create the credentials file
without storing it in version control.
"""
import os
import json
from pathlib import Path


def create_credentials_file():
    """
    Creates credentials.json from environment variables.
    Returns the path to the created file.
    """
    # Get the directory where this script is located
    from constants import APP_PATH
    credentials_path = APP_PATH / "credentials.json"

    # Read credentials from environment variables
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    project_id = os.getenv("GOOGLE_PROJECT_ID", "billabee-467612")
    
    # Validate required variables
    if not client_id or not client_secret:
        raise ValueError(
            "Missing required environment variables: GOOGLE_CLIENT_ID and/or GOOGLE_CLIENT_SECRET"
        )
    
    # Create the credentials structure
    credentials = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Write to file
    with open(credentials_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✓ credentials.json created successfully at {credentials_path}")
    return credentials_path


if __name__ == "__main__":
    create_credentials_file()
