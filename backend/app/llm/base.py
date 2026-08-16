from abc import ABC, abstractmethod
from typing import Type, Dict, Any
from pydantic import BaseModel

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    async def extract_structured(self, prompt: str, schema_cls: Type[BaseModel]) -> Dict[str, Any]:
        """
        Submits prompt to LLM and returns a dictionary matching the schema_cls Pydantic structure.
        """
        pass
