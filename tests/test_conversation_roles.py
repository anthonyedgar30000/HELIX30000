from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_conversation_roles import (  # noqa: E402
    RegistryValidationError,
    validate_registry,
)


class ConversationRoleRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_path = ROOT / ".helix" / "conversation-role-registry.json"
        cls.registry = json.loads(cls.registry_path.read_text(encoding="utf-8"))

    def test_current_registry_validates(self) -> None:
        result = validate_registry(copy.deepcopy(self.registry))
        self.assertTrue(result["valid"])
        self.assertEqual(result["role_count"], 9)
        self.assertEqual(result["confirmed_writer_count"], 2)
        self.assertEqual(result["chat_title_application"], "manual_only")

    def test_duplicate_confirmed_writer_for_branch_is_rejected(self) -> None:
        modified = copy.deepcopy(self.registry)
        duplicate = copy.deepcopy(modified["roles"][1])
        duplicate["role_id"] = "servicetracer-pr27-second-owner"
        duplicate["desired_chat_title"] = "[OWNER] ServiceTracer — Duplicate Owner"
        modified["roles"].append(duplicate)
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_review_only_role_cannot_claim_repository_write(self) -> None:
        modified = copy.deepcopy(self.registry)
        reviewer = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "servicetracer-pr27-reviewer"
        )
        reviewer["allowed_actions"].append("repository_write")
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_unresolved_role_cannot_claim_branch_ownership(self) -> None:
        modified = copy.deepcopy(self.registry)
        unresolved = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "contextos-pr13-owner-unresolved"
        )
        unresolved["owned_repository"] = "anthonyedgar30000/ContextOS"
        unresolved["owned_branch"] = "feature/helix-query-bridge"
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_control_tower_is_not_a_persistent_branch_owner(self) -> None:
        control = next(
            role
            for role in self.registry["roles"]
            if role["role_id"] == "helix-control-tower"
        )
        self.assertEqual(control["authority_state"], "coordination_only")
        self.assertIsNone(control["owned_repository"])
        self.assertIsNone(control["owned_branch"])
        self.assertNotIn("repository_write", control["allowed_actions"])
        self.assertNotIn(
            "repository_write_declared_scope",
            control["allowed_actions"],
        )

    def test_control_tower_cannot_claim_repository_write(self) -> None:
        modified = copy.deepcopy(self.registry)
        control = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "helix-control-tower"
        )
        control["allowed_actions"].append("repository_write_declared_scope")
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_merged_registry_records_skipped_independent_review(self) -> None:
        control = next(
            role
            for role in self.registry["roles"]
            if role["role_id"] == "helix-control-tower"
        )
        self.assertTrue(control["lifecycle"]["ci_verified"])
        self.assertTrue(control["lifecycle"]["merged"])
        self.assertFalse(control["lifecycle"]["deployed"])
        self.assertFalse(control["lifecycle"]["operationally_verified"])
        self.assertIn(
            "independent_review_not_completed",
            control["current_status"],
        )
        self.assertIn(
            "submitted reviews none",
            control["evidence"]["observed_ref"],
        )

    def test_role_title_prefix_must_match_role_type(self) -> None:
        modified = copy.deepcopy(self.registry)
        owner = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "helix-protocol-kernel-pr4-owner"
        )
        owner["desired_chat_title"] = "[REVIEW] HELIX — Wrong Prefix"
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_lifecycle_cannot_claim_deployed_before_merge(self) -> None:
        modified = copy.deepcopy(self.registry)
        owner = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "servicetracer-pr27-owner"
        )
        owner["lifecycle"]["deployed"] = True
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_pull_request_target_requires_exact_head_sha(self) -> None:
        modified = copy.deepcopy(self.registry)
        owner = next(
            role
            for role in modified["roles"]
            if role["role_id"] == "servicetracer-pr27-owner"
        )
        owner["target"]["head_sha"] = None
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)

    def test_chat_titles_remain_manual_workspace_actions(self) -> None:
        modified = copy.deepcopy(self.registry)
        modified["authority_model"]["title_application"] = "automatic"
        with self.assertRaises(RegistryValidationError):
            validate_registry(modified)


if __name__ == "__main__":
    unittest.main()
