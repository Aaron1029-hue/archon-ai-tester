"""
Configuration settings for the Archon Agent Tester.
"""
from pydantic import BaseSettings, Field, SecretStr


class Settings(BaseSettings):
    """
    Application settings that can be loaded from environment variables or .env file.
    """
    # API keys
    archon_api_key: SecretStr = Field(..., env="ARCHON_API_KEY")
    openrouter_api_key: SecretStr = Field(..., env="OPENROUTER_API_KEY")
    
    # API endpoints
    archon_api_base_url: str = Field("https://api.archon.ai", env="ARCHON_API_BASE_URL")
    openrouter_api_base_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_API_BASE_URL")
    
    # Testing settings
    default_timeout: int = Field(30, env="DEFAULT_TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    default_test_suite: str = Field("functional", env="DEFAULT_TEST_SUITE")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Database
    db_url: str = Field("sqlite:///./tests.db", env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a global settings instance
settings = Settings()