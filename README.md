# HR/Payroll Support Drafting & Optional Claude Integration
**Independent educational demo. No real clients, personal payroll data, or live Claude calls tested.**

Pure Python, source-grounded retrieval and citation IDs, abstention, synthetic sensitive-data patterns, human approval requirement, FastAPI route `POST /support/draft`. Contains an opt-in Claude Messages API adapter for *synthetic, non-sensitive* prompt text only. Local mode needs no API key or model access.

## Run
```bash
python -m pip install fastapi uvicorn pytest httpx
pytest -q
python support_agent.py
uvicorn support_agent:app --port 8103
```
Optional real Claude integration requires `ANTHROPIC_API_KEY`, a currently valid model ID, authorized network, and a separate call to `safe_claude_draft`. This was **not used or tested live** in this package. Do not send real employee names, payroll amounts, bank numbers, SSNs, or confidential case records. Synthetic pattern filtering is not a production DLP control.

## Evaluation and future work
Measure citation coverage, accuracy on reviewer-labeled cases, abstention correctness, human edit rate, sensitive input blocks, latency/cost (when live), and escalation outcomes. For real use, add SSO/RBAC, retention policies, formal DLP, incident response and approved vendor data processing agreements.

## Added Checkwriters fit demonstrations
Expanded with an offline allowlisted tool router, audit events, ticket handoffs, explicit human approval and deterministic agent-evaluation fixtures. Live Claude API was NOT tested and no autonomous GTM agent is deployed.
