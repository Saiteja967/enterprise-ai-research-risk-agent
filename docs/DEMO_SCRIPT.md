# Three-minute demo

Run the local setup in the README. Use the seeded workspace in demo mode. Keep `data/sample_upload.csv` ready for the file picker. All companies and amounts in this presentation are fictional.

| Time | On screen | What to say |
| --- | --- | --- |
| 0:00–0:25 | Overview → Receivables at risk | “The desk reviews six counterparties. At the June close, overdue receivables represent 11.9% of the portfolio. Select January to compare the two ends of the same ledger series.” |
| 0:25–0:55 | Investigation spotlight → Open research workspace → Run and save research | “ABC has an aging alert. I want to know what changed, which record supports it, and what a credit analyst could verify next. The demo selector is deterministic. Retrieval, SQL and the graph all run locally.” |
| 0:55–1:20 | Open an AL-1048 citation, then a DOC citation | “This amount comes from a ledger aggregation. This passage comes from the credit review. Each finding resolves to an immutable evidence snapshot. The two proposed follow-ups are for a person to consider.” |
| 1:20–1:45 | Inspect workflow | “These are the actual calls to the two read-only MCP tools. The model can select known evidence and review actions. Validation discards unknown IDs before we assemble the report.” |
| 1:45–2:25 | Knowledge base → choose ABC → submit sample CSV → Approval queue → Approve | “Submission extracts the rows for review. The source becomes searchable after my decision. Approving the same proposal twice cannot index the file twice.” Open the knowledge base to show the indexed source. |
| 2:25–2:50 | Evaluation → Run evaluation | “This executes seven labeled cases in a clean fixture database. We measure expected citations found, exact text support, document retrieval, wall-clock time and provider usage. The unchanged answer key makes runs comparable.” |
| 2:50–3:00 | Audit log | “The report, approval and evaluation each have a request ID. This illustrates where I would connect enterprise identity, telemetry and retention controls before a customer rollout.” |

If asked about missing evidence, select HBR in the research workspace and ask about invoice reconciliation. The report retains its ledger evidence and marks the missing document retrieval as a limitation.
