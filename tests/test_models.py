"""Unit tests for the core File Not Found data models."""

from __future__ import annotations

import unittest

from models import CaseData, CaseSolution, Document, EvidenceItem, GameState


def build_case_data() -> CaseData:
    """Create a small reusable case fixture for model tests."""
    evidence = EvidenceItem(
        evidence_id="EV-1",
        label="Camera Still",
        description="A camera captured the suspect vehicle.",
        source_document_id="DOC-1",
        is_key_evidence=True,
    )
    document = Document(
        document_id="DOC-1",
        title="Traffic Camera",
        text="Camera footage summary.",
        unlock_keywords=["traffic camera footage"],
        evidence_items=[evidence],
    )
    return CaseData(
        title="Test Case",
        intro_text="A tiny case for model behavior.",
        suspects=["Alex Kim"],
        documents=[document],
        starting_keywords=["traffic camera footage"],
        solution=CaseSolution(
            correct_suspect="Alex Kim",
            required_evidence_ids={"EV-1"},
        ),
    )


class ModelsTests(unittest.TestCase):
    def test_evidence_item_stores_fields(self) -> None:
        item = EvidenceItem(
            evidence_id="EV-1",
            label="Camera Still",
            description="Vehicle appears on camera.",
            source_document_id="DOC-1",
            is_key_evidence=True,
        )

        self.assertEqual(item.evidence_id, "EV-1")
        self.assertEqual(item.label, "Camera Still")
        self.assertEqual(item.description, "Vehicle appears on camera.")
        self.assertEqual(item.source_document_id, "DOC-1")
        self.assertTrue(item.is_key_evidence)

    def test_document_matches_exact_unlock_keyword(self) -> None:
        document = build_case_data().documents[0]

        self.assertTrue(document.matches_keyword("traffic camera footage"))

    def test_document_does_not_match_unknown_keyword(self) -> None:
        document = build_case_data().documents[0]

        self.assertFalse(document.matches_keyword("repair receipt"))

    def test_document_matches_keyword_requires_exact_case(self) -> None:
        document = build_case_data().documents[0]

        self.assertFalse(document.matches_keyword("Traffic Camera Footage"))

    def test_document_get_evidence_by_id_returns_match(self) -> None:
        document = build_case_data().documents[0]

        self.assertEqual(document.get_evidence_by_id("EV-1"), document.evidence_items[0])

    def test_document_get_evidence_by_id_requires_exact_id(self) -> None:
        document = build_case_data().documents[0]

        self.assertIsNone(document.get_evidence_by_id("ev-1"))

    def test_document_get_evidence_by_id_returns_none_for_unknown_id(self) -> None:
        document = build_case_data().documents[0]

        self.assertIsNone(document.get_evidence_by_id("EV-404"))

    def test_case_solution_stores_answer_fields(self) -> None:
        solution = CaseSolution(
            correct_suspect="Alex Kim",
            required_evidence_ids={"EV-1", "EV-2"},
        )

        self.assertEqual(solution.correct_suspect, "Alex Kim")
        self.assertEqual(solution.required_evidence_ids, {"EV-1", "EV-2"})

    def test_case_data_get_document_by_id_returns_match(self) -> None:
        case_data = build_case_data()

        self.assertEqual(case_data.get_document_by_id("DOC-1"), case_data.documents[0])

    def test_case_data_get_document_by_id_returns_none_for_unknown_id(self) -> None:
        case_data = build_case_data()

        self.assertIsNone(case_data.get_document_by_id("DOC-404"))

    def test_game_state_mark_keyword_used_adds_keyword(self) -> None:
        state = GameState(case_data=build_case_data())

        state.mark_keyword_used("traffic camera footage")

        self.assertEqual(state.used_keywords, {"traffic camera footage"})

    def test_game_state_defaults_start_empty_and_unfinished(self) -> None:
        state = GameState(case_data=build_case_data())

        self.assertEqual(state.available_keywords, set())
        self.assertEqual(state.used_keywords, set())
        self.assertEqual(state.unlocked_document_ids, set())
        self.assertEqual(state.collected_evidence_ids, set())
        self.assertIsNone(state.selected_suspect)
        self.assertFalse(state.game_over)
        self.assertFalse(state.player_won)

    def test_game_state_unlock_document_updates_state_and_document(self) -> None:
        case_data = build_case_data()
        state = GameState(case_data=case_data)

        state.unlock_document("DOC-1")

        self.assertEqual(state.unlocked_document_ids, {"DOC-1"})
        self.assertTrue(case_data.documents[0].is_unlocked)

    def test_game_state_unlock_document_handles_missing_document_id(self) -> None:
        case_data = build_case_data()
        state = GameState(case_data=case_data)

        state.unlock_document("DOC-404")

        self.assertIn("DOC-404", state.unlocked_document_ids)
        self.assertFalse(case_data.documents[0].is_unlocked)

    def test_game_state_collect_evidence_adds_evidence_id(self) -> None:
        state = GameState(case_data=build_case_data())

        state.collect_evidence("EV-1")

        self.assertEqual(state.collected_evidence_ids, {"EV-1"})

    def test_game_state_collect_evidence_does_not_duplicate_ids(self) -> None:
        state = GameState(case_data=build_case_data())

        state.collect_evidence("EV-1")
        state.collect_evidence("EV-1")

        self.assertEqual(state.collected_evidence_ids, {"EV-1"})


if __name__ == "__main__":
    unittest.main()
