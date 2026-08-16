# Architecture Documentation - GMC Policy Document Intelligence System

## System Architecture

```mermaid
flowchart TD
    A[User PDF Upload / API Request] --> B[Document Ingestor]
    B --> C{Text Native?}
    C -- Yes --> D[PyMuPDF / pdfplumber Text Extractor]
    C -- Sparse/No Text --> E[RapidOCR Fallback Engine]
    D --> F[Table Extractor - Markdown Grid Converter]
    E --> F
    F --> G[Text Cleaner & Header/Footer Noise Remover]
    G --> H[Generic Semantic Section Classifier]
    H --> I[Page & Section Aware Chunker]
    I --> J[Vector Store & SentenceTransformer Embeddings]
    J --> K[Multi-Pass Policy Extraction Pipeline]
    
    subgraph Multi-Pass Extraction Pipeline
        K1[Pass 1: High Level Document Understanding - Insurer, TPA, Dates]
        K2[Pass 2: Targeted Benefit Group Extraction - Hospitalization, Maternity, Waiting]
        K3[Pass 3: Deterministic Validation Engine - Dates, Ranges, Math]
        K4[Pass 4: Evidence Attribution & Confidence Scoring Engine]
        K1 --> K2 --> K3 --> K4
    end

    K4 --> L[Normalized QMS JSON Output]
    L --> M[FastAPI REST API / Downloadable JSON / Web Dashboard UI]
```

## Modular Layer Breakdown

1. **Ingestion Layer (`app/ingestion/`)**:
   - `pdf_loader.py`: Opens PDF streams safely.
   - `text_extractor.py`: Extracts native text stream with spatial coordinates. Triggers OCR if text char count < 30 per page.
   - `ocr.py`: `Tesseract OCR` (`pytesseract`) engine for scanned image pages.
   - `table_extractor.py`: Extracts grid structures using `pdfplumber` and serializes them as LLM-ready markdown tables.
   - `document_processor.py`: Assembles `InternalDoc` object.

2. **Preprocessing Layer (`app/preprocessing/`)**:
   - `cleaner.py`: Standardizes text, strips null bytes, fixes reversed text snippets.
   - `normalizer.py`: Standardizes dates (`YYYY-MM-DD`), monetary values (`500000.0 INR`), percentage numbers, and status codes (`COVERED`, `NOT_COVERED`, `WAIVED_OFF`, `NOT_FOUND`, `UNKNOWN`).
   - `section_detector.py`: Keyword density and sentence structure section classifier.
   - `chunker.py`: Constructs `DocChunk`s with page and section metadata.

3. **Retrieval & Embedding Layer (`app/retrieval/`)**:
   - `embeddings.py`: Embeds chunks using `all-MiniLM-L6-v2`.
   - `vector_store.py`: In-memory similarity index.
   - `retriever.py`: Section-focused chunk retrieval.

4. **LLM Abstraction Layer (`app/llm/`)**:
   - `base.py`: Provider interface.
   - `gemini.py`: Integration with Google Gemini SDK (`google-genai`).
   - `groq.py`: Integration with Groq Llama 3 SDK.
   - `mock.py`: Smart deterministic fallback engine.
   - `factory.py`: Configurable provider factory.

5. **Validation & Confidence Layer (`app/validation/`)**:
   - `validator.py`: Checks date chronologies, demographic totals, percentage ranges.
   - `confidence.py`: Computes transparent multi-signal confidence scores [0.0 - 1.0].
