# HELIX — Data, Evidence, and Persistence Charter v0.1

## Status

This document is a coordination charter, not an implemented database design.

It registers the intended authority boundary and entry gates for a future dedicated HELIX persistence repository. It does not create that repository, select a database product as a foregone conclusion, define deployable migrations, import the legacy `HelixMemoryService`, or authorize runtime and cloud changes.

## Mission

Preserve HELIX canonical state, original evidence, provenance, authority history, lifecycle history, and recovery information so that important claims and transitions remain explainable, reproducible, auditable, and recoverable.

The persistence layer may preserve and reject state, but it does not invent governance authority.

```text
vector_match != verified_evidence
retrieved_memory != canonical_state
database_row != valid_state_transition
stored_artifact != trusted_artifact
successful_write != authorized_write
derived_index != source_of_truth
authentication != mutation_authority
record_existence != record_validity
current_state != complete_history
```

## 1. Authoritative entities and relationships

The first implementation repository must begin by defining stable identities and explicit relationships for:

- claims;
- evidence records and immutable evidence artifacts;
- hypotheses and investigations;
- decisions, approvals, reviewers, and review dispositions;
- actors, capabilities, authority grants, delegations, and revocations;
- requested, accepted, rejected, and executed actions;
- outcomes and outcome validation;
- lifecycle events, invalidations, expiries, withdrawals, and supersessions;
- provenance, manifests, content hashes, classifications, and artifact references.

Relationships must preserve how evidence supports or contradicts claims, how claims contribute to decisions, which authority permitted an action, what action was attempted, and what outcome was observed.

A record's existence alone must never prove that a transition was legitimate.

## 2. Lifecycle transitions

Each authoritative entity must define its legal transition graph before tables or APIs are implemented.

At minimum, designs must distinguish:

- proposed from accepted;
- provisional from validated;
- active from expired;
- current from superseded;
- withdrawn from invalidated;
- rejected from failed;
- requested from authorized;
- authorized from executed;
- executed from verified;
- preserved from trusted.

Transitions must include the initiating actor, governing authority reference, reason, timestamp, correlation identity, previous state, resulting state, and supporting evidence references.

Database constraints and transactional procedures must reject structurally invalid transitions. HELIX governance remains responsible for deciding whether a validly structured transition is substantively authorized.

## 3. Authority and integrity rules

The future implementation must fail closed when:

- an actor lacks a valid authority grant;
- a capability is outside the grant's scope;
- a grant is expired, revoked, superseded, or not yet active;
- required approval or separation-of-duty evidence is absent;
- the expected prior state does not match;
- evidence hashes or manifests do not reconcile;
- idempotency keys conflict;
- a write would overwrite an immutable original;
- an operation attempts to treat a derived record as canonical;
- a transaction would produce only part of a multi-record transition.

Authentication, database connectivity, and record ownership do not themselves confer mutation authority.

## 4. Evidence and audit requirements

Original evidence artifacts must be preserved without silent mutation.

An evidence record should preserve, where applicable:

- stable evidence identity;
- source and collector identity;
- capture and ingestion timestamps;
- repository, commit, environment, host, tenant, subscription, or system context;
- cryptographic content hash and storage reference;
- media type or schema identity;
- classification and sensitivity;
- chain of custody and transformation history;
- validation and reviewer status;
- related claims, hypotheses, decisions, actions, and outcomes;
- expiry, invalidation, withdrawal, retention, deletion, and supersession status.

OCR, extraction, normalization, summarization, embedding, redaction, and format conversion create derived records linked to the original. They must never replace it.

Audit history must be append-oriented and capable of reconstructing requested, accepted, rejected, invalidated, revoked, expired, superseded, executed, and verified transitions.

## 5. Failure, recovery, and replay behavior

The first implementation design must cover:

- idempotent ingestion and duplicate detection;
- transaction rollback and partial-write prevention;
- artifact-write success with database-write failure;
- database-write success with artifact-write failure;
- hash mismatch and missing artifact detection;
- replay after interrupted processing;
- reconciliation between canonical state, artifacts, and derived indexes;
- backup and point-in-time restore;
- tested migration rollback or forward-repair strategy;
- corruption detection and quarantine;
- recovery after loss of a derived vector or search index;
- retention, legal hold, controlled deletion, and tombstone semantics.

Recovery must preserve the distinction between restoring bytes, restoring records, restoring valid relationships, and restoring trusted operational state.

## 6. Query requirements

The future persistence design must support bounded queries for:

- the current valid state of an entity;
- the complete lifecycle history of an entity;
- evidence related to a claim, decision, action, or outcome;
- the authority chain governing a transition;
- all decisions and actions derived from a particular evidence item;
- unresolved contradictions and invalidated dependencies;
- records affected by a revocation, expiry, or supersession;
- artifact and manifest integrity status;
- replay and reconciliation status;
- records requiring review, retention action, or recovery.

Current-state projections and materialized views may improve performance, but complete history must remain reconstructable from authoritative records.

## 7. Storage classes

The initial architecture must preserve explicit storage classes.

### Canonical structured state

Authoritative entities, relationships, lifecycle status, authority records, transition records, and integrity constraints.

PostgreSQL is the default candidate, subject to requirements and an explicit architecture decision record. The product choice must follow the model and failure requirements rather than precede them.

### Evidence artifacts

Original logs, reports, screenshots, packet captures, exports, source documents, and test output.

Artifacts should be immutable or version-preserving and linked through hashes, manifests, classifications, and provenance records.

### Audit history

Append-oriented transition and review records sufficient to reconstruct complete history.

### Version-controlled definitions

Schemas, migrations, protocol contracts, policy definitions, capability catalogues, architecture decisions, and validation code remain authoritative in Git where appropriate.

### Derived systems

Embeddings, vector stores, search indexes, caches, summaries, analytics, materialized views, and projections must be rebuildable from authoritative sources.

## 8. Interfaces owned by persistence

A future implementation may expose explicit interfaces for:

- registering evidence and immutable artifacts;
- proposing a transition;
- committing an already-authorized transition;
- recording rejection or failed execution;
- invalidating, withdrawing, expiring, revoking, or superseding a record;
- retrieving an original artifact;
- querying canonical current state and complete history;
- rebuilding and querying derived indexes;
- reconciling artifacts, canonical records, and indexes;
- exporting backup, restore, and replay evidence.

The persistence layer must not provide an uncontrolled generic write interface that bypasses authority, transition, or integrity checks.

## 9. Cross-project boundaries

- **HELIX governance** determines whether a transition is legitimate and authorized.
- **ContextOS** enforces execution and containment boundaries.
- **HELIX Protocol Kernel** defines transport-neutral contracts and evidence identities that persistence must honor.
- **ServiceTracer and other deterministic tools** provide bounded findings and evidence, not unrestricted mutation authority.
- **LineAlert and domain systems** retain ownership of domain-specific machine and operational models.
- **HELIX Data, Evidence, and Persistence** owns durable canonical storage semantics, integrity, audit, recovery, and derived-index rebuildability.

## 10. Legacy prototype classification

`anthonyedgar30000/HelixMemoryService` is evidence from an earlier prototype.

Its useful principles include stable document identity, source retrieval, local-first operation, and treating ChromaDB as a derived index. Its Markdown-as-source-of-truth model and update API are not automatically suitable for canonical HELIX state.

```text
legacy_prototype != approved_architecture
working_search != governed_persistence
markdown_source != canonical_transition_store
chroma_index != evidence authority
```

No code or data from that repository may be imported until a later bounded workstream performs an explicit compatibility, provenance, security, and migration review.

## 11. First dedicated-repository increment

After a dedicated repository is explicitly created and ownership is declared, the first implementation pull request should remain documentation-and-contract focused.

It should include:

1. `.project/active-work.json` with one bounded branch owner;
2. this charter or its promoted equivalent;
3. an authoritative entity and relationship model;
4. lifecycle state machines and transition invariants;
5. authority and integrity rules;
6. storage-class and artifact-boundary decisions;
7. failure, recovery, replay, and reconciliation requirements;
8. query requirements;
9. an architecture decision record evaluating PostgreSQL and artifact storage;
10. tests that validate machine-readable contracts without deploying a database.

It should not yet include production credentials, cloud deployment, destructive migrations, unrestricted APIs, or claims of operational verification.

## 12. Verification gates

Important increments must test:

- schemas, constraints, and migrations;
- transactions and rollback;
- unauthorized and invalid writes;
- duplicate and idempotent ingestion;
- hash and artifact integrity;
- invalidation and supersession;
- backup and restore;
- replay and reconciliation;
- derived-index rebuilding;
- partial-write and storage-failure scenarios.

Every merge must preserve exact-head CI evidence, changed-file scope, review disposition, known limitations, deployment status, and operational-verification status.

## Current classification

```text
workspace_registered: proposed
dedicated_repository_created: false
repository_authority: none
database_schema_implemented: false
database_deployed: false
legacy_prototype_imported: false
protocol_constraints_available: true
safe_next_action: create a dedicated repository and declare one bounded documentation-and-contract workstream
```
