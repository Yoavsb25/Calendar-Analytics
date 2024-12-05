import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your_secret_key"
    GOOGLE_OAUTH_CLIENT_ID = "657802434191-hkm4bqm4vdq2omm864v2mjcdbha4csqb.apps.googleusercontent.com"
    GOOGLE_OAUTH_CLIENT_SECRET = "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"
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
