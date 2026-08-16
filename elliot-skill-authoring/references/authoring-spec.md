# SKILL.md Authoring Specification

## Frontmatter

### name

- Gerund structure.
- Lowercase letters, numbers, hyphens only.
- Max 64 characters.
- No XML tags.
- No reserved words `anthropic` or `claude`.

### description

- `description = capability boundary + trigger condition`.
- What: what tasks this skill covers.
- When: what scenarios or symptoms should trigger it.
- Do not summarize the workflow.
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
