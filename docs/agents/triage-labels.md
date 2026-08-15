# Triage labels

The five canonical triage roles, each mapped to the label string of the same
name (identity mapping). The `triage` skill hardcodes these defaults — this
file documents the convention; the skill is the executable source of truth.

| Role | Label |
|---|---|
| Needs triage | `needs-triage` |
| Needs info | `needs-info` |
| Ready for agent | `ready-for-agent` |
| Ready for human | `ready-for-human` |
| Won't fix | `wontfix` |

This repo also carries priority labels `P0` / `P1` / `P2` (introduced with the
2026-08-15 ultrareview epic). Triage roles and priority are orthogonal: a
triage role says who acts next, priority says how urgent the item is.
