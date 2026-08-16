import os
import sys
import asyncio

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.services.policy_service import policy_service

SAMPLE_PDF = os.path.join(root_dir, "technical assessment", "technical assessment", "1.Policy Copy.pdf")

def test_full_pipeline():
    if not os.path.exists(SAMPLE_PDF):
        return
        
    result = asyncio.run(policy_service.process_pdf_path(SAMPLE_PDF))
    assert result is not None
    assert result.document_metadata.filename == "1.Policy Copy.pdf"
    assert result.document_metadata.page_count == 4
    assert result.insurer_details is not None
    assert result.extraction_metadata.overall_confidence >= 0.0
