from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EXAM-AI-COACH"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    VAULT_DIR: Path = BASE_DIR / "vault"
    DATABASE_PATH: Path = BASE_DIR / "backend" / "exam_coach.db"
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"
    SYNC_DATABASE_URL: str = f"sqlite:///{DATABASE_PATH.as_posix()}"
    
    # AI API Keys
    GEMINI_API_KEY: str = ""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
