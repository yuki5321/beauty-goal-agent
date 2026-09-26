import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    YOUCAM_API_KEY: str = os.getenv("YOUCAM_API_KEY", "")
    YOUCAM_BASE_URL: str = os.getenv("YOUCAM_BASE_URL", "https://api.perfectcorp.com/v1")
    USE_MOCK_YOUCAM: bool = os.getenv("USE_MOCK_YOUCAM", "false").lower() in ("true", "1", "yes")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    MAX_REPLAN_ITERATIONS: int = 3
    SCORE_CONVERGENCE_THRESHOLD: int = 85

settings = Settings()
