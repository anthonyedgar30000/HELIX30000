# HELIX conversation role cards

## Why this exists

A chat title describes what people see. It does not establish repository authority.

Every active HELIX conversation should carry a visible role prefix and a short role card that can be checked against live GitHub state. The machine-readable source is `.helix/conversation-role-registry.json`.

## Recommended workspace titles

| Current workspace label | Recommended title | Authority meaning |
|---|---|---|
| `HELIX Coordination Framework` | `[CONTROL] HELIX — Coordination & Reality` | Owns the HELIX30000 coordination registry; may inspect other repositories read-only and route reviews/handoffs. |
| `ServiceTracer Azure Operations` | `[OWNER] ServiceTracer — PR #27 Rollback Design` | Sole write owner of `azure-iac-msp-lab` branch `design/collector-rollback-snapshot-recreation`. |
| `HELIX Protocol Kernel` | `[OWNER] HELIX — Protocol Kernel & Interoperability` | Sole write owner of `helix-protocol-kernel` branch `feature/edge-envelope-v0.3`. |
| `ContextOS vs HELIX` | `[UNRESOLVED] ContextOS — PR #13 Query Bridge` | PR #13 exists, but no repository-native active-work owner has been established. Read-only until a handoff is recorded. |
| `Modern Agent Protocols` | `[ARCHIVE] HELIX — Modern Agent Protocols` | Prior owner context; ownership was handed to the Protocol Kernel and Agent Interoperability conversation. |
| `Message Adapter Structure` | `[DESIGN] HELIX — Message Adapter Structure` | Design reference only until a new bounded branch and owner are declared. |
| `Front end improvements` | `[BACKLOG] HELIX — Front-End Improvements` | Unassigned backlog; no repository or branch authority. |
| `Yellow text warning meaning` | `[REFERENCE] ChatGPT UI — Warning Meaning` | UI reference; no HELIX project authority. |

These are prescribed titles. This repository cannot rename ChatGPT conversations automatically.

## Role-card template

Place this at the beginning of an active conversation or keep it in the first pinned project note:

```text
Role ID: <stable registry role_id>
Visible title: <desired title>
Role type: OWNER | REVIEW | CONTROL | UNRESOLVED | DESIGN | BACKLOG | ARCHIVE | REFERENCE
Repository: <owner/repository or none>
Owned branch: <branch or none>
Target PR: <number or none>
Permitted actions: <bounded actions>
Prohibited actions: <explicit boundaries>
Authority evidence: <GitHub ref and observation date>
Freshness rule: re-resolve repository, branch, PR head, CI, and .project state before acting
```

## Operating rules

1. Resolve the exact `owner/repository` before looking up project state.
2. Read the active branch's `.project/` state before proposing or changing work.
3. Treat only `confirmed` roles as write owners.
4. A reviewer may comment, approve, reject, or hand off; a reviewer does not patch the reviewed branch.
5. `UNRESOLVED`, `DESIGN`, `BACKLOG`, `ARCHIVE`, and `REFERENCE` conversations are read-only until a repository-native ownership transition is recorded.
6. A green CI result proves only the tested commit. It does not prove review approval, deployment, rollback recoverability, or operational health.
7. Moving or renaming a chat does not transfer branch ownership.
8. GitHub and `.project/` state outrank this registry when they are newer or conflict.

## Lifecycle language

Use these states precisely:

- **Proposed:** discussed but not committed.
- **Implemented:** present on a branch.
- **CI-verified:** tests passed on the exact cited head.
- **Merged:** incorporated into the target branch.
- **Deployed:** applied to a runtime environment with current evidence.
- **Manually repaired:** runtime diverged from automation and required manual correction.
- **Operationally verified:** the intended runtime behavior was observed after deployment or repair.

Never compress these into the word “done.”
