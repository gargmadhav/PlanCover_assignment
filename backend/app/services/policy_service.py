import os
from typing import Dict, Any, List
from backend.app.ingestion.document_processor import DocumentIngestor
from backend.app.extraction.extraction_pipeline import PolicyExtractionPipeline
from backend.app.schemas.response import QMSPolicyOutput
from backend.app.utils.file_utils import save_temp_file, cleanup_temp_file
from backend.app.utils.json_utils import dumps_json
from backend.app.utils.logging import logger

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "outputs"))

class PolicyService:
    def __init__(self):
        self.pipeline = PolicyExtractionPipeline()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _save_qms_json(self, output: QMSPolicyOutput, original_filename: str):
        """Automatically persists extracted QMS JSON into dedicated top-level outputs folder."""
        try:
            base_name = os.path.splitext(original_filename)[0]
            clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '_', '-')).strip()
            json_filename = f"{clean_name}_qms.json"
            save_path = os.path.join(OUTPUT_DIR, json_filename)
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(dumps_json(output.model_dump()))
                
            logger.info(f"Persisted QMS JSON output to '{save_path}'")
        except Exception as e:
            logger.error(f"Failed to save QMS output file: {e}")

    async def process_pdf_file(self, file_bytes: bytes, filename: str) -> QMSPolicyOutput:
        temp_path = save_temp_file(file_bytes, filename)
        try:
            doc = DocumentIngestor.process_pdf(temp_path, filename=filename)
            output = await self.pipeline.execute(doc)
            self._save_qms_json(output, filename)
            return output
        finally:
            cleanup_temp_file(temp_path)

    async def process_pdf_path(self, filepath: str) -> QMSPolicyOutput:
        filename = os.path.basename(filepath)
        doc = DocumentIngestor.process_pdf(filepath, filename=filename)
        output = await self.pipeline.execute(doc)
        self._save_qms_json(output, filename)
        return output

policy_service = PolicyService()
