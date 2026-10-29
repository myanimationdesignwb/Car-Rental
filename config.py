import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///rohit_transport.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    BUSINESS_NAME = "Rohit Transport, Tour and Travels"
    BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "+91 96085 76670")
    OWNER_WHATSAPP = os.getenv("OWNER_WHATSAPP", "919608576670")
    OWNER_EMAIL = os.getenv("OWNER_EMAIL", "owner@example.com")
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
    GA_ID = os.getenv("GA_ID", "")
    META_PIXEL_ID = os.getenv("META_PIXEL_ID", "")
