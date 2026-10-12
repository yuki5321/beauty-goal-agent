import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    YOUCAM_API_KEY: str = os.getenv("YOUCAM_API_KEY", "")
    YOUCAM_BASE_URL: str = os.getenv("YOUCAM_BASE_URL", "https://yce-api-01.makeupar.com")
    YOUCAM_POLL_TIMEOUT: float = float(os.getenv("YOUCAM_POLL_TIMEOUT", "90"))
    USE_MOCK_YOUCAM: bool = os.getenv("USE_MOCK_YOUCAM", "false").lower() in ("true", "1", "yes")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    CORS_ALLOW_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()
    ]
    MAX_REPLAN_ITERATIONS: int = 3
    SCORE_CONVERGENCE_THRESHOLD: int = int(os.getenv("SCORE_CONVERGENCE_THRESHOLD", "85"))

settings = Settings()
