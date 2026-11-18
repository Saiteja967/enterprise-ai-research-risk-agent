# Verification record

The portfolio repository contains the four planned milestones. The default user journey runs without keys, containers or network access after installation. CI passed in a fresh Linux checkout on November 18, 2026.

| Verification | Result on the development host |
| --- | --- |
| Python suite | 17 tests passed with a temporary PostgreSQL instance available. The PostgreSQL case explicitly skips when its disposable URL is absent. |
| Database | Alembic upgrade, idempotent seed, scoped vector retrieval, report persistence and approved ingestion exercised. PostgreSQL 16.2 with pgvector 0.6.2 and SQLite were tested. |
| Browser | Two Playwright journeys passed using installed Chrome. Desktop covered report → source → workflow → upload → approval → evaluation → audit. Mobile covered navigation, dark mode and viewport overflow. |
| Static checks | Ruff lint/format, mypy, pip dependency check, frontend ESLint, Prettier, TypeScript and Vite production build passed. |
| Evaluations | Seven synthetic cases. Raw evidence IDs and timings are in [evaluation-baseline.json](evaluation-baseline.json). The independent [RAGAS run](ragas-baseline.json) found 100% context recall and 66.7% macro context precision. |
| Permissions and data | Browser-origin checks, bounded input, staging isolation, database read-only tool scope, conflict/retry handling and atomic commit/audit reviewed. Runtime caches, local databases, environment files and other workspace materials are excluded from the Git repository. |
| Live OpenAI | Adapter verified through a mocked HTTP transport using the actual SDK and LangChain path. Provider error handling and invalid citations tested. No paid call was made. |
| Containers and hosting | [Hosted Actions run 44368014843](https://github.com/Saiteja967/enterprise-ai-research-risk-agent/actions/runs/44368014843) passed all three jobs: backend (PostgreSQL 17/pgvector), browser, and Compose build/startup/health. The [public portfolio case study](https://saiteja-meridian-portfolio.keenaspen8192.chatgpt.site) is deployed; the analyst application is a local single-user demo. |

## Publication and remaining validation

The public repository is [Saiteja967/enterprise-ai-research-risk-agent](https://github.com/Saiteja967/enterprise-ai-research-risk-agent), pinned on the owner's profile. The static portfolio case study links to its source and recorded evaluations. LinkedIn features the source and case study, and lists Meridian as an independent personal project.

To validate a paid account, set the live environment values, restart, run one research brief and inspect its model, token usage and trace. Model access and prices depend on the selected account. A shared deployment of the analyst application still needs identity, per-company authorization and protected audit storage.
