# DataDialogue — Seamless Self-Service Data Intelligence

> **NatWest Hackathon Finalist** · Talk to Data · Multi-Agent AI Platform

![Dashboard Overview](IMAGES/Screenshot%202026-04-19%20at%2021.44.25.png)

---

## i. Overview

**DataDialogue** is an advanced, self-service data intelligence platform that converts natural language questions into complex analytical queries. It solves the critical bottleneck wherein business users must wait days for data analysts to write SQL or configure dashboards to answer simple reporting questions. Intended for enterprise business users, managers, and executives, the platform allows anyone to upload messy CSV datasets or unstructured PDF reports and instantly "talk to their data" to receive factual answers backed by interactive charts.

## ii. Features

The following features are **fully implemented and working** in the provided codebase:
- **Secure Authentication:** Complete JWT-based registration and login system ensuring tenant data isolation via Row-Level Security.
- **Multi-Modal Data Ingestion:** 
  - CSV files are uploaded, parsed asynchronously via Celery, and converted to in-memory DuckDB tables.
  - PDF files are uploaded, chunked, vectorized using Sentence Transformers, and stored in a PGVector database.
- **Intelligent Intent Classification:** Natural language questions are automatically routed to the correct agent (Structured SQL vs Unstructured RAG).
- **LangGraph Agentic Pipeline:** True multi-agent cyclic reasoning that writes SQL, verifies syntax against a sandbox, and handles exceptions dynamically without hallucinating.
- **Dynamic Visualizations:** An AI Synthesizer reads raw statistical outputs and dynamically constructs React Rechart specifications (Bar, Line, Pie) rendered instantly on the frontend.
- **Data Lineage Citations:** Every answer provides exact source transparency, showing the rows or file paths that contributed to the generated response.
- **Enterprise Audit Logging:** A fully functioning audit trail that tracks user queries, LLM token consumption, latency, and matched intents.

---

## iii. Install and Run Instructions

The platform is fully containerized, requiring minimal setup. Follow these steps to build and run the application locally.

### Prerequisites
- **Docker Desktop** installed and running on your device.
- **Git** to clone the repository.
- An **Anthropic API Key** (required for the LangGraph AI pipeline).

### Initializing the System

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-org/datadialogue.git
   cd datadialogue
   ```

2. **Configure Environment Variables:**
   Copy the provided example file to create your local `.env`.
   ```bash
   cp .env.example .env
   ```
   Open `.env` and assign your Anthropic Key. Without this, the AI will throw safe exceptions:
   ```properties
   ANTHROPIC_API_KEY=sk-ant-api03...
   ```

3. **Build and Run the Containers:**
   Start the isolated multi-container architecture. This downloads all dependencies (`requirements.txt` and `package.json`) and starts the system.
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
   ```
   *(Note: This may take a few minutes as it compiles Python libraries).*

4. **Initialize the Database:**
   Once the containers are running (`Up`), execute the Alembic schemas and seed the initial dictionary definitions. Run these sequentially in your terminal:
   ```bash
   docker compose run --rm -e PYTHONPATH=/app backend alembic upgrade head
   docker compose run --rm -e PYTHONPATH=/app backend python -m app.scripts.seed_metrics
   ```

The platform is now successfully running in the background!

---

## iv. Tech Stack

- **Programming Languages:** Python 3.11, TypeScript, SQL
- **Frontend Framework:** React 18, Vite, Zustand, TailwindCSS, Recharts
- **Backend Framework:** FastAPI, SQLAlchemy, Alembic
- **Databases:** PostgreSQL (Relational), Redis (Caching/Broker)
- **Object Storage:** MinIO (S3-compatible blob storage)
- **Analytical & Search Engines:** DuckDB (In-memory SQL), `pgvector` (HNSW Nearest-Neighbor clustering)
- **Async Workers:** Celery
- **AI/ML Libraries:** LangGraph, LangChain, Anthropic API (Claude 3.5), `sentence-transformers` (Local embedding models)

---

## v. Usage Examples and User Journey

Below is the step-by-step user journey, showcasing exactly how to leverage DataDialogue to extract business value.

### 1. Secure Authentication & Portals
First, access the platform at `http://localhost:5173`. You will be met with a secure authentication layer, ensuring all your data objects are sandboxed to your localized tenant profile. 

![Secure Login & Authentication](IMAGES/Screenshot%202026-04-19%20at%2021.43.09.png)

### 2. High-Level Dashboard
Once authenticated, the dashboard centralizes your workflows. Here you can track all the datasets uploaded by your organization and view their processing statuses. 

![Dashboard View](IMAGES/Screenshot%202026-04-19%20at%2021.44.25.png)

### 3. Asynchronous Data Uploading
Upload raw, messy CSV data or unstructured PDF reports via the central dropzone. Behind the scenes, Celery asynchronous workers are piping this data directly into MinIO storage. 

![Data Upload & Celery Tasks](IMAGES/Screenshot%202026-04-19%20at%2021.44.35.png)

### 4. Vectorization & Readiness Tracking
As chunks are processed by Sentence Transformers and shipped to `pgvector` (for PDFs) or indexed in-memory (for CSVs), the progress is accurately tracked via live state-updates. 

![Ready State Validation](IMAGES/Screenshot%202026-04-19%20at%2021.45.04.png)

### 5. Conversational AI Query Interface
Enter the primary query chat interface and dictate your logic in plain English. No SQL or complicated parameters are necessary. For example:
> *"Show me a timeline of revenue vs expenses, and explain any distinct drops."*

![AI Query Interface](IMAGES/Screenshot%202026-04-19%20at%2021.45.54.png)

### 6. Interactive Visualizations & Analytics
Our multi-agent pipeline writes, verifies, and executes analytical queries instantly. It returns a dynamic, interactive `Recharts` graph along with a deeply analytical business narrative, accompanied by distinct source citations to prove where the numbers came from.

![Rich Output and Visualizations](IMAGES/Screenshot%202026-04-19%20at%2021.46.26.png)

### 7. Transparent Audit Logs
For enterprise compliance, the system records everything. Users and administrators can inspect the exact LLM tokens consumed, execution latencies, and AI-intent pathways via the Audit Log.

![Logging and Auditing](IMAGES/Screenshot%202026-04-19%20at%2021.47.18.png)

---

## vi. Architecture & Additional Notes

### System Architecture Breakdown

Our platform orchestrates 6 independent microservices using Docker Compose:
1. **Nginx Reverse Proxy:** Routes `/api` traffic to FastAPI and root traffic to the Vite React Dev Server.
2. **FastAPI Backend:** Handles stateless API requests and streams logic via LangChain graph pathways.
3. **Celery Worker & Redis:** Decouples expensive file-processing constraints (chunking PDFs, extracting CSV schemas) from the main API thread.
4. **Persistent Data Tier:** State is dispersed cleanly—binaries live in **MinIO**, structured application state & vectors live in **PostgreSQL**.

### Highlighting Technical Depth

**Why LangGraph over standard prompt chains?**
Instead of using rudimentary, single-shot LLM queries (which are notoriously brittle for SQL generation), we deployed a cyclic state machine utilizing **LangGraph**. The system utilizes a "Verifier Agent" that executes AI-generated SQL inside an isolated DuckDB sandbox. If the syntax fails or requests non-existent columns, the Verifier catches the Postgres exception, parses the exact SQL error, and passes it *back* to the SQL Agent to self-correct. This guarantees syntactically perfect analytical execution and prevents the LLM hallucinations commonly found in generic prompt-workflows.

**Why PGVector and HNSW?**
We use a fine-tuned open-source local clustering model (`sentence-transformers`) to slice PDF strings into dense vectors. We inserted these vectors into Postgres using the `hnsw` (Hierarchical Navigable Small World) index rather than `ivfflat`. This drastically improves semantic retrieval search latency when hunting for documents because it utilizes high-dimensional graph traversal over flattened list clustering.

### Limitations
- The system heavily relies on Anthropic's model constraints. Excessively large or nested CSV files with hundred-plus columns will occasionally exceed the metadata token context windows unless properly sanitized by the user.
- Security parsing for the sandbox SQL runner is currently in an MVP state and expects non-malicious user inputs; production use would require rigorous parameterized queries.

### Future Improvements
Given more time, we would implement:
1. Support for real-time external database connections (Snowflake, BigQuery).
2. Saved Dashboards, where users could "pin" LangGraph generated charts to a real-time updating live homepage.
3. Expanded File ingestion formats to specifically handle complex nested JSON outputs.

---
**Built for the NatWest Hackathon** · *Talk to Data Team*
