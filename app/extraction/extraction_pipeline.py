import time
from typing import Dict, Any, List
from app.ingestion.document_processor import InternalDoc
from app.preprocessing.chunker import DocumentChunker, DocChunk
from app.retrieval.vector_store import VectorStore
from app.retrieval.retriever import SemanticRetriever
from app.llm.factory import LLMFactory
from app.llm.mock import MockProvider
from app.extraction.field_extractors import FieldExtractors
from app.schemas.response import QMSPolicyOutput, DocumentMetadata, ExtractionMetadata
from app.schemas.policy import (
    InsurerDetails, PolicyMetadata, PreviousPolicyDetails, PolicyStructure, DemographicsDetails
)
from app.schemas.benefits import (
    HospitalizationDetails, MaternityDetails, WaitingPeriodDetails,
    OtherBenefitsDetails, InfertilitySurrogacyDetails, AmbulanceDetails, BufferWaiverDetails
)
from app.validation.validator import ValidationEngine
from app.validation.confidence import ConfidenceEngine
from app.utils.logging import logger

class PolicyExtractionPipeline:
    def __init__(self):
        self.provider = LLMFactory.get_provider()

    async def execute(self, doc: InternalDoc) -> QMSPolicyOutput:
        start_time = time.time()
        logger.info(f"Starting 4-Pass Extraction Pipeline for document '{doc.filename}' (ID: {doc.document_id})...")

        # Step 1: Chunking & Indexing
        chunks = DocumentChunker.chunk_document(doc)
        vector_store = VectorStore()
        vector_store.index_chunks(chunks)
        retriever = SemanticRetriever(vector_store)
        
        field_extractors = FieldExtractors(self.provider, retriever)

        # PASS 1: Document Understanding (Insurer, TPA, Metadata)
        logger.info("Executing Pass 1: Document understanding & metadata...")
        full_text = "\n\n".join([c.content for c in chunks])
        
        if isinstance(self.provider, MockProvider):
            pass1_data = await self.provider.extract_structured(full_text, QMSPolicyOutput)
        else:
            pass1_data = await field_extractors.extract_pass1_metadata(chunks)

        insurer_info = InsurerDetails(**(pass1_data.get("insurer_details") or {}))
        policy_meta = PolicyMetadata(**(pass1_data.get("policy_metadata") or {}))

        # PASS 2: Targeted Benefit Extraction
        logger.info("Executing Pass 2: Targeted benefit extraction...")
        
        if isinstance(self.provider, MockProvider):
            hosp_dict = await self.provider.extract_structured(full_text, HospitalizationDetails)
            mat_dict = await self.provider.extract_structured(full_text, MaternityDetails)
            wait_dict = await self.provider.extract_structured(full_text, WaitingPeriodDetails)
            demo_dict = await self.provider.extract_structured(full_text, DemographicsDetails)
            other_dict = await self.provider.extract_structured(full_text, OtherBenefitsDetails)
        else:
            hosp_dict = await field_extractors.extract_hospitalization()
            mat_dict = await field_extractors.extract_maternity()
            wait_dict = await field_extractors.extract_waiting_periods()
            demo_dict = {}
            other_dict = await field_extractors.extract_other_benefits()

        hospitalization = HospitalizationDetails(**hosp_dict) if isinstance(hosp_dict, dict) else hosp_dict
        maternity = MaternityDetails(**mat_dict) if isinstance(mat_dict, dict) else mat_dict
        waiting_periods = WaitingPeriodDetails(**wait_dict) if isinstance(wait_dict, dict) else wait_dict
        
        policy_struct = PolicyStructure(**(demo_dict.get("policy_structure") or {})) if isinstance(demo_dict, dict) else PolicyStructure()
        demographics = DemographicsDetails(**(demo_dict.get("demographics") or {})) if isinstance(demo_dict, dict) else DemographicsDetails()
        other_benefits = OtherBenefitsDetails(**other_dict) if isinstance(other_dict, dict) else OtherBenefitsDetails()

        prev_policy = PreviousPolicyDetails()
        infertility = InfertilitySurrogacyDetails()
        ambulance = AmbulanceDetails()
        buffer_waivers = BufferWaiverDetails()

        # PASS 3: Deterministic Validation
        logger.info("Executing Pass 3: Deterministic validation...")
        warnings = ValidationEngine.run_all_validations(policy_meta, demographics, hospitalization)

        # PASS 4: Confidence Scoring & Final Assembly
        logger.info("Executing Pass 4: Confidence calculation & QMS assembly...")
        
        confidences = []
        for benefit_grp in [hospitalization, maternity, waiting_periods, other_benefits]:
            for field_name, b_detail in benefit_grp.model_dump().items():
                if isinstance(b_detail, dict) and "confidence" in b_detail:
                    confidences.append(b_detail["confidence"])
                    
        overall_conf = ConfidenceEngine.calculate_overall_confidence(confidences)

        duration = round(time.time() - start_time, 2)
        ocr_count = sum(1 for p in doc.pages if p.source_type == "ocr")

        qms_output = QMSPolicyOutput(
            document_metadata=DocumentMetadata(
                document_id=doc.document_id,
                filename=doc.filename,
                page_count=doc.page_count,
                file_size_bytes=doc.file_size_bytes,
                ocr_pages_count=ocr_count,
                pages_processed=[p.page_number for p in doc.pages]
            ),
            insurer_details=insurer_info,
            policy_metadata=policy_meta,
            previous_policy_details=prev_policy,
            policy_structure=policy_struct,
            demographics=demographics,
            hospitalization=hospitalization,
            maternity=maternity,
            waiting_periods=waiting_periods,
            other_benefits=other_benefits,
            infertility_surrogacy=infertility,
            ambulance=ambulance,
            buffer_waivers=buffer_waivers,
            validation_warnings=warnings,
            extraction_metadata=ExtractionMetadata(
                provider_used=self.provider.provider_name,
                model_used=self.provider.model_name,
                overall_confidence=overall_conf,
                processing_duration_seconds=duration
            )
        )

        logger.info(f"Pipeline completed successfully in {duration}s. Confidence={overall_conf}")
        return qms_output
