# Cost-Aware Model Routing

## Operating rule while ollama-cloud quota >= 90% (2026-09-14 owner direction)

1. Routine work uses `small`/`explore` on local `granite4.1:3b`.
2. Bounded standard work uses `general`/`plan`/`build` on OpenAI `gpt-5.6-luna`.
3. Interactive ollama-cloud is reserved for materially necessary long-context or
   vision work. `ollama-cloud/glm-5.3-flash` remains the proven routine startup
   fallback, but routine cloud fallback remains disabled by policy.
4. The local standard-tier `ollama/qwen3.5:9b` attempt remains closed after a
   harness-level stall; retry requires repairing that harness first.

- Do not launch a model for commit creation, command execution, formatting, or
  deterministic state edits.
- Routine-class requests are refused on standard and complex routes.
- Use `trust-review` only for a material trust boundary and `frontier-build`
  only after standard construction fails explicit criteria.
- `vision` uses local `ollama/qwen3.5:4b` with
  `ollama-cloud/gemma4:31b` fallback only for screenshot assertions.
- Use at most one construction and one independent review subagent normally.
- Provider limits are request outcomes, not authority for retries or fallback.
- New routes require benchmark evidence; complex and trust-boundary promotion
  also require owner approval. `approved.json` is the route registry.
- Follow the repository-owned `model-routing` skill; do not hand-edit live
  routes or alter provider budgets to bypass a failed readiness check.
