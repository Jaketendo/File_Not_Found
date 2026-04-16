"""Unit tests for the File Not Found game engine."""

from __future__ import annotations

import unittest

from game_engine import GameEngine, create_new_game, read_document, search_keyword
from models import CaseData, CaseSolution, Document, EvidenceItem


def build_test_case() -> CaseData:
    """Create a small case fixture for engine tests."""

    document_1 = Document(
        document_id="DOC-1",
        title="Police Report",
        text="Initial report",
        unlock_keywords=["accident timeline"],
        discovered_keywords=["witness testimony", "traffic camera footage"],
        evidence_items=[
            EvidenceItem(
                evidence_id="E1",
                label="timeline",
                description="Collision time noted",
                source_document_id="DOC-1",
            )
        ],
    )
    document_2 = Document(
        document_id="DOC-2",
        title="Traffic Camera Footage",
        text="Camera stills",
        unlock_keywords=["traffic camera footage"],
        discovered_keywords=["vehicle registration database"],
        evidence_items=[
            EvidenceItem(
                evidence_id="E2",
                label="plate",
                description="Partial plate captured on camera",
                source_document_id="DOC-2",
                is_key_evidence=True,
            )
        ],
    )
    document_3 = Document(
        document_id="DOC-3",
        title="Car Registration Database",
        text="Registration lookup",
        unlock_keywords=["vehicle registration database"],
        discovered_keywords=["auto repair records"],
        evidence_items=[
            EvidenceItem(
                evidence_id="E3",
                label="registration",
                description="Plate JT7KQ4 is registered to Tyler Smith",
                source_document_id="DOC-3",
                is_key_evidence=True,
            )
        ],
    )
    document_4 = Document(
        document_id="DOC-4",
        title="Auto Repair Shop Receipt",
        text="Repair invoice",
        unlock_keywords=["auto repair records"],
        discovered_keywords=[],
        evidence_items=[
            EvidenceItem(
                evidence_id="E4",
                label="repair",
                description="Front-right headlight replaced the next morning",
                source_document_id="DOC-4",
                is_key_evidence=True,
            )
        ],
    )
    document_5 = Document(
        document_id="DOC-5",
        title="Witness Statement",
        text="Witness notes",
        unlock_keywords=["witness testimony"],
        discovered_keywords=[],
        evidence_items=[
            EvidenceItem(
                evidence_id="E5",
                label="witness",
                description="Witness saw the vehicle leave the scene",
                source_document_id="DOC-5",
            )
        ],
    )
    document_6 = Document(
        document_id="DOC-6",
        title="Timeline Summary",
        text="Timeline cross-check",
        unlock_keywords=["accident timeline"],
        discovered_keywords=["auto repair records"],
        evidence_items=[],
    )

    return CaseData(
        title="File Not Found",
        intro_text="Test case",
        suspects=["Tyler Smith", "Jordan Reed"],
        documents=[document_1, document_2, document_3, document_4, document_5, document_6],
        starting_keywords=["accident timeline"],
        solution=CaseSolution(
            correct_suspect="Tyler Smith",
            required_evidence_ids={"E2", "E3", "E4"},
        ),
    )


class GameEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_data = build_test_case()
        self.state = create_new_game(self.case_data)
        self.engine = GameEngine.from_state(self.state)

    def test_create_new_game_sets_starting_keywords(self) -> None:
        self.assertEqual(self.state.available_keywords, {"accident timeline"})
        self.assertEqual(self.state.used_keywords, set())
        self.assertEqual(self.state.unlocked_document_ids, set())

    def test_search_unlocks_all_new_matching_documents_and_discovers_keywords(self) -> None:
        result = self.engine.search_keyword("ACCIDENT TIMELINE")

        self.assertEqual(result.status, "success")
        self.assertEqual(
            {document.document_id for document in result.unlocked_documents},
            {"DOC-1", "DOC-6"},
        )
        self.assertEqual(
            set(result.discovered_keywords),
            {"witness testimony", "traffic camera footage", "auto repair records"},
        )
        self.assertEqual(self.state.used_keywords, {"accident timeline"})
        self.assertEqual(
            self.state.unlocked_document_ids,
            {"DOC-1", "DOC-6"},
        )

    def test_reused_keyword_returns_reused_status(self) -> None:
        self.engine.search_keyword("accident timeline")

        result = self.engine.search_keyword("Accident Timeline")

        self.assertEqual(result.status, "reused")
        self.assertEqual(result.unlocked_documents, ())

    def test_invalid_keyword_returns_no_results(self) -> None:
        result = self.engine.search_keyword("made up keyword")

        self.assertEqual(result.status, "no_results")
        self.assertEqual(result.message, "No results matched that keyword.")
        self.assertEqual(self.state.used_keywords, set())

    def test_read_document_only_returns_unlocked_documents(self) -> None:
        self.assertIsNone(read_document(self.state, "DOC-1"))

        self.engine.search_keyword("accident timeline")

        self.assertIsNotNone(read_document(self.state, "DOC-1"))

    def test_collect_evidence_from_document_rejects_locked_document(self) -> None:
        result = self.engine.collect_evidence_from_document("DOC-2", ["E2"])

        self.assertEqual(result.status, "locked_document")
        self.assertEqual(self.state.collected_evidence_ids, set())

    def test_collect_evidence_from_document_handles_duplicates(self) -> None:
        self.engine.search_keyword("accident timeline")

        first_result = self.engine.collect_evidence_from_document("DOC-1", ["e1"])
        second_result = self.engine.collect_evidence_from_document("DOC-1", ["E1"])

        self.assertEqual(first_result.status, "success")
        self.assertEqual(second_result.status, "already_collected")
        self.assertEqual(self.state.collected_evidence_ids, {"E1"})

    def test_collect_evidence_from_document_rejects_wrong_document_evidence(self) -> None:
        self.engine.search_keyword("accident timeline")

        result = self.engine.collect_evidence_from_document("DOC-1", ["E2"])

        self.assertEqual(result.status, "invalid_evidence")
        self.assertEqual(result.invalid_evidence_ids, ("E2",))

    def test_submit_case_marks_game_over_and_ignores_uncollected_evidence(self) -> None:
        self.engine.search_keyword("accident timeline")
        self.engine.search_keyword("traffic camera footage")
        self.engine.search_keyword("vehicle registration database")
        self.engine.search_keyword("auto repair records")
        self.engine.collect_evidence_from_document("DOC-2", ["E2"])
        self.engine.collect_evidence_from_document("DOC-3", ["E3"])
        self.engine.collect_evidence_from_document("DOC-4", ["E4"])

        result = self.engine.submit_case("Tyler Smith", ["E2", "E3", "E4", "E999"])

        self.assertTrue(result.is_win)
        self.assertTrue(self.state.game_over)
        self.assertTrue(self.state.player_won)
        self.assertEqual(self.state.selected_suspect, "Tyler Smith")
        self.assertIn("Ignored evidence that had not been collected: E999.", result.message)

    def test_wrapper_search_keyword_returns_documents_and_message(self) -> None:
        new_documents, message = search_keyword(self.state, "accident timeline")

        self.assertEqual({document.document_id for document in new_documents}, {"DOC-1", "DOC-6"})
        self.assertIn("Unlocked 2 new documents", message)


if __name__ == "__main__":
    unittest.main()
