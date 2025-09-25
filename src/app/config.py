from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    BOT_TOKEN: str
    WEBHOOK_SECRET: str
    BASE_URL: str
    TZ: str = 'Europe/Helsinki'
    DATABASE_URL: str
    CURRENCY: str = 'XTR'
    MORNING_DEFAULT: str = '09:15'
    EVENING_DEFAULT: str = '21:30'

settings = Settings()
