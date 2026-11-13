# Implementation plan

| Milestone | Acceptance criteria |
| --- | --- |
| 1. Research vertical slice | Bootstrap synthetic counterparties and transactions. Open a React screen, submit a question, and receive a validated LangGraph report with inspectable source IDs. Run an integration check and build the UI. |
| 2. Evidence and controls | Retrieve company-scoped chunks through read-only MCP; stage PDF/CSV ingestion and alert changes for explicit approval. Exercise invalid input, degraded providers, empty evidence and repeated decisions. |
| 3. Analyst console | Connect overview, research, investigations, knowledge base, workflow trace, evaluations, approvals and audit to the same API. Verify responsive layout and main browser journey. |
| 4. Reproducible release | Run fixtures, publish measured results, lint, type check, build and test. Package loopback-only Compose with PostgreSQL/pgvector and CI. Record exact limitations, demo script and interview walkthrough. |

