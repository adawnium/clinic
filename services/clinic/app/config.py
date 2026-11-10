"""Configuration through environment variables: the code does not change, the configuration does."""

import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./clinic.db")
ALLOWED_ORIGINS = [o for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o]
