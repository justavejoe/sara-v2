# SARA Feature Development Roadmap & Priority
_Last Updated: 2025-07-23_

This document outlines the phased development plan for the SARA platform. It serves as the single source of truth for feature prioritization.

---

### Phase 1: Knowledge Hub MVP (In Progress)
**Goal:** Perfect the core functionality of ingesting and searching documents.

| Priority | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **1** | **Google Cloud Storage (GCS) Vault** | 📝 **To Do** | Replace the local folder ingestion with a scalable GCS bucket. |
| **2** | **Source Document Linking** | 📝 **To Do** | Implement citations that link answers back to the source file in GCS. |
| - | Basic Search & Retrieval | ✅ **Done** | Core functionality is operational. |
| - | Local Ingestion Workflow | ✅ **Done** | Proof of concept complete; to be replaced by GCS workflow. |

---

### Phase 2: The Analytical Partner (Next Up)
**Goal:** Make SARA more intelligent and secure by enabling it to analyze structured data and manage users.

| Priority | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **1** | **User Authentication & Roles (RBAC)** | 📝 **To Do** | A critical prerequisite for all advanced features. |
| **2** | **Text-to-SQL Agent** | 📝 **To Do** | Allow SARA to query its own structured SQL data. |
| **3** | **Personalization (Personalities & Lenses)**| 📝 **To Do** | Allow users to customize SARA's response style and analytical focus. |

---

### Phase 3: The Collaboration Hub (Future)
**Goal:** Transform SARA into an active platform for managing AI-powered workflows.

| Priority | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **1** | **"Prompt Studio" UI/UX** | 📝 **To Do** | The core interface for asynchronous prompt collaboration. |
| **2** | **AI Orchestration Service** | 📝 **To Do** | Backend service to call external AI models securely. |
| **3** | **"Curation View" for Synthesis** | 📝 **To Do** | The three-panel UI for synthesizing a final response. |

---

### Phase 4: The Engineering Co-pilot (Advanced Future)
**Goal:** Integrate SARA directly into the engineering toolchain (SolidWorks, ANSYS, etc.).

| Priority | Feature | Status | Notes |
| :--- | :--- | :--- | :--- |
| **1** | **CAE/CAD Agent (Parameterizer & Runner)**| 📝 **To Do** | Run pre-defined simulation scripts with user parameters. |
| **2** | **CAE/CAD Agent (Results Parser)** | 📝 **To Do** | Ingest and store simulation results in the SQL database. |
| **3** | **CAE/CAD Agent (AI Analyst & Optimizer)** | 📝 **To Do** | Use AI to analyze results and suggest new design parameters. |