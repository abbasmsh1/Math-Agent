"""Configuration management for the Math Agent System"""
import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""
    
    # Mistral AI Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")
    
    # API Configuration
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))
    TOP_P: float = float(os.getenv("TOP_P", "0.95"))
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def get_api_key(cls, session_key: Optional[str] = None) -> str:
        """Get API key from session or environment"""
        # Priority: session key > environment variable
        if session_key:
            return session_key
        return cls.MISTRAL_API_KEY
    
    @classmethod
    def validate(cls, api_key: Optional[str] = None) -> None:
        """Validate that required configuration is present"""
        key = cls.get_api_key(api_key)
        if not key:
            raise ValueError(
                "MISTRAL_API_KEY is required. "
                "Please set it in your .env file, environment variables, or in the application settings."
            )
        logger.info("Configuration validated successfully")
    
    @classmethod
    def get_mistral_client(cls, api_key: Optional[str] = None):
        """Get a configured Mistral AI client"""
        from mistralai import Mistral
        key = cls.get_api_key(api_key)
        cls.validate(key)
        return Mistral(api_key=key)

