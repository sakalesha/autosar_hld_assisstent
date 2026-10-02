# Product Requirements Document (PRD)
## AUTOSAR HLD Document Analysis Assistant

| Field | Details |
|---|---|
| Version | 0.1 (Draft) |
| Date | October 2026 |
| Source | *Automotive Engineering AI: Project Case Studies*, Case Study 1 (pp. 4–7) |
| Status | Draft for review |
| Companion document | `Architecture.md` |

**Labeling convention.** Statements are tagged where the distinction matters:
**FACT** (stated in the source document or decided by the project owner), **INFERENCE** (reasoned, not verified), **RECOMMENDATION** (proposed, not yet approved), **OPEN** (undecided).

> **Note on requirement IDs.** FR numbers in this document are provisional. If an earlier PRD with its own FR numbering already exists, reconcile the IDs before using either document for traceability.

---

## 1. Purpose

Build a secure, AI-assisted application that extracts, organizes, searches, and validates architectural knowledge from large AUTOSAR High-Level Design (HLD) documents, so engineers can review designs faster and with better traceability.

The system **assists** engineers. It does not approve architecture decisions or replace formal architecture governance.

## 2. Problem Statement

**FACT (case study):** HLD documents describe software components, interfaces, ports, signals, dependencies, functional flows, and integration logic. They are often hundreds of pages long and kept as unstructured PDFs. Architects, developers, integrators, and testers interpret them manually, which makes it hard to find mismatches, missing dependencies, inconsistent terminology, and incomplete test coverage.

## 3. Goals and Non-Goals

### Goals
1. Reduce manual effort needed to review HLD documents.
2. Create a structured, searchable repository of architecture knowledge.
3. Improve traceability of components, interfaces, signals, and dependencies.
4. Support design reviews, onboarding, impact analysis, and test planning.

### Non-Goals (case study "Out of Scope")
- Automatic approval of architecture decisions.
- Modifying source HLD documents without review.
- Replacing formal architecture governance.

### Non-Goals for the pilot (project decision)
- Revision comparison, inconsistency detection, graph relationships, and role-based access control (deferred, see §5).

## 4. Users and User Stories

| User | Need |
|---|---|
| System / AUTOSAR architects | Understand and validate an architecture quickly |
| Software developers | Find interface and dependency details without reading the full document |
| Integration engineers | Trace signals and ports across components |
| Test engineers | Derive test scope from documented behavior |
| Engineering managers | Assess review progress and findings |

| ID | User story |
|---|---|
| US-1 | As an architect, I upload an approved HLD and get it registered with a version label, so I know which revision answers refer to. |
| US-2 | As a developer, I ask a natural-language question and receive an answer with page citations, so I can verify it in the source. |
| US-3 | As an integrator, I list the components and interfaces found in a document and export them, so I can use them downstream. |
| US-4 | As a reviewer, I accept, edit, or reject extracted items, so only reviewed content is treated as trusted. |
| US-5 | As any user, I see an explicit "not found in the document" response instead of a guess when evidence is missing. |

## 5. Scope

### 5.1 Pilot scope (target: working end-to-end slice in about two days)

| In pilot | Deferred |
|---|---|
| PDF upload, validation, version label, registration | Revision comparison |
| Text, heading, and table extraction | Inconsistency and completeness checks |
| Section-aware chunking | Graph / traceability store |
| Embeddings and local vector search | Role-based access and project isolation |
| Cited question answering with refusal when evidence is missing | Full review state machine |
| Basic component and interface extraction (stretch) | Scanned-page OCR (stretch) |
| JSON/CSV export (stretch) | Enterprise UI, Docker packaging |

**RECOMMENDATION:** Treat the two-day pilot as a technical demonstration on sample documents, not a validated system.
**INFERENCE (confidence about 75%):** a thin vertical slice (upload → cited Q&A, plus basic extraction) is achievable in two days with AI coding tools if the LLM and parser decisions are made early. The full case-study scope is not (confidence under 30%).

### 5.2 Full scope (case study "In Scope")
PDF ingestion, OCR for scanned pages, component/interface/port/signal/flow extraction, cited natural-language search, document comparison and inconsistency reporting, and structured export.

## 6. Functional Requirements

Priority: **P0** pilot must-have, **P1** pilot stretch, **P2** post-pilot.

| ID | Requirement | Priority | Acceptance criteria |
|---|---|---|---|
| FR-1 | **Upload and validation.** Accept PDF uploads through the API. Validate extension, content signature, and size limit. | P0 | Non-PDF or oversized files are rejected with a clear error; no record is created for rejected files. |
| FR-2 | **Version / revision labeling.** Every document carries a version label and an approved-source status. | P0 | Upload without a valid version label is rejected; the same document name and version cannot be registered twice. |
| FR-3 | **Registration and storage.** Generate a document ID, store the file, capture metadata (filename, size, hash, uploader, timestamp), and create a document record with a status. | P0 | A successful upload returns a document ID; the record and stored file both exist and the hash matches. |
| FR-4 | **Content extraction.** Extract text, headings, tables, and page metadata from digital PDFs. | P0 | Each extracted block retains its page number and section path. |
| FR-5 | **OCR fallback.** Run OCR only on pages with no extractable text. | P1 | A scanned page yields text tagged `ocr=true`; digital pages are not OCR'd. |
| FR-6 | **Section-aware chunking.** Split content by section and architecture context, within the embedding model's input limit. | P0 | No chunk exceeds the model's token limit; every chunk keeps document ID, version, page range, and section path. |
| FR-7 | **Embedding and vector storage.** Embed chunks and store them in a persistent local collection. | P0 | Re-running ingestion on the same document does not duplicate chunks; the embedding model name is recorded. |
| FR-8 | **Retrieval.** Retrieve the top-k relevant chunks, filterable by document and version. | P0 | A query returns ranked chunks with similarity scores and source metadata. |
| FR-9 | **Cited question answering.** Generate answers only from retrieved context, with page or section citations. | P0 | Every answer carries at least one valid citation that maps to a retrieved chunk, or an explicit refusal. |
| FR-10 | **Limitation indicator.** Show a confidence or limitation indicator and refuse when evidence is insufficient. | P0 | Out-of-scope or unsupported questions return "not found in the document" rather than a fabricated answer. |
| FR-11 | **Entity extraction.** Extract components, interfaces, ports, signals, and dependencies into a structured inventory. | P1 | Output conforms to the defined schema; each item links to its source page. |
| FR-12 | **Structured export.** Export findings as JSON and CSV. | P1 | Exports are reproducible and include document ID, version, and citations. |
| FR-13 | **Engineer review and audit.** Let engineers accept, edit, or reject extracted items and answers; log decisions. | P1 | Each decision is stored with user, time, and the original and edited values. |
| FR-14 | **Revision comparison and inconsistency checks.** Compare document revisions; flag potential mismatches and missing dependencies. | P2 | Differences between two versions are listed with source references. |
| FR-15 | **Access control and project isolation.** Role-based access and per-project data separation. | P2 | A user cannot retrieve content from a project they are not assigned to. |

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Groundedness | Answers must be restricted to retrieved evidence. **FACT (case study):** risk control for hallucinated relationships. |
| Traceability | Every answer and extracted item must reference document ID, version, and page. |
| Security and data residency | Embeddings stay on the local machine in the pilot. Source PDF documents and structured metadata are stored in a hosted database (see §9, risk R-6). |
| Auditability | Upload, query, and review actions are logged. |
| Reproducibility | Ingestion is idempotent. The embedding model and chunking settings are recorded per document. |
| Usability | A single Streamlit interface for upload, search, review, and export. |
| Performance | Interactive query response. **OPEN:** numeric targets to be set after a baseline measurement on the sample document. |
| Maintainability | The LLM, parser, and OCR engines sit behind interfaces so they can be replaced. |

## 8. Technology Decisions

| Layer | Choice | Status |
|---|---|---|
| UI | Streamlit | **Decided** |
| API | FastAPI (Python) | **Decided** |
| Vector store | ChromaDB (local, persistent) | **Decided** |
| Structured store | PostgreSQL hosted on Neon | **Decided** |
| Containerization | Docker | **Decided: deferred, added last** |
| OCR | Tesseract, as a fallback for scanned pages only | **Proposed** (confirmation pending) |
| Embedding model | `BAAI/bge-base-en-v1.5` (fallback: `bge-small-en-v1.5` if too slow) | **Proposed** (confirmation pending) |
| Document parser | To be decided | **OPEN** |
| LLM | To be decided | **OPEN** (highest-risk open item) |

**RECOMMENDATION notes**
- BGE was chosen over E5 mainly for simpler usage (E5 requires `query:` / `passage:` prefixes). No benchmark evidence on AUTOSAR text exists; the choice should be validated on the benchmark questions in §10.
- Tesseract does not understand diagrams or table structure; do not expect OCR to recover them.

## 9. Risks and Mitigations

| ID | Risk | Mitigation |
|---|---|---|
| R-1 | Incorrect extraction from tables or diagrams | Page-level citations; review queue (FR-13); report extraction quality honestly |
| R-2 | Hallucinated architecture relationships | Answer only from retrieved evidence; refuse when evidence is weak (FR-10); citation validation |
| R-3 | Sample document is not representative of real HLDs | Treat pilot results as a demo; collect a real HLD before claiming validation |
| R-4 | LLM selection or local hosting consumes the schedule | Decide the LLM first; hide it behind an interface; fall back to an approved API if policy allows |
| R-5 | Outdated document versions used for answers | Version labels and approved-source status (FR-2); filter retrieval by version |
| R-6 | Hosted database conflicts with a local-only data principle | Store only structured metadata in Neon; keep text and embeddings local; re-check policy before loading confidential HLDs |
| R-7 | Free-tier database cold starts cause timeouts (**INFERENCE**, verify against current vendor docs) | Connection retry logic; warm the connection before demos |
| R-8 | Scope creep beyond the pilot slice | Fixed pilot scope in §5.1; deferred items stay deferred |
| R-9 | Parser library licensing (some popular PDF libraries use copyleft licenses) | Verify license terms during the parser decision, before any enterprise use |

## 10. Success Metrics

**FACT:** the case study gives indicative metrics without numeric targets.

| Metric | Definition | Pilot approach |
|---|---|---|
| Answer groundedness | % of answers with valid source citations | Automated check; target 100% citation-or-refusal as a design rule |
| Extraction quality | Precision / recall for approved entities | **RECOMMENDATION:** hand-label a small ground-truth set from the sample document |
| Retrieval quality | Does the correct page appear in the top-k? | **RECOMMENDATION:** about 15–20 benchmark questions, graded manually |
| Document review effort | % reduction against baseline | Not measurable in the pilot; needs a baseline from real reviews |
| Issue discovery | Confirmed mismatches found | Post-pilot (requires FR-14) |
| User adoption | Active users, repeat queries | Post-pilot |

## 11. Delivery Plan

**Case study phases:** Discovery → Pilot → Validation → Scale.

**Build order (project sequence):** (1) `documents` table and configuration stub, (2) ingestion, (3) extraction, then chunking, embedding, retrieval, Q&A, UI.

| Window | Focus |
|---|---|
| Day 1 | Config and `documents` table; upload API with validation and registration; parsing; chunking; embeddings into ChromaDB; retrieval with page citations |
| Day 2 | LLM answer generation with grounding and refusal; basic entity extraction; Streamlit UI (upload, Q&A, export); benchmark check |
| After pilot | OCR, review workflow, revision comparison, inconsistency checks, access control, Docker |

## 12. Open Decisions

| # | Decision | Needed by |
|---|---|---|
| 1 | LLM (local model vs approved API) | Before Day 1 ends |
| 2 | Document parser | Before extraction starts |
| 3 | Confirm Tesseract and `bge-base-en-v1.5` | Before FR-5 / FR-7 |
| 4 | Pilot authentication approach (none vs simple) | Before UI work |
| 5 | Chunk size and overlap (validate on benchmark questions) | During chunking |

## 13. Assumptions and Constraints

- Pilot test data is a sample AUTOSAR architecture PDF; its fit to real HLDs is unverified (R-3).
- Single user, single project in the pilot.
- Python is the implementation language.
- No Docker until the end of the project.
- Outputs are advisory and require qualified engineer review before any compliance, design-approval, or release use. **FACT (case study governance principle).**

## 14. Definition of Done (Pilot)

1. A PDF can be uploaded, validated, versioned, and registered, and a document ID is returned.
2. The document is processed into chunks and indexed locally.
3. A question returns an answer with valid page citations, or an explicit refusal when evidence is missing.
4. The benchmark questions have been run and results recorded honestly, including failures.
5. Known limitations (tables, diagrams, OCR, representativeness) are documented.

## 15. Traceability to Source

| PRD section | Case study reference |
|---|---|
| §2 Problem | CS1 §1 Business Context |
| §3 Goals / Non-goals | CS1 §2 Objective, §3 Scope |
| §4 Users | CS1 §4 Users and Stakeholders |
| §6 Requirements | CS1 §6 Functional Capabilities, §7 Workflow |
| §8 Technology | CS1 §9 Technology Stack, plus project decisions |
| §9 Risks | CS1 §12 Risks and Controls, plus project risks |
| §10 Metrics | CS1 §11 Success Metrics |
| §11 Plan | CS1 §13 Implementation Approach |
