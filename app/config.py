from pydantic_settings import BaseSettings, SettingsConfigDict
import os
current_dir = os.path.dirname(os.path.abspath(__file__))


ENV_PATH = os.path.abspath(os.path.join(current_dir, "..", ".env")) 
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    model_config = SettingsConfigDict(env_file=ENV_PATH)
    
settings = Settings()