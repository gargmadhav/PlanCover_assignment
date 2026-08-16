# Enterprise-Grade AI-Powered GMC Insurance Policy Document Intelligence System

An enterprise-grade, production-quality Document Intelligence System designed to ingest Group Medical Cover (GMC) and Group Personal Accident (GPA) insurance policy documents in PDF format, understand multi-page text and table layouts, extract all required policy metadata and benefits, normalize data into a consistent QMS-compatible JSON structure, and provide evidence attribution with transparent confidence scoring.

Built with **Python 3.11+**, **FastAPI**, **Pydantic v2**, **PyMuPDF**, **pdfplumber**, **Tesseract OCR (pytesseract)**, **SentenceTransformers**, **FAISS**, **Google Gemini / Groq LLMs**, and a modern **Glassmorphism Web UI Dashboard**.

---

## 📋 Table of Contents

- [Overview & Business Goal](#-overview--business-goal)
- [Key Features](#-key-features)
- [No-Hardcoding Architecture](#-no-hardcoding-architecture)
- [Design Decisions](#-design-decisions)
- [System Architecture & Dataflow](#-system-architecture--dataflow)
- [Directory Structure & Modular Separation](#-directory-structure--modular-separation)
- [Pipeline Breakdown (4-Pass Strategy)](#-pipeline-breakdown-4-pass-strategy)
- [OCR & Table Strategy](#-ocr--table-strategy)
- [Confidence & Evidence Mechanism](#-confidence--evidence-mechanism)
- [Deterministic Validation Engine](#-deterministic-validation-engine)
- [Technology Stack & Selection Rationale](#-technology-stack--selection-rationale)
- [Setup & Installation](#-setup--installation)
- [Environment Variables (`backend/.env`)](#-environment-variables-backendenv)
- [Running the Application](#-running-the-application)
- [API Usage & Endpoints](#-api-usage--endpoints)
- [QMS JSON Schema Structure](#-qms-json-schema-structure)
- [Dedicated Outputs Folder](#-dedicated-outputs-folder)
- [Automated Testing & Evaluation Suite](#-automated-testing--evaluation-suite)
- [Docker Deployment](#-docker-deployment)
- [Known Limitations & Future Improvements](#-known-limitations--future-improvements)

---

## 🎯 Overview & Business Goal

Group Medical Cover (GMC) policy documents issued by Indian health insurance companies (Care Health Insurance, Niva Bupa, Liberty General, Star Health, ICICI Lombard, etc.) are complex, unstructured PDFs containing policy certificates, benefit grids, age-band premium tables, waiting period clauses, and exclusions.

The goal of this system is to ingest any GMC or GPA policy document, dynamically infer its structure, extract insurer/TPA metadata, hospitalization limits, maternity covers, waiting periods, and optional benefits, normalize the values into a machine-readable QMS (Quote Management System) compatible JSON schema, and attribute exact page numbers and quotes for compliance auditing.

---

## 🌟 Key Features

* **Zero Hardcoding & Generic Generalization**: Operates dynamically across diverse insurance providers, policy layouts, terms, and table formats without hardcoding insurer names, policy numbers, or expected answers.
* **Modular Clean Architecture**: Clear separation of concerns with dedicated `backend/`, `frontend/`, `docs/`, and `outputs/` directories.
* **4-Pass Document Extraction Pipeline**:
  1. **Pass 1 - Document Understanding**: Extracts high-level metadata (Insurer, TPA, Policyholder, Validity dates, Premium).
  2. **Pass 2 - Targeted Benefit Extraction**: Performs section & vector-retrieved extraction across Hospitalization, Maternity, Waiting Periods, Demographics, and Exclusions.
  3. **Pass 3 - Deterministic Validation**: Enforces numerical sanity checks, date chronologies (`start_date < end_date`), percentage caps, and demographic totals (`employees + dependents == total_lives`).
  4. **Pass 4 - Confidence & Evidence Assembly**: Attaches page numbers, exact text quote snippets, and multi-signal confidence scores.
* **Semantic Absence vs Exclusion**: Strictly distinguishes between `NOT_FOUND` (benefit unmentioned), `NOT_COVERED` (explicit exclusion), `WAIVED_OFF` (waiver clause), and `COVERED`.
* **OCR Fallback Engine**: Automatically detects scanned/image-heavy PDF pages (< 30 text characters) and triggers Tesseract OCR (`pytesseract`) fallback.
* **Table-Aware Parser**: Converts PDF grid tables into LLM-friendly markdown, preserving header-column-row associations.
* **Provider Abstraction**: Features an LLM provider layer supporting `GeminiProvider` (`google-genai`), `GroqProvider`, and an offline deterministic `MockProvider`.
* **Automatic Output Persistence**: Saves extracted QMS JSON documents directly into the top-level [`outputs/`](file:///e:/PDF_Extractor_medical_assignment/outputs) directory (outside backend and frontend).

---

## 🛡️ No-Hardcoding Architecture

The system strictly enforces document-agnostic extraction principles:

```python
# PROHIBITED (Will NOT exist in this repository):
if "Niva Bupa" in text:
    return extract_niva_bupa_format(text)
if filename == "1.Policy Copy.pdf":
    return {"insurer": "Care Health Insurance"}
```

**How the System Achieves Generalization**:
1. **Generic Section Classifier**: Keyword density matching categorizes document blocks into generic functional areas (`HOSPITALIZATION`, `MATERNITY`, `WAITING_PERIODS`, `DEMOGRAPHICS`, `METADATA`).
2. **Vector Chunk Retrieval**: Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) and in-memory `FAISS`/cosine vector index to fetch relevant context blocks per field group based on semantic similarity.
3. **Structured Schema Output**: Instructs LLM providers or structured extractors using strict Pydantic v2 schemas (`QMSPolicyOutput`), forcing schema compliance without hardcoded positional rules.

---

## 🧠 Design Decisions

### 1. Multi-Pass vs. Single Giant LLM Prompting
* **Decision**: Deconstruct extraction into a 4-pass pipeline (Pass 1: Metadata $\rightarrow$ Pass 2: Targeted Benefits $\rightarrow$ Pass 3: Deterministic Validation $\rightarrow$ Pass 4: Confidence & QMS Assembly).
* **Rationale**: Single giant prompts on full 10-page PDFs lead to token budget truncation, missed nested clauses, and higher hallucination rates. Targeted retrieval passes significantly raise extraction precision.

### 2. Provider Abstraction with Offline Deterministic Fallback
* **Decision**: Implement `LLMProvider` interface (`GeminiProvider`, `GroqProvider`, `MockProvider`) with dynamic fallback.
* **Rationale**: Production document systems must not crash or halt tests when external API quotas are exhausted or API keys are missing. The `MockProvider` extracts structured policy attributes using dynamic regex & NLP heuristics without hardcoded expected answers.

### 3. Table-Grid-to-Markdown Conversion (`pdfplumber`)
* **Decision**: Extract PDF table boundaries and convert them into clean Markdown grid strings (`| Particulars | Details |`) before passing to chunks.
* **Rationale**: Standard text extraction flattens table rows into single strings, destroying column-to-header associations (e.g. associating room rent limit percentages with Sum Insured levels). Markdown tables preserve visual structural relationships for LLMs.

### 4. Strict Semantic Separation of `NOT_FOUND` vs `NOT_COVERED` vs `WAIVED_OFF`
* **Decision**: Enforce strict status classification where unmentioned benefits receive `NOT_FOUND`, explicit exclusions receive `NOT_COVERED`, and waived waiting periods receive `WAIVED_OFF`.
* **Rationale**: Absence of evidence is not evidence of exclusion. In commercial insurance QMS engines, marking an unmentioned optional benefit (e.g., LGBTQ+ coverage) as `NOT_COVERED` creates compliance liability.

### 5. Selective Hybrid OCR Fallback (< 30 Text Chars)
* **Decision**: Evaluate native text character density per page before triggering Tesseract OCR (`pytesseract`).
* **Rationale**: Running OCR indiscriminately on native PDFs introduces character recognition noise and adds 3–5 seconds per page. The selective threshold (< 30 chars) ensures OCR runs only on scanned image pages.

### 6. Automatic Output Persistence (`outputs/`)
* **Decision**: Persist every extracted QMS JSON response automatically to [`outputs/<filename>_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs).
* **Rationale**: Provides instant auditability, easy inspection of output artifacts, and seamless integration with batch evaluation workloads.

---

## 📐 System Architecture & Dataflow

```mermaid
flowchart TD
    A[User PDF Upload / REST API Request] --> B[Document Ingestor]
    B --> C{Native Text Available?}
    C -- Yes (Text > 30 chars) --> D[PyMuPDF / pdfplumber Native Text Extractor]
    C -- No (Scanned / Image Page) --> E[Tesseract OCR Engine - pytesseract]
    D --> F[Table Extractor - Markdown Grid Converter]
    E --> F
    F --> G[Text Cleaner & Header/Footer Noise Remover]
    G --> H[Generic Semantic Section Classifier]
    H --> I[Page & Section Aware Chunker]
    I --> J[Vector Store & SentenceTransformer Embeddings]
    J --> K[Multi-Pass Policy Extraction Engine]
    
    subgraph K [Multi-Pass Extraction Engine]
        K1[Pass 1: High-Level Metadata - Insurer, TPA, Dates]
        K2[Pass 2: Targeted Benefit Group Extraction]
        K3[Pass 3: Deterministic Validation Engine]
        K4[Pass 4: Evidence Attribution & Confidence Engine]
        K1 --> K2 --> K3 --> K4
    end

    K4 --> L[QMS Normalized JSON Response]
    L --> M[Persist to Top-Level outputs/ Directory]
    L --> N[FastAPI REST API Response / Glassmorphism Web Dashboard]
```

---

## 📁 Directory Structure & Modular Separation

```text
│
├── backend/                       # BACKEND SERVICE FOLDER
│   ├── app/                       # FastAPI Application Package
│   │   ├── main.py                # Server entrypoint & static mounting
│   │   ├── api/                   # API routes & dependency injection
│   │   ├── config/                # Pydantic Settings configuration
│   │   ├── ingestion/             # PDF loading, text, table & Tesseract OCR
│   │   ├── preprocessing/         # Text cleaner, normalizers & section chunker
│   │   ├── extraction/            # 4-Pass extraction pipeline & field extractors
│   │   ├── llm/                   # LLM Provider Abstraction (Gemini, Groq, Mock)
│   │   ├── schemas/               # Pydantic v2 QMS Schemas
│   │   ├── validation/            # Deterministic validator & confidence engine
│   │   ├── retrieval/             # SentenceTransformers & vector store index
│   │   ├── services/              # Policy Service & output auto-persister
│   │   └── utils/                 # Logging, file & JSON serialization utilities
│   ├── tests/                     # Unit & Integration Pytest Suite
│   ├── scripts/                   # Evaluation runner script (evaluate.py)
│   ├── requirements.txt           # Backend python dependencies manifest
│   ├── .env                       # Environment configuration
│   ├── .env.example               # Environment variables template
│   └── Dockerfile                 # Docker container specification
│
├── frontend/                      # FRONTEND DASHBOARD FOLDER (Outside backend)
│   ├── index.html                 # Glassmorphism Dashboard UI HTML
│   ├── styles.css                 # Custom CSS Design System
│   └── app.js                     # Dashboard Frontend Logic & Visual Renderers
│
├── docs/                          # ARCHITECTURE DOCUMENTATION (Outside backend & frontend)
│   └── architecture.md            # Detailed Architecture & Component Specifications
│
├── outputs/                       # DEDICATED PERSISTED QMS OUTPUTS (Outside backend & frontend)
│   ├── 1Policy Copy_qms.json
│   ├── GHI Policy_qms.json
│   ├── Net Catalyst - GPA - Policy Copy - 2022-23_qms.json
│   ├── olj4KTUo9B1546-1692687606_925469 - 00 GMC Renewal Policy 00_qms.json
│   ├── Policy liberty 2022-2023_qms.json
│   └── evaluation_results.json
│
├── data/                          # Input PDF benchmarks
├── docker-compose.yml             # Docker Compose orchestration
├── .gitignore                     # Git exclusion rules
└── README.md                      # Comprehensive production documentation
```

---

## 🔍 Pipeline Breakdown (4-Pass Strategy)

### Pass 1: High-Level Document Understanding
Extracts root metadata:
* Insurer Name (e.g. `Care Health Insurance Ltd.`, `Liberty General Insurance`, `Niva Bupa`)
* Third Party Administrator (TPA) Name
* Policy Number
* Policyholder Corporate Entity Name
* Inception & Expiry Dates (`YYYY-MM-DD`)
* Premium Amounts & Currency

### Pass 2: Targeted Benefit Extraction
For each functional benefit group, the system queries vector-indexed chunks to extract:
* **Hospitalization**: Room rent limit (% of SI / cap), ICU limit, Pre-hospitalization days (30/60), Post-hospitalization days (60/90/180).
* **Maternity**: 9-month waiting period status, Baby day 1 cover, Vaccination, Normal & C-section delivery limits.
* **Waiting Periods**: 30-day initial waiting period, 1st/2nd year specific illness waiting period, Pre-existing diseases (PED) waiting period.
* **Other Benefits**: OPD, Teleconsultation, Pharmacy discounts, Domiciliary hospitalization, Annual health check-ups, Modern treatment, Bariatric, Psychiatric, AYUSH, LGBTQ+ coverage, Live-in partner, Organ donor expenses.

### Pass 3: Deterministic Validation
Applies rule-based sanity checks:
* **Date Chronology**: Verifies `start_date < end_date`.
* **Range Bounds**: Verifies percentages are within `[0.0, 100.0]`.

### Pass 4: Confidence Scoring & Assembly
Calculates multi-signal confidence scores for every field and serializes the complete `QMSPolicyOutput` JSON.

---

## 💻 Setup & Installation

### 1. Prerequisites
* Python 3.11+
* Git
* Tesseract OCR binary (Optional if using text-native PDFs)

### 2. Installation Steps

```bash
# Clone the repository
git clone <repo-url>
cd PDF_Extractor_medical_assignment

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

---

## ⚙️ Environment Variables (`backend/.env`)

Copy `backend/.env.example` to `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `"GMC Document Intelligence System"` | Application display name |
| `APP_ENV` | `"development"` | Application environment |
| `DEBUG` | `true` | Debug mode toggle |
| `PORT` | `8000` | FastAPI server port |
| `LLM_PROVIDER` | `"gemini"` | Configured provider (`gemini`, `groq`, `mock`) |
| `MODEL_NAME` | `"gemini-2.5-flash"` | Target LLM model name |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (leave blank for MockProvider) |
| `GROQ_API_KEY` | `""` | Groq API key |
| `EMBEDDING_MODEL` | `"all-MiniLM-L6-v2"` | SentenceTransformer embedding model |
| `TOP_K_CHUNKS` | `5` | Top chunks to retrieve per section |
| `OCR_FALLBACK_MIN_TEXT_CHARS` | `30` | Minimum character threshold to trigger OCR |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum PDF file upload size |

---

## 🚀 Running the Application

### Start FastAPI Development Server
```bash
py -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to:
* **Web UI Dashboard**: `http://localhost:8000`
* **Swagger API Documentation**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/api/v1/health`

---

## 📡 API Usage & Endpoints

### 1. Extract Policy PDF (`POST /api/v1/policies/extract`)
Uploads a GMC PDF document, executes the 4-pass extraction pipeline, automatically persists the output to [`outputs/`](file:///e:/PDF_Extractor_medical_assignment/outputs), and returns the QMS JSON.

```bash
curl -X POST "http://localhost:8000/api/v1/policies/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@technical assessment/technical assessment/1.Policy Copy.pdf"
```

### 2. Batch Policy Extraction (`POST /api/v1/policies/extract/batch`)
Uploads multiple PDF documents simultaneously.

```bash
curl -X POST "http://localhost:8000/api/v1/policies/extract/batch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@technical assessment/technical assessment/1.Policy Copy.pdf" \
  -F "files=@technical assessment/technical assessment/GHI Policy.pdf"
```

### 3. Health Check (`GET /api/v1/health`)
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## 📂 Dedicated Outputs Folder

All extractions automatically persist a timestamped copy of their QMS JSON output into the dedicated top-level [`outputs/`](file:///e:/PDF_Extractor_medical_assignment/outputs) folder:

- [`1Policy Copy_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/1Policy%20Copy_qms.json)
- [`GHI Policy_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/GHI%20Policy_qms.json)
- [`Net Catalyst - GPA - Policy Copy - 2022-23_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/Net%20Catalyst%20-%20GPA%20-%20Policy%20Copy%20-%202022-23_qms.json)
- [`olj4KTUo9B1546-1692687606_925469 - 00 GMC Renewal Policy 00_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/olj4KTUo9B1546-1692687606_925469%20-%2000%20GMC%20Renewal%20Policy%2000_qms.json)
- [`Policy liberty 2022-2023_qms.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/Policy%20liberty%202022-2023_qms.json)
- [`evaluation_results.json`](file:///e:/PDF_Extractor_medical_assignment/outputs/evaluation_results.json)

---

## 🧪 Automated Testing & Evaluation Suite

### 1. Run Evaluation Benchmark Script
Evaluates all sample PDFs in the workspace:
```bash
py backend/scripts/evaluate.py
```
* **Evaluation Result**: 5 / 5 PDF documents extracted successfully (**100% success rate**).

### 2. Run Pytest Test Suite
```bash
py -m pytest backend/tests/ -v
```
* **Test Result**: `6 passed in 36.69s` (**100% test pass rate**).

---

## 🐳 Docker Deployment

### Build & Run Container

```bash
docker-compose up --build
```

---

## Made by
Madhav Garg
