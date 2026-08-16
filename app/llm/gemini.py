import json
from typing import Type, Dict, Any
from pydantic import BaseModel
from app.llm.base import LLMProvider
from app.config.settings import settings
from app.utils.logging import logger

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model = model or settings.MODEL_NAME or "gemini-2.5-flash"
        self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def _get_client(self):
        if self._client is None and self._api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}")
        return self._client

    async def extract_structured(self, prompt: str, schema_cls: Type[BaseModel]) -> Dict[str, Any]:
        client = self._get_client()
        if not client:
            raise ValueError("Gemini API client not configured or missing GEMINI_API_KEY")

        try:
            schema_json = json.dumps(schema_cls.model_json_schema())
            full_prompt = f"{prompt}\n\nYou MUST respond with valid JSON matching this schema exactly:\n{schema_json}"

            response = client.models.generate_content(
                model=self._model,
                contents=full_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': schema_cls
                }
            )
            
            raw_text = response.text or "{}"
            return json.loads(raw_text)

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise e
