# SKILL.md Authoring Specification

## Frontmatter

### name

- Gerund structure.
- Lowercase letters, numbers, hyphens only.
- Max 64 characters.
- No XML tags.
- No reserved words `anthropic` or `claude`.

### description

Baseline: `Does X and Y. Use when Z.`

- `description = capability boundary + trigger condition`.
- X, Y: what the skill covers, and what it excludes (out-of-scope uses).
- Z: what scenarios or symptoms should trigger it.
- Check: first sentence = capability boundary, last = trigger; no step-by-step narration.
- Third person.
- Max 1024 characters.

## Body

Minimal core:

- Goal
- Workflow
- Success criteria
- Stop rules

Optional:

- Context / Input
- Constraints
- Output Format
- Verification
- Gotchas

## Directory structure

```text
skill-name/
├── SKILL.md
├── README.md
├── references/
├── templates/
└── examples/
```

## Rules

- Keep SKILL.md concise.
- Use forward slashes.
- Link only files that exist.
- Avoid deep reference chains.
- Avoid Windows paths.
- Avoid redundant rules.
