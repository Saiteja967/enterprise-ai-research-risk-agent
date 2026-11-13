# Interview walkthrough

## Open with the operational question

“A credit analyst sees a rising overdue balance. Which counterparties warrant a closer look, what changed, and which record supports the explanation?” Use ABC to walk from the portfolio chart to a ledger comparison, an open alert and a document passage. Describe this as an independent synthetic portfolio project. Give the interviewer the distinction between a measured software property and a business outcome.

## Draw the trust boundary

Draw three boxes for the analyst console, the graph and the evidence store. The console saves a report when the analyst requests it. The graph receives one validated company identifier and two named MCP tools. SQL is assembled by the application and binds identifiers as values. The research connection also enters read-only mode in the database. The model never gets a database credential, an arbitrary query tool, a filesystem tool or a way to decide approvals.

The stdio server is usable by a local MCP client. The application exercises the same registered tools over the SDK's in-memory transport. Separate network services would add authentication, retry, service discovery and operational cost. Here the interviewer can inspect the real protocol call without provisioning those services.

## Explain one decision with evidence

The first node groups transactions by reporting month, compares the two latest periods and reads open alerts. Retrieval filters by company before ranking up to three document chunks. Source IDs and page or row locators accompany the text. The analysis node selects evidence IDs and permitted follow-ups. Validation rebuilds finding text from stored evidence. Citations remain inspectable after the workspace changes because the run stores a snapshot.

Explain that extractive reporting trades linguistic flexibility for easy verification. A correctly quoted source can still be irrelevant or wrong. A “limited evidence” label describes gaps in this run. It is not a probability of default. When both tools fail the graph produces a failed report with no validated findings. When live inference fails it retains the source material for manual review.

## Show the human decision

Stage the sample CSV. Before approval the library still contains only the previously approved sources. An approval transaction claims a pending proposal, applies its effect and writes the audit row. A conflicting decision receives HTTP 409. Matching retries return the recorded outcome. The uniqueness constraint uses company and content digest to prevent duplicate indexing. Open an alert and request a reviewed status to show the same boundary on a second type of change.

## Defend the evaluation

Show the answer key before running the suite. Each case identifies expected findings and an expected document hit or an expected absence. The runner builds a fresh database and calls the same graph. The independent RAGAS run found all expected evidence and measured 66.7% context precision. Additional ledger and alert records can be valid for a company while exceeding the scope of a particular question. Explain macro recall, exact support, retrieval accuracy and nearest-rank P95. A seven-question fixed corpus tests regression. It gives little evidence about novel customers, ambiguous questions or difficult language. Exact support is deliberately easy for an extractive renderer. Discuss a blinded held-out set, conflict and recency cases, expert relevance labels and inter-rater agreement before offering a broader quality claim.

## Discuss the deployment decision

Start with one locally bound app and an unexposed database. The host is the identity boundary for this demonstration. For a customer pilot, establish the allowed datasets and decisions with the analyst first. Add enterprise identity and company-scoped authorization before a shared rollout. Split migration, research and mutation database roles, send durable events to a protected log, and isolate document processing. Use a queue for longer jobs and cancellation. Decide whether OCR and learned embeddings justify their cost using the target corpus.

Explain what was actually exercised locally using the verification table in the README. The transport-mocked adapter verifies parsing and token accounting. A separately authorized live-provider smoke run is still necessary to validate an account's access, selected model, latency and billable usage.
