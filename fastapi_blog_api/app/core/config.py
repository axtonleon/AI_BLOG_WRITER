# config.py

import os
from dotenv import load_dotenv

load_dotenv(".env.example")

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()
