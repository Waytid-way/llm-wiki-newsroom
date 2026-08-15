# Domain Docs

How the engineering skills consume this repo's domain documentation when exploring the codebase.

This repo is single-context and does **not** currently ship `CONTEXT.md` / `CONTEXT-MAP.md` /
`docs/adr/` — its architecture SoT is `CLAUDE.md` + `.claude/`. Per the scaffold rules,
proceed silently when those files are absent: do not flag their absence or create them
upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and
`/improve-codebase-architecture`) creates `CONTEXT.md` / `docs/adr/` lazily when terms or
decisions actually get resolved — at that point this file's structure guidance applies:

- `CONTEXT.md` at the repo root (or `CONTEXT-MAP.md` pointing at one per context)
- `docs/adr/` — read ADRs that touch the area you're about to work in

Single-context layout (most repos):

```
/
├── CONTEXT.md
├── docs/adr/
│   └── 0001-...
└── src/
```

Multi-context layout (presence of `CONTEXT-MAP.md` at the root): one `CONTEXT.md` per
context, ADRs under each context's `docs/adr/`.
