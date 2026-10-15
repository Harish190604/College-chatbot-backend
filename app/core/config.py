import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "karpagam_college_chatbot_secret_key_2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "karpagam_jwt_token_secret_key_987654321")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Absolute path to backend/instance/karpagam_chatbot.db
    INSTANCE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "instance", "karpagam_chatbot.db"))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{INSTANCE_DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

