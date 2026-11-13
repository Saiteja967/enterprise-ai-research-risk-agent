# Verification record

The portfolio repository contains the four planned milestones. The default user journey runs without keys, containers or network access after installation. CI is configured for a fresh Linux checkout.

| Verification | Result on the development host |
| --- | --- |
| Python suite | 17 tests passed with a temporary PostgreSQL instance available. The PostgreSQL case explicitly skips when its disposable URL is absent. |
| Database | Alembic upgrade, idempotent seed, scoped vector retrieval, report persistence and approved ingestion exercised. PostgreSQL 16.2 with pgvector 0.6.2 and SQLite were tested. |
| Browser | Two Playwright journeys passed using installed Chrome. Desktop covered report → source → workflow → upload → approval → evaluation → audit. Mobile covered navigation, dark mode and viewport overflow. |
| Static checks | Ruff lint/format, mypy, pip dependency check, frontend ESLint, Prettier, TypeScript and Vite production build passed. |
| Evaluations | Seven synthetic cases. Raw evidence IDs and timings are in [evaluation-baseline.json](evaluation-baseline.json). The independent [RAGAS run](ragas-baseline.json) found 100% context recall and 66.7% macro context precision. |
| Permissions and data | Browser-origin checks, bounded input, staging isolation, database read-only tool scope, conflict/retry handling and atomic commit/audit reviewed. Runtime caches, local databases, environment files and other workspace materials are excluded from the Git repository. |
| Live OpenAI | Adapter verified through a mocked HTTP transport using the actual SDK and LangChain path. Provider error handling and invalid citations tested. No paid call was made. |
| Containers and hosting | Compose and GitHub Actions definitions parsed locally. Docker was unavailable on this host. A container build, hosted Actions run and public deployment have not been observed. |

## External verification

1. On a Docker host, follow the README’s Compose instructions, run `docker compose ps`, then open the console and generate a report. This verifies image build, service health checks, database connectivity and asset serving on that host.
2. To validate a paid account, set the live environment values, restart, run one research brief and inspect its model, token usage and trace. Model access and prices depend on the selected account.
3. When ready to publish, inspect `git status` and `git remote -v` in this repository, select the intended GitHub owner, repository name and visibility, then push the local `main` branch. A hosted Actions run will exercise the repository's Linux and container jobs.

The project has no configured remote or deployed cloud resources at the time of this record.
