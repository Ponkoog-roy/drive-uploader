from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def authenticate_google_drive():
    creds = None

    # Load saved login
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # First login
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            scopes=SCOPES
        )

        creds = flow.run_local_server(port=8080)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service