# CXBridge — synthetic hybrid support orchestration
Independent portfolio prototype, not Coinbase software or commercial deployment.

Python/FastAPI/LangGraph routes synthetic customer messages to deterministic internal handlers, an offline vendor stub, or human review. Only an allowlisted intent crosses the vendor boundary. Conversation state persists in SQLite or PostgreSQL using optimistic version checks. Human resolution requires a separate tenant reviewer key. No actual account actions or financial advice.

## Run offline
Install requirements.txt and run python -m pytest -q and python evaluate.py. Set distinct random CXBRIDGE_KEY_A, CXBRIDGE_REVIEWER_A (and optionally B equivalents), then uvicorn api:app --host 127.0.0.1. Use POST /sessions/demo/turn with x-api-key and JSON {"message":"fraud"}; resolve via POST /sessions/demo/resolve with additional x-reviewer-key and {"resolved":true}. Synthetic messages only; raw history is stored locally. Do not expose publicly.

## Verification
CI installs LangGraph and starts PostgreSQL. No provider secrets needed. Evaluation is rule-aligned, not independent accuracy. See evidence.txt for local results; CI and real provider results remain pending.

## Optional live smoke
Skip unless free-tier eligibility is confirmed and billing disabled. Set GEMINI_API_KEY and CXBRIDGE_FREE_TIER_CONFIRMED=yes locally. Run python -c "from provider import gemini; print(gemini({'intent':'general'}))". No automatic retries or calls from CI/API. Never commit keys. This verifies only the adapter, not live end-to-end orchestration.

## Design tradeoffs
Deterministic classification is limited to keywords and simple follow-ups. Vendor stub returns an internal handoff; real adapter is separate. Persistent application state is not native LangGraph checkpointing. Optimistic concurrency rejects stale writes but does not prevent duplicate external calls. Tenant keys are not individual identities; no production compliance, cloud deployment, distributed load, or independent factuality claims. Human review blocks further turns until resolution. Future production needs identity, retention controls, encryption, idempotency and independent evaluation.
