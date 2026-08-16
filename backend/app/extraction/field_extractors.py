from typing import Dict, Any, List
from backend.app.llm.base import LLMProvider
from backend.app.preprocessing.chunker import DocChunk
from backend.app.retrieval.retriever import SemanticRetriever
from backend.app.extraction.prompts import (
    SYSTEM_PROMPT, PASS1_DOCUMENT_UNDERSTANDING_PROMPT, PASS2_BENEFIT_EXTRACTION_PROMPT
)
from backend.app.schemas.policy import InsurerDetails, PolicyMetadata, PreviousPolicyDetails, PolicyStructure, DemographicsDetails
from backend.app.schemas.benefits import (
    HospitalizationDetails, MaternityDetails, WaitingPeriodDetails,
    OtherBenefitsDetails, InfertilitySurrogacyDetails, AmbulanceDetails, BufferWaiverDetails
)
from backend.app.utils.logging import logger

class FieldExtractors:
    def __init__(self, provider: LLMProvider, retriever: SemanticRetriever):
        self.provider = provider
        self.retriever = retriever

    async def extract_pass1_metadata(self, chunks: List[DocChunk]) -> Dict[str, Any]:
        """Pass 1: High-level document metadata, insurer, policy numbers, dates."""
        metadata_chunks = [c for c in chunks if c.section in ["POLICY_METADATA", "INSURER_HEADER", "GENERAL"]]
        context_str = "\n\n".join([f"[Page {c.pages[0]}]\n{c.content}" for c in metadata_chunks[:4]])
        
        prompt = f"{SYSTEM_PROMPT}\n{PASS1_DOCUMENT_UNDERSTANDING_PROMPT.format(context=context_str)}"
        
        try:
            return await self.provider.extract_structured(prompt, PolicyMetadata)
        except Exception as e:
            logger.warning(f"LLM Pass 1 extraction failed: {e}. Falling back to chunk context inspection.")
            return {}

    async def extract_hospitalization(self) -> Dict[str, Any]:
        chunks = self.retriever.retrieve_chunks_for_section("HOSPITALIZATION", "room rent icu pre post hospitalization", top_k=4)
        context_str = "\n\n".join([f"[Page {c.pages[0]}]\n{c.content}" for c in chunks])
        prompt = f"{SYSTEM_PROMPT}\n{PASS2_BENEFIT_EXTRACTION_PROMPT.format(field_group_name='Hospitalization & Room Rent', context=context_str)}"
        
        try:
            return await self.provider.extract_structured(prompt, HospitalizationDetails)
        except Exception as e:
            logger.warning(f"LLM Hospitalization extraction error: {e}")
            return {}

    async def extract_maternity(self) -> Dict[str, Any]:
        chunks = self.retriever.retrieve_chunks_for_section("MATERNITY", "maternity normal delivery c-section baby day one vaccination", top_k=4)
        context_str = "\n\n".join([f"[Page {c.pages[0]}]\n{c.content}" for c in chunks])
        prompt = f"{SYSTEM_PROMPT}\n{PASS2_BENEFIT_EXTRACTION_PROMPT.format(field_group_name='Maternity Benefits', context=context_str)}"
        
        try:
            return await self.provider.extract_structured(prompt, MaternityDetails)
        except Exception as e:
            logger.warning(f"LLM Maternity extraction error: {e}")
            return {}

    async def extract_waiting_periods(self) -> Dict[str, Any]:
        chunks = self.retriever.retrieve_chunks_for_section("WAITING_PERIODS", "waiting period 30 days initial ped pre-existing disease specific illness", top_k=4)
        context_str = "\n\n".join([f"[Page {c.pages[0]}]\n{c.content}" for c in chunks])
        prompt = f"{SYSTEM_PROMPT}\n{PASS2_BENEFIT_EXTRACTION_PROMPT.format(field_group_name='Waiting Periods & Exclusions', context=context_str)}"
        
        try:
            return await self.provider.extract_structured(prompt, WaitingPeriodDetails)
        except Exception as e:
            logger.warning(f"LLM Waiting Periods extraction error: {e}")
            return {}

    async def extract_other_benefits(self) -> Dict[str, Any]:
        chunks = self.retriever.retrieve_chunks_for_section("OTHER_BENEFITS", "opd teleconsultation ayush health checkup modern treatment bariatric psychiatric", top_k=4)
        context_str = "\n\n".join([f"[Page {c.pages[0]}]\n{c.content}" for c in chunks])
        prompt = f"{SYSTEM_PROMPT}\n{PASS2_BENEFIT_EXTRACTION_PROMPT.format(field_group_name='Other Policy Benefits', context=context_str)}"
        
        try:
            return await self.provider.extract_structured(prompt, OtherBenefitsDetails)
        except Exception as e:
            logger.warning(f"LLM Other Benefits extraction error: {e}")
            return {}
