---
name: reviewing-pull-requests
description: Reviews pull requests for correctness, test coverage, and risky changes. Use when the user asks to review a PR, check a diff, or prepare merge feedback.
---

# Reviewing Pull Requests

## Goal

What result should be produced.

Produce a concise, actionable PR review.

## Workflow

The necessary order and decision branches.

1. Get the diff.
2. Identify changed files and key functions.
3. Read relevant code and tests.
4. Check for missing error handling, hardcoded values, broken abstractions, or untested paths.
5. Write the review.

## Success criteria

Conditions that must be true before completion.

- Blocking issues come first.
- Each blocking issue has a file reference and suggested fix.
- Nits are separated from blocking issues.
- Empty diff is reported as no changes.

## Stop rules

When to stop, ask, retry, or hand back.

- Ask which base branch to compare if unclear.
- Do not approve deployment, security, or irreversible changes without confirmation.
- Mark unverified suspicions as suspicions, not confirmed bugs.

## Output Format

Only if output shape must be strict.

```markdown
## Summary
<2-3 bullet points>

## Blocking issues
- [file:line] <problem> -> <suggested fix>

## Nits
- <optional suggestions>
```

## Gotchas

Only if known pitfalls exist.

- Green CI does not prove the changed behavior is tested.
- Renames and formatting-only changes can hide logic changes.
- Generated files and lockfiles should not be reviewed line by line unless intentional.
