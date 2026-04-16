"""Unit tests for File Not Found validation rules."""

from __future__ import annotations

import unittest

from models import CaseData, CaseSolution, Document, EvidenceItem, GameState
from validation import (
    filter_new_documents,
    find_matching_documents,
    has_required_evidence,
    is_correct_suspect,
    is_reused_keyword,
    is_valid_keyword,
    normalize_text,
    validate_submission,
)


def build_test_case() -> CaseData:
    """Create a small case fixture for validation tests."""

    return CaseData(
        title="File Not Found",
        intro_text="Test case",
        suspects=["Tyler Smith", "Jordan Reed"],
        documents=[
            Document(
                document_id="DOC-1",
                title="Traffic Camera Footage",
                text="Camera capture",
                unlock_keywords=["traffic camera footage"],
                discovered_keywords=[],
                evidence_items=[
                    EvidenceItem(
                        evidence_id="E2",
                        label="plate",
                        description="Partial plate from the camera",
                        source_document_id="DOC-1",
                        is_key_evidence=True,
                    )
                ],
            ),
            Document(
                document_id="DOC-2",
                title="Car Registration Database",
                text="Registration lookup",
                unlock_keywords=["vehicle registration database"],
                discovered_keywords=[],
                evidence_items=[
                    EvidenceItem(
                        evidence_id="E3",
                        label="registration",
                        description="Plate is registered to Tyler Smith",
                        source_document_id="DOC-2",
                        is_key_evidence=True,
                    )
                ],
            ),
        ],
        starting_keywords=["traffic camera footage"],
        solution=CaseSolution(
            correct_suspect="Tyler Smith",
            required_evidence_ids={"E2", "E3", "E4"},
        ),
    )


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_data = build_test_case()
        self.state = GameState(
            case_data=self.case_data,
            available_keywords={"traffic camera footage", "vehicle registration database"},
            used_keywords={"traffic camera footage"},
            unlocked_document_ids={"DOC-1"},
            collected_evidence_ids={"E2", "E3", "E4"},
        )

    def test_normalize_text_is_case_insensitive_and_trims_spaces(self) -> None:
        self.assertEqual(normalize_text("  Traffic   Camera Footage "), "traffic camera footage")

    def test_find_matching_documents_uses_case_insensitive_keyword_match(self) -> None:
        matches = find_matching_documents(self.case_data, "TRAFFIC CAMERA FOOTAGE")

        self.assertEqual([document.document_id for document in matches], ["DOC-1"])

    def test_filter_new_documents_excludes_already_unlocked_ids(self) -> None:
        filtered = filter_new_documents(self.state, self.case_data.documents)

        self.assertEqual([document.document_id for document in filtered], ["DOC-2"])

    def test_keyword_helpers_reflect_current_state(self) -> None:
        self.assertTrue(is_valid_keyword(self.state, "vehicle registration database"))
        self.assertTrue(is_reused_keyword(self.state, "TRAFFIC CAMERA FOOTAGE"))
        self.assertFalse(is_valid_keyword(self.state, "auto repair records"))

    def test_has_required_evidence_and_is_correct_suspect(self) -> None:
        self.assertTrue(has_required_evidence(self.state))
        self.assertTrue(is_correct_suspect(self.state, "tyler smith"))
        self.assertFalse(is_correct_suspect(self.state, "Jordan Reed"))

    def test_validate_submission_returns_win_for_correct_suspect_and_evidence(self) -> None:
        result = validate_submission("Tyler Smith", {"E2", "E3", "E4"}, self.case_data)

        self.assertTrue(result.is_win)
        self.assertTrue(result.suspect_correct)
        self.assertTrue(result.evidence_correct)
        self.assertEqual(result.missing_evidence_ids, ())

    def test_validate_submission_reports_wrong_suspect(self) -> None:
        result = validate_submission("Jordan Reed", {"E2", "E3", "E4"}, self.case_data)

        self.assertFalse(result.is_win)
        self.assertFalse(result.suspect_correct)
        self.assertTrue(result.evidence_correct)
        self.assertIn("the suspect is incorrect", result.message)

    def test_validate_submission_reports_missing_evidence(self) -> None:
        result = validate_submission("Tyler Smith", {"E2"}, self.case_data)

        self.assertFalse(result.is_win)
        self.assertTrue(result.suspect_correct)
        self.assertFalse(result.evidence_correct)
        self.assertEqual(result.missing_evidence_ids, ("E3", "E4"))

    def test_validate_submission_reports_wrong_suspect_and_missing_evidence(self) -> None:
        result = validate_submission("Jordan Reed", {"E2"}, self.case_data)

        self.assertFalse(result.is_win)
        self.assertFalse(result.suspect_correct)
        self.assertFalse(result.evidence_correct)
        self.assertEqual(result.missing_evidence_ids, ("E3", "E4"))
        self.assertIn("the suspect is incorrect", result.message)
        self.assertIn("required evidence is missing", result.message)


if __name__ == "__main__":
    unittest.main()
