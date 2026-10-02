AUTOMOTIVE ENGINEERING AI | PROJECT CASE STUDIES
Confidential | Reference Solution Document Page 4
# Case Study 1
# AUTOSAR HLD Document Analysis Assistant
Project Overview
Automate the extraction, organization, search, and validation of architectural knowledge from large AUTOSAR
High-Level Design documents.
### 1. Business Context
High-Level Design documents describe software components, interfaces, ports, signals, dependencies, functional
flows, and integration logic. They are often hundreds of pages long and maintained as unstructured PDFs.
Architects, developers, integrators, and testers must manually interpret this content. The lack of structured
extraction and search makes it difficult to identify mismatches, missing dependencies, inconsistent terminology,
and incomplete test coverage.
### 2. Project Objective
• Reduce manual effort required to review HLD documents.
• Create a structured and searchable repository of architecture knowledge.
• Improve component, interface, signal, and dependency traceability.
• Support design reviews, onboarding, impact analysis, and test planning.
### 3. Scope
In Scope Out of Scope
• PDF and supported document ingestion
• OCR for scanned pages
• Component, interface, port, signal, and flow extraction
• Natural language search with citations
• Document comparison and inconsistency reporting
• Export of structured findings
• Automatic approval of architecture decisions
• Modification of source HLD documents without review
• Replacement of formal architecture governance
### 4. Primary Users and Stakeholders
• System architects
• AUTOSAR architects
• Software developers
• Integration engineers
• Test engineers
• Engineering managers

---

AUTOMOTIVE ENGINEERING AI | PROJECT CASE STUDIES
Confidential | Reference Solution Document Page 5
### 5. Proposed Solution
The proposed solution is a secure AI-assisted application using a locally or privately hosted Large Language Model,
Retrieval-Augmented Generation, local vector storage, and a Python-based web application. The system supports
engineers with evidence-based recommendations while retaining human review and approval.
### 6. Functional Capabilities
• Document upload and controlled ingestion
• Section, table, and metadata extraction
• Architecture entity recognition
• Interface and dependency mapping
• Natural language question answering
• Cited summaries and component reports
• Revision comparison
• Potential mismatch and completeness checks
### 7. High-Level Workflow
1. Upload or select an approved HLD document.
2. Extract text, tables, headings, and metadata.
3. Chunk content by section and architecture context.
4. Create embeddings and save them in the local vector database.
5. Retrieve relevant sections for each user query.
6. Generate grounded responses with page or section citations.
7. Allow engineer review, correction, and export.
### 8. Inputs and Outputs
Inputs Expected Outputs
• AUTOSAR HLD documents
• Interface specifications
• Architecture descriptions
• Component catalogues
• Revision history
• Component and interface inventory
• Dependency maps
• Functional-flow summaries
• Searchable Q&A responses
• Potential inconsistency report
• Structured export for downstream use
### 9. Suggested Technology Stack
Layer Recommended Options Deployment Note
User interface Streamlit; Flask Web UI; optional enterprise portal 
Streamlit for pilot, enterprise UI
later
API and services FastAPI or Flask 
FastAPI preferred for modular
APIs
LLM 
Any approved LLM: Llama, Mistral, Qwen, DeepSeek,
Falcon, or equivalent
Local, on-premises, or private
environment

---

AUTOMOTIVE ENGINEERING AI | PROJECT CASE STUDIES
Confidential | Reference Solution Document Page 6
Layer Recommended Options Deployment Note
Embeddings BGE, E5, Sentence Transformers, or equivalent 
Evaluate with domain-specific
queries
Vector database 
FAISS or ChromaDB; Milvus or self-hosted Weaviate for
scale
Persistent local storage and
metadata filters
RAG orchestration LangChain, LlamaIndex, or custom Python pipeline 
Use controlled prompts and
citations
Structured storage PostgreSQL
Projects, users, reviews,
approvals, audit data
Deployment Docker; optional Kubernetes 
Network isolation and controlled
access
### 10. Expected Business Benefits
• Reduced document-review effort
• Faster architecture validation
• Improved knowledge reuse
• Better onboarding
• Enhanced traceability to testing, safety, and cybersecurity
### 11. Indicative Success Metrics
Metric Indicative Measurement
Document review effort Percentage reduction against baseline manual review time
Extraction quality Precision and recall for approved architecture entities
Answer groundedness Percentage of responses with valid source citations
User adoption Active users and repeat query volume
Issue discovery Number of confirmed mismatches or missing dependencies identified
### 12. Key Risks and Controls
Risk Recommended Control
Incorrect extraction from tables or
diagrams 
Use page-level citations and review queues
Hallucinated architecture relationships Restrict answers to retrieved evidence and show confidence
Unauthorized access to project documents Apply role-based access and project isolation
Outdated document versions Enforce document version labels and approved-source status

---

AUTOMOTIVE ENGINEERING AI | PROJECT CASE STUDIES
Confidential | Reference Solution Document Page 7
### 13. Implementation Approach
Phase Key Activities
1. Discovery Collect representative HLDs, define taxonomy, questions, and success metrics.
2. Pilot Build ingestion, local vector store, RAG search, Streamlit UI, and export.
3. Validation Benchmark extraction and Q&A with architects and testers.
4. Scale Add revision comparison, graph relationships, access control, and integrations.
Governance Principle
AI-generated content must be traceable to approved source material and reviewed by authorized engineering
specialists before it is used for compliance, design approval, software release, or vehicle validation.