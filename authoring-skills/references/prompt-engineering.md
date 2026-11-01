# Prompt Engineering for Skills

## Core principle

Define the result, important constraints, available evidence, and completion criteria. Leave the model space to choose the efficient path.

## Simplify

Remove:

- Duplicated rules.
- Examples that do not change behavior.
- Irrelevant tools.
- Process instructions for things the model already does.

Keep:

- User-visible result.
- Success criteria.
- Constraints.
- Tool routing rules.
- Output format and verification.

## Result-oriented writing

Describe the destination, not a route map.

Use absolute rules only for true invariants. Use decision rules for judgment calls.

## Budgets beat adjectives

"Concise" is not a constraint; it is a preference, and preferences lose to
completeness pressure. Any text with a stated ceiling will drift toward that
ceiling, so a ceiling is a target, not a limit.

State budgets as numbers with two thresholds — a target and a hard fail — and
give a mechanical check that reads them. `Check: no step narration` cannot fail
on its own; `> 280 chars = fail` can.

When a budget applies, put it where the text is written (frontmatter guidance,
template comment) *and* in the checker. One copy will be missed.

## Stop rules

Define when to stop, ask, retry, or hand back.

## Tool routing

Expose only relevant tools. Describe what, when, important returns, and errors.

In portable skills, write abstract actions in the body and put concrete tool mappings in the environment or references.

## Verification

For quality-critical tasks, define how to verify before completion.

## Form matches failure

| Failure | Correct form |
| --- | --- |
| Violates rule under pressure | Prohibition + rationalization table + red flags |
| Wrong output shape | Positive recipe / Output Format |
| Missing required elements | REQUIRED fields or slots |
| Behavior depends on condition | Conditional sentences |
| Output grows until it is unusable | Numeric budget + target/hard-fail split + checker |
| Covers "everything just in case" | One compressed example next to the bloated original |
| Rule ignored because the failure mode was mis-named | Ban the observed failure verbatim (`Triggers include:`), not a proxy (`step-by-step narration`) |
