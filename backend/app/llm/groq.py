import json
from typing import Type, Dict, Any
from pydantic import BaseModel
from backend.app.llm.base import LLMProvider
from backend.app.config.settings import settings
from backend.app.utils.logging import logger

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or settings.GROQ_API_KEY
        self._model = model or settings.MODEL_NAME or "llama-3.3-70b-versatile"
        self._client = None

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._model

    def _get_client(self):
        if self._client is None and self._api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self._api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        return self._client

    async def extract_structured(self, prompt: str, schema_cls: Type[BaseModel]) -> Dict[str, Any]:
        client = self._get_client()
        if not client:
            raise ValueError("Groq API client not configured or missing GROQ_API_KEY")

        try:
            schema_json = json.dumps(schema_cls.model_json_schema())
            full_prompt = f"{prompt}\n\nYou MUST respond with valid JSON matching this schema strictly:\n{schema_json}"

            completion = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are a specialized document intelligence LLM extractor for insurance policies."},
                    {"role": "user", "content": full_prompt}
                ],
                response_format={"type": "json_object"}
            )

            raw_text = completion.choices[0].message.content or "{}"
            return json.loads(raw_text)

        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise e
