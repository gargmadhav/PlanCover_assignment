from backend.app.llm.base import LLMProvider
from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.groq import GroqProvider
from backend.app.llm.mock import MockProvider
from backend.app.config.settings import settings
from backend.app.utils.logging import logger

class LLMFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        provider_type = settings.LLM_PROVIDER.lower().strip()
        
        if provider_type == "gemini":
            if settings.GEMINI_API_KEY:
                logger.info(f"Using Gemini Provider with model '{settings.MODEL_NAME}'")
                return GeminiProvider()
            else:
                logger.warning("GEMINI_API_KEY not set in environment. Falling back to MockProvider.")
                return MockProvider()
                
        elif provider_type == "groq":
            if settings.GROQ_API_KEY:
                logger.info(f"Using Groq Provider with model '{settings.MODEL_NAME}'")
                return GroqProvider()
            else:
                logger.warning("GROQ_API_KEY not set in environment. Falling back to MockProvider.")
                return MockProvider()
                
        logger.info("Using MockProvider for structured document extraction.")
        return MockProvider()
