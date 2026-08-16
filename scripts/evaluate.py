import os
import sys
import json
import asyncio
import time
from typing import List, Dict, Any

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.policy_service import policy_service, OUTPUT_DIR
from app.utils.json_utils import dumps_json
from app.utils.logging import logger

SAMPLE_PDF_DIR = r"e:\PDF_Extractor_medical_assignment\technical assessment\technical assessment"

async def run_evaluation():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    pdfs = [f for f in os.listdir(SAMPLE_PDF_DIR) if f.endswith(".pdf")]
    logger.info(f"Starting Evaluation on {len(pdfs)} sample PDF documents...")
    
    results = []
    
    for pdf_name in pdfs:
        pdf_path = os.path.join(SAMPLE_PDF_DIR, pdf_name)
        logger.info(f"\n=======================================================")
        logger.info(f"Evaluating PDF: {pdf_name}")
        start = time.time()
        
        try:
            output = await policy_service.process_pdf_path(pdf_path)
            duration = round(time.time() - start, 2)
            
            clean_name = "".join(c for c in os.path.splitext(pdf_name)[0] if c.isalnum() or c in (' ', '_', '-')).strip()
            output_json_path = os.path.join(OUTPUT_DIR, f"{clean_name}_qms.json")
                
            res_summary = {
                "filename": pdf_name,
                "document_id": output.document_metadata.document_id,
                "page_count": output.document_metadata.page_count,
                "ocr_pages": output.document_metadata.ocr_pages_count,
                "insurer_detected": output.insurer_details.insurer_name or "Not Inferred",
                "tpa_detected": output.insurer_details.tpa_name or "Direct / None",
                "policy_number": output.policy_metadata.policy_number or "N/A",
                "policyholder": output.policy_metadata.policyholder_name or "N/A",
                "start_date": output.policy_metadata.start_date,
                "end_date": output.policy_metadata.end_date,
                "overall_confidence": output.extraction_metadata.overall_confidence,
                "validation_warnings_count": len(output.validation_warnings),
                "duration_seconds": duration,
                "output_json_path": output_json_path,
                "status": "SUCCESS"
            }
            results.append(res_summary)
            logger.info(f"SUCCESS: Insurer='{res_summary['insurer_detected']}', PolicyNo='{res_summary['policy_number']}', Confidence={res_summary['overall_confidence']}")
            
        except Exception as e:
            logger.error(f"FAILURE on {pdf_name}: {e}", exc_info=True)
            results.append({
                "filename": pdf_name,
                "status": "FAILED",
                "error": str(e)
            })

    eval_results_path = os.path.join(OUTPUT_DIR, "evaluation_results.json")
    with open(eval_results_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_documents": len(pdfs),
            "successful_extractions": sum(1 for r in results if r["status"] == "SUCCESS"),
            "failed_extractions": sum(1 for r in results if r["status"] == "FAILED"),
            "results": results
        }, f, indent=2)
        
    logger.info(f"\n=======================================================")
    logger.info(f"Evaluation Complete! All JSON outputs and summary saved to '{OUTPUT_DIR}'")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
