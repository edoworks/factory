---
name: issue-tracking
description: Track non-trivial Factory work in edoworks/factory issues and verify closeout without replacing repository evidence.
---

# Factory Issue Tracking

Use one `edoworks/factory` issue per bounded work chunk. Issue writes require
explicit authority and the authorized GitHub identity; `--auto` is not human
authorization.

1. Freeze a complete issue body and intent with `scripts/issue-intent.mjs`.
2. Validate the intent before any separately authorized GitHub write.
3. Keep implementation evidence and issue state independently verifiable.
4. Close only after implementation and verification pass.
5. Run `{env:FACTORY_DEV_NODE} {env:FACTORY_DEV_OPENCODE_ROOT}/scripts/issue-closeout.mjs verify --repo edoworks/factory --issues N`
   and require `CLOSED` before claiming tracked completion.

Never use inline multiline mutation bodies, bypass identity checks, or treat an
issue as the replacement for canonical repository evidence.
