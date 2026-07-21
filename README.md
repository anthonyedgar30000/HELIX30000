# HELIX30000

Umbrella coordination and reality-control repository for HELIX governed-agent engineering.

## Purpose

This repository maps conversational agents to durable repository authority. Chat titles are a usability layer; GitHub branch state, pull-request metadata, CI evidence, and repository `.project/` records remain authoritative.

## Reality precedence

1. Live GitHub pull-request, branch, and CI metadata.
2. The active branch's declared `.project/` ownership and capability boundary.
3. Merged `main` state for canonical completed reality.
4. The HELIX conversation-role registry in this repository.
5. Chat titles, memory, and informal conversation claims.

Never silently combine work-in-progress branch state with merged `main` state.

## Conversation-role registry

`.helix/conversation-role-registry.json` records:

- the desired visible chat title;
- whether a conversation is an owner, reviewer, control tower, unresolved candidate, design reference, backlog, or archive;
- the repository, branch, and pull request it targets;
- allowed and prohibited actions;
- lifecycle state from proposed through operationally verified;
- the evidence used to establish the role.

The registry can prescribe a title, but it cannot rename a ChatGPT conversation. Renaming remains a manual workspace action.

## Current bounded increment

Branch: `feature/conversation-role-registry-v0.1`

Objective: create a machine-readable conversation-role registry, validation rules, tests, role-card guidance, and a no-secret CI gate. This increment does not modify ServiceTracer, ContextOS, the HELIX Protocol Kernel, ChatGPT UI state, Azure, or any runtime system.
