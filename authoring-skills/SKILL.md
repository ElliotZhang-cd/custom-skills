---
name: authoring-skills
description: Creates, reviews, and fixes portable Agent Skills (SKILL.md packages). Use when writing a new skill, revising an existing one, or validating a skill before sharing.
---

# Authoring Skills

## Goal

Produce or improve a portable Agent Skill that an agent can discover, load, and
use to perform a recurring task more reliably than without it.

## Workflow

The necessary order and decision branches.

1. Clarify the task, target runtime, and expected output.
2. Decide whether a skill is warranted.
3. **Write the body first**: Goal, Workflow, Success criteria, Stop rules. This
   is where the scope actually gets decided.
4. **Compress the scope back into `description`** — after the body exists, never
   before:
   - one sentence of capability: the class of work and the artifact;
   - one sentence of trigger: 2-3 representative signals;
   - budget: 2 sentences, 200 chars target / 280 hard fail.
   - Anything cut here belongs in the body, not deleted.
5. Write `name`: gerund, lowercase letters/numbers/hyphens, <= 64 chars.
6. Add optional sections and supporting files only when needed.
7. Run `scripts/check-skill.py` and clear every error.

## Success criteria

Conditions that must be true before completion.

- `name` is valid.
- `description` is <= 2 sentences, <= 200 chars, capability first then trigger,
  with no feature inventory, no exclusions, and no workflow narration.
- Body contains Goal, Workflow, Success criteria, and Stop rules.
- Optional sections are added only when needed.
- All linked files exist and use forward slashes.
- `scripts/check-skill.py` exits 0.
- The skill is as concise as possible while still being useful.

## Stop rules

When to stop, ask, retry, or hand back.

- Stop and ask when scope, runtime, or expected output is unclear.
- Recommend against creating a skill when it is not reusable.
- Do not include destructive actions or credentials without confirmation.
- Do not claim a skill is proven without evidence.
- Do not "fix" an over-budget description by trimming words out of the same
  inventory. Move the inventory to the body and rewrite the capability as a
  class — otherwise the next edit grows it back.

## Constraints

- `description` is context cost on every turn for every installed skill. Treat
  it as an ad slot, not a place to be thorough.
- Exclusions ("not for PDFs") belong in the body, not the description: they are
  only useful after the decision to load.
- The 1024-character platform limit is a legality ceiling, never a target.

## Optional sections

Add only when needed.

- `Context / Input` when inputs or preconditions are non-obvious.
- `Constraints` when safety, permissions, or scope boundaries matter.
- `Output Format` when output shape must be strict.
- `Verification` when self-checking is important.
- `Gotchas` when known pitfalls exist.

## Verification

```bash
python scripts/check-skill.py <skill-dir>      # Windows
python3 scripts/check-skill.py <skill-dir>     # WSL
```

Exit 0 is required. Warnings are read and either fixed or justified in the body.

## References

- [authoring-spec.md](references/authoring-spec.md) — format, description budget, naming, structure, anti-patterns.
- [prompt-engineering.md](references/prompt-engineering.md) — result-oriented writing, budgets, tool routing, stop rules, verification.

## Templates

- [new-skill.SKILL.md](templates/new-skill.SKILL.md) — a ready-to-fill skill template.

## Examples

- [example-skill.md](examples/example-skill.md) — a complete example skill.
