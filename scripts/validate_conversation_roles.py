#!/usr/bin/env python3
"""Validate the HELIX conversation-role registry without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "helix.conversation-role-registry.v1"
EXPECTED_PRECEDENCE = [
    "live_github_metadata",
    "active_branch_project_state",
    "merged_main_state",
    "helix_conversation_role_registry",
    "chat_title_memory_or_informal_claim",
]
PREFIX_BY_ROLE = {
    "control_tower": "[CONTROL] ",
    "write_owner": "[OWNER] ",
    "independent_reviewer": "[REVIEW] ",
    "unresolved_owner": "[UNRESOLVED] ",
    "superseded_reference": "[ARCHIVE] ",
    "design_reference": "[DESIGN] ",
    "backlog": "[BACKLOG] ",
    "ui_reference": "[REFERENCE] ",
}
AUTHORITY_BY_ROLE = {
    "control_tower": "confirmed",
    "write_owner": "confirmed",
    "independent_reviewer": "review_only",
    "unresolved_owner": "unresolved",
    "superseded_reference": "handed_off",
    "design_reference": "none",
    "backlog": "none",
    "ui_reference": "none",
}
WRITE_ACTIONS = {"repository_write", "repository_write_declared_scope"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ROLE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")


class RegistryValidationError(ValueError):
    """Raised when registry state violates a HELIX role invariant."""


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RegistryValidationError(f"{field} must be an object")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise RegistryValidationError(f"{field} must be a list")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _nullable_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _text(value, field)


def _string_set(value: Any, field: str) -> set[str]:
    items = [_text(item, f"{field}[]") for item in _list(value, field)]
    if len(items) != len(set(items)):
        raise RegistryValidationError(f"{field} contains duplicates")
    return set(items)


def _validate_lifecycle(value: Any, field: str) -> dict[str, bool]:
    lifecycle = _object(value, field)
    names = [
        "proposed",
        "implemented",
        "ci_verified",
        "merged",
        "deployed",
        "operationally_verified",
    ]
    if set(lifecycle) != set(names):
        raise RegistryValidationError(f"{field} must contain exactly {names}")
    for name in names:
        if not isinstance(lifecycle[name], bool):
            raise RegistryValidationError(f"{field}.{name} must be boolean")

    dependencies = {
        "implemented": "proposed",
        "ci_verified": "implemented",
        "merged": "ci_verified",
        "deployed": "merged",
        "operationally_verified": "deployed",
    }
    for state, prerequisite in dependencies.items():
        if lifecycle[state] and not lifecycle[prerequisite]:
            raise RegistryValidationError(
                f"{field}.{state}=true requires {prerequisite}=true"
            )
    return lifecycle


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise RegistryValidationError("unsupported schema_version")
    _text(registry.get("updated_on"), "updated_on")

    authority_model = _object(registry.get("authority_model"), "authority_model")
    precedence = [
        _text(item, "authority_model.source_precedence[]")
        for item in _list(
            authority_model.get("source_precedence"),
            "authority_model.source_precedence",
        )
    ]
    if precedence != EXPECTED_PRECEDENCE:
        raise RegistryValidationError("authority source precedence changed")
    if authority_model.get("title_application") != "manual_chatgpt_workspace_action":
        raise RegistryValidationError("chat titles must remain a manual workspace action")
    _text(authority_model.get("conflict_rule"), "authority_model.conflict_rule")

    roles = _list(registry.get("roles"), "roles")
    if not roles:
        raise RegistryValidationError("at least one role is required")

    role_ids: set[str] = set()
    titles: set[str] = set()
    confirmed_writers: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}

    for index, role_value in enumerate(roles):
        field = f"roles[{index}]"
        role = _object(role_value, field)
        role_id = _text(role.get("role_id"), f"{field}.role_id")
        if not ROLE_ID_RE.fullmatch(role_id):
            raise RegistryValidationError(f"{field}.role_id is not canonical")
        if role_id in role_ids:
            raise RegistryValidationError(f"duplicate role_id: {role_id}")
        role_ids.add(role_id)

        role_type = _text(role.get("role_type"), f"{field}.role_type")
        if role_type not in PREFIX_BY_ROLE:
            raise RegistryValidationError(f"unsupported role_type: {role_type}")
        counts[role_type] = counts.get(role_type, 0) + 1

        title = _text(role.get("desired_chat_title"), f"{field}.desired_chat_title")
        if not title.startswith(PREFIX_BY_ROLE[role_type]):
            raise RegistryValidationError(
                f"{field}.desired_chat_title must start with {PREFIX_BY_ROLE[role_type]!r}"
            )
        if title in titles:
            raise RegistryValidationError(f"duplicate desired_chat_title: {title}")
        titles.add(title)

        authority_state = _text(
            role.get("authority_state"), f"{field}.authority_state"
        )
        if authority_state != AUTHORITY_BY_ROLE[role_type]:
            raise RegistryValidationError(
                f"{field}.authority_state does not match role_type"
            )

        owned_repository = _nullable_text(
            role.get("owned_repository"), f"{field}.owned_repository"
        )
        owned_branch = _nullable_text(role.get("owned_branch"), f"{field}.owned_branch")
        if owned_repository is not None and not REPOSITORY_RE.fullmatch(owned_repository):
            raise RegistryValidationError(f"{field}.owned_repository is not owner/repo")

        allowed = _string_set(role.get("allowed_actions"), f"{field}.allowed_actions")
        prohibited = _string_set(
            role.get("prohibited_actions"), f"{field}.prohibited_actions"
        )
        overlap = allowed & prohibited
        if overlap:
            raise RegistryValidationError(
                f"{field} allows and prohibits the same actions: {sorted(overlap)}"
            )

        if authority_state == "confirmed":
            if owned_repository is None or owned_branch is None:
                raise RegistryValidationError(
                    f"{field} confirmed authority requires owned repository and branch"
                )
            if not (allowed & WRITE_ACTIONS):
                raise RegistryValidationError(
                    f"{field} confirmed authority requires bounded repository write action"
                )
            writer_key = (owned_repository, owned_branch)
            if writer_key in confirmed_writers:
                raise RegistryValidationError(
                    f"multiple confirmed writers for {owned_repository}:{owned_branch}"
                )
            confirmed_writers.add(writer_key)
        else:
            if owned_repository is not None or owned_branch is not None:
                raise RegistryValidationError(
                    f"{field} non-owner role cannot own a repository or branch"
                )
            if allowed & WRITE_ACTIONS:
                raise RegistryValidationError(
                    f"{field} non-owner role cannot allow repository writes"
                )

        target = _object(role.get("target"), f"{field}.target")
        target_repository = _nullable_text(
            target.get("repository"), f"{field}.target.repository"
        )
        target_branch = _nullable_text(target.get("branch"), f"{field}.target.branch")
        target_pr = target.get("pull_request")
        head_sha = _nullable_text(target.get("head_sha"), f"{field}.target.head_sha")
        if target_repository is not None and not REPOSITORY_RE.fullmatch(target_repository):
            raise RegistryValidationError(f"{field}.target.repository is not owner/repo")
        if target_pr is not None:
            if not isinstance(target_pr, int) or isinstance(target_pr, bool) or target_pr < 1:
                raise RegistryValidationError(f"{field}.target.pull_request is invalid")
            if target_repository is None or target_branch is None or head_sha is None:
                raise RegistryValidationError(
                    f"{field} pull request target requires repository, branch, and head_sha"
                )
        if head_sha is not None and not SHA_RE.fullmatch(head_sha):
            raise RegistryValidationError(f"{field}.target.head_sha is not a full SHA")

        if authority_state == "confirmed":
            if target_repository != owned_repository or target_branch != owned_branch:
                raise RegistryValidationError(
                    f"{field} target must match the confirmed owned repository and branch"
                )

        _text(role.get("current_status"), f"{field}.current_status")
        _validate_lifecycle(role.get("lifecycle"), f"{field}.lifecycle")

        evidence = _object(role.get("evidence"), f"{field}.evidence")
        _text(evidence.get("source_kind"), f"{field}.evidence.source_kind")
        _text(evidence.get("evidence_strength"), f"{field}.evidence.evidence_strength")
        evidence_repository = _text(
            evidence.get("repository"), f"{field}.evidence.repository"
        )
        if not REPOSITORY_RE.fullmatch(evidence_repository):
            raise RegistryValidationError(
                f"{field}.evidence.repository is not owner/repo"
            )
        _text(evidence.get("observed_ref"), f"{field}.evidence.observed_ref")
        _text(evidence.get("observed_on"), f"{field}.evidence.observed_on")

    if counts.get("control_tower") != 1:
        raise RegistryValidationError("exactly one control_tower role is required")

    return {
        "schema_version": "helix.conversation-role-registry-validation.v1",
        "role_count": len(roles),
        "role_type_counts": dict(sorted(counts.items())),
        "confirmed_writer_count": len(confirmed_writers),
        "unique_titles": len(titles),
        "chat_title_application": "manual_only",
        "valid": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(".helix/conversation-role-registry.json"),
    )
    args = parser.parse_args()

    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        if not isinstance(registry, dict):
            raise RegistryValidationError("registry root must be an object")
        result = validate_registry(registry)
    except (OSError, json.JSONDecodeError, RegistryValidationError) as exc:
        print(f"conversation-role registry validation failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
