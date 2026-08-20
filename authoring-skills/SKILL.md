---
name: authoring-skills
description: Creates, reviews, and iterates on portable Agent Skills (SKILL.md packages) that follow open SKILL.md / AgentSkills conventions. Use when the user asks to write a new skill, improve an existing SKILL.md, review or refactor a skill, turn documentation or repetitive work into a skill, or validate a skill before sharing.
---

# Authoring Skills

## Goal

What result should be produced.

Produce or improve a portable Agent Skill that an agent can discover, load, and use to perform a recurring task more reliably than without it.

## Workflow

The necessary order and decision branches.

1. Clarify the task, target runtime, and expected output.
2. Decide whether a skill is warranted.
3. Write frontmatter:
   - `name`: gerund structure, lowercase letters/numbers/hyphens, <= 64 characters, no XML, no reserved words.
   - `description`: capability boundary + trigger condition. State what the skill covers and when to use it. Do not summarize the workflow.
4. Write the body with the minimal core:
   - Goal
   - Workflow
   - Success criteria
   - Stop rules
5. Add optional sections only when needed.
6. Add supporting files only when needed.
7. Review against Success criteria.

## Success criteria

Conditions that must be true before completion.

- `name` is valid.
- `description` is capability boundary + trigger condition, not a workflow summary.
- Body contains Goal, Workflow, Success criteria, and Stop rules.
- Optional sections are added only when needed.
- All linked files exist.
- Paths use forward slashes.
- The skill is as concise as possible while still being useful.

## Stop rules

When to stop, ask, retry, or hand back.

- Stop and ask when scope, runtime, or expected output is unclear.
- Recommend against creating a skill when it is not reusable.
- Do not include destructive actions or credentials without confirmation.
- Do not claim a skill is proven without evidence.

## Optional sections

Add only when needed.

- `Context / Input` when inputs or preconditions are non-obvious.
- `Constraints` when safety, permissions, or scope boundaries matter.
- `Output Format` when output shape must be strict.
- `Verification` when self-checking is important.
- `Gotchas` when known pitfalls exist.

## References

- [authoring-spec.md](references/authoring-spec.md) — format, frontmatter, naming, structure, anti-patterns.
- [prompt-engineering.md](references/prompt-engineering.md) — result-oriented writing, tool routing, stop rules, verification, simplification.

## Templates

- [new-skill.SKILL.md](templates/new-skill.SKILL.md) — a ready-to-fill skill template.

## Examples

- [example-skill.md](examples/example-skill.md) — a complete example skill.
