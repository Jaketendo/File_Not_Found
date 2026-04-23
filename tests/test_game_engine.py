"""Unit tests for the File Not Found game engine."""

from __future__ import annotations

from dataclasses import dataclass, field
import unittest

from game_engine import (
    GameEngine,
    _as_value_list,
    _clean_text,
    _find_matching_string,
    _get_document_label,
    _ordered_unique_strings,
    add_discovered_keywords,
    collect_evidence_from_document as collect_evidence_from_document_wrapper,
    create_new_game,
    get_unlocked_documents,
    is_game_over,
    read_document,
    search_keyword,
    submit_case_answer,
)
from models import CaseData, CaseSolution, Document, EvidenceItem


@dataclass
class StartsUnlockedDocument:
    """Simple document type for testing the starts_unlocked path."""

    document_id: str
    title: str
    text: str
    unlock_keywords: list[str] = field(default_factory=list)
    discovered_keywords: list[str] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    is_unlocked: bool = False
    starts_unlocked: bool = False


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
            ),
            EvidenceItem(
                evidence_id="E1B",
                label="paint",
                description="Dark paint transfer found at the scene",
                source_document_id="DOC-1",
            ),
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
        intro_text="  Test   case summary  ",
        suspects=["Tyler Smith", "Jordan Reed"],
        documents=[document_1, document_2, document_3, document_4, document_5, document_6],
        starting_keywords=["accident timeline"],
        solution=CaseSolution(
            correct_suspect="Tyler Smith",
            required_evidence_ids={"E2", "E3", "E4"},
        ),
    )


def build_case_with_unused_valid_keyword() -> CaseData:
    """Create a case where an available keyword matches no documents."""

    case_data = build_test_case()
    case_data.starting_keywords = ["ghost lead"]
    return case_data


def build_case_with_initially_unlocked_document() -> CaseData:
    """Create a case that exercises the starts_unlocked branch."""

    unlocked_document = StartsUnlockedDocument(
        document_id="DOC-START",
        title="Starting Lead",
        text="Already available document",
        unlock_keywords=["starting lead"],
        discovered_keywords=["second lead", "second lead", "   "],
        evidence_items=[],
        starts_unlocked=True,
    )
    locked_document = StartsUnlockedDocument(
        document_id="DOC-LATER",
        title="Second Lead",
        text="Locked document",
        unlock_keywords=["second lead"],
        discovered_keywords=[],
        evidence_items=[],
        starts_unlocked=False,
    )
    return CaseData(
        title="Starts Unlocked",
        intro_text="Case with one document already available",
        suspects=["Tyler Smith"],
        documents=[unlocked_document, locked_document],
        starting_keywords=["starting lead"],
        solution=CaseSolution(correct_suspect="Tyler Smith", required_evidence_ids=set()),
    )


class GameEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_data = build_test_case()
        self.state = create_new_game(self.case_data)
        self.engine = GameEngine.from_state(self.state)

    def unlock_all_key_documents(self) -> None:
        """Reveal the documents needed for the submission tests."""

        self.engine.search_keyword("accident timeline")
        self.engine.search_keyword("traffic camera footage")
        self.engine.search_keyword("vehicle registration database")
        self.engine.search_keyword("auto repair records")

    def test_game_engine_builds_state_without_explicit_state(self) -> None:
        engine = GameEngine(self.case_data)

        self.assertEqual(engine.get_case_summary(), "Test case summary")
        self.assertEqual(engine.get_suspects(), ["Tyler Smith", "Jordan Reed"])
        self.assertFalse(engine.is_game_over())
        self.assertEqual(engine.state.available_keywords, {"accident timeline"})

    def test_create_new_game_sets_starting_keywords(self) -> None:
        self.assertEqual(self.state.available_keywords, {"accident timeline"})
        self.assertEqual(self.state.used_keywords, set())
        self.assertEqual(self.state.unlocked_document_ids, set())

    def test_create_new_game_unlocks_initial_documents_and_discovers_keywords(self) -> None:
        case_data = build_case_with_initially_unlocked_document()

        state = create_new_game(case_data)

        self.assertEqual(state.unlocked_document_ids, {"DOC-START"})
        self.assertIn("second lead", state.available_keywords)
        self.assertTrue(case_data.documents[0].is_unlocked)
        self.assertFalse(case_data.documents[1].is_unlocked)

    def test_get_available_keywords_excludes_used_keywords_by_default(self) -> None:
        self.engine.search_keyword("accident timeline")

        self.assertEqual(
            self.engine.get_available_keywords(),
            ["auto repair records", "traffic camera footage", "witness testimony"],
        )
        self.assertEqual(
            self.engine.get_available_keywords(include_used=True),
            [
                "accident timeline",
                "auto repair records",
                "traffic camera footage",
                "witness testimony",
            ],
        )

    def test_get_used_keywords_returns_sorted_keywords(self) -> None:
        self.state.used_keywords.update({"Witness Testimony", "accident timeline"})

        self.assertEqual(
            self.engine.get_used_keywords(),
            ["accident timeline", "Witness Testimony"],
        )

    def test_search_rejects_empty_input(self) -> None:
        result = self.engine.search_keyword("   ")

        self.assertEqual(result.status, "empty_input")
        self.assertEqual(result.message, "Enter a keyword before searching.")

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
        self.assertEqual(self.state.unlocked_document_ids, {"DOC-1", "DOC-6"})

    def test_search_returns_no_results_for_valid_keyword_without_matching_documents(self) -> None:
        case_data = build_case_with_unused_valid_keyword()
        engine = GameEngine(case_data)

        result = engine.search_keyword("ghost lead")

        self.assertEqual(result.status, "no_results")
        self.assertEqual(result.message, "No results matched that keyword.")
        self.assertEqual(engine.state.used_keywords, {"ghost lead"})

    def test_search_returns_no_new_documents_when_all_matches_are_already_unlocked(self) -> None:
        self.state.unlocked_document_ids.update({"DOC-1", "DOC-6"})

        result = self.engine.search_keyword("accident timeline")

        self.assertEqual(result.status, "no_new_documents")
        self.assertEqual(
            result.message,
            "That keyword is relevant, but it did not reveal any new documents.",
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

    def test_search_message_without_new_keywords_uses_single_document_text(self) -> None:
        self.unlock_all_key_documents()

        result = self.engine.search_keyword("witness testimony")

        self.assertEqual(result.status, "success")
        self.assertEqual({document.document_id for document in result.unlocked_documents}, {"DOC-5"})
        self.assertNotIn("New keywords discovered:", result.message)
        self.assertIn("Unlocked 1 new document", result.message)

    def test_wrapper_get_unlocked_documents_returns_unlocked_docs(self) -> None:
        self.engine.search_keyword("accident timeline")

        unlocked = get_unlocked_documents(self.state)

        self.assertEqual([document.document_id for document in unlocked], ["DOC-1", "DOC-6"])

    def test_read_document_only_returns_unlocked_documents(self) -> None:
        self.assertIsNone(read_document(self.state, "DOC-1"))

        self.engine.search_keyword("accident timeline")

        self.assertIsNotNone(read_document(self.state, "DOC-1"))
        self.assertIsNone(self.engine.get_document("DOC-999"))

    def test_add_discovered_keywords_wrapper_ignores_duplicates(self) -> None:
        add_discovered_keywords(self.state, [self.case_data.documents[0], self.case_data.documents[5]])

        self.assertEqual(
            self.engine.get_available_keywords(include_used=True),
            ["accident timeline", "auto repair records", "traffic camera footage", "witness testimony"],
        )

    def test_collect_evidence_rejects_empty_invalid_and_duplicate_selection(self) -> None:
        self.engine.search_keyword("accident timeline")

        empty_result = self.engine.collect_evidence("")
        missing_result = self.engine.collect_evidence("E999")
        success_result = self.engine.collect_evidence("e1")
        duplicate_result = self.engine.collect_evidence("E1")

        self.assertEqual(empty_result.status, "empty_selection")
        self.assertEqual(missing_result.status, "invalid_evidence")
        self.assertEqual(success_result.status, "success")
        self.assertEqual(duplicate_result.status, "already_collected")
        self.assertEqual(self.state.collected_evidence_ids, {"E1"})

    def test_collect_evidence_from_document_rejects_invalid_document(self) -> None:
        result = self.engine.collect_evidence_from_document("DOC-999", ["E1"])

        self.assertEqual(result.status, "invalid_document")
        self.assertEqual(result.document_id, "DOC-999")

    def test_collect_evidence_from_document_rejects_locked_document(self) -> None:
        result = self.engine.collect_evidence_from_document("DOC-2", ["E2"])

        self.assertEqual(result.status, "locked_document")
        self.assertEqual(self.state.collected_evidence_ids, set())

    def test_collect_evidence_from_document_rejects_empty_selection(self) -> None:
        self.engine.search_keyword("accident timeline")

        result = self.engine.collect_evidence_from_document("DOC-1", [])

        self.assertEqual(result.status, "empty_selection")
        self.assertEqual(result.document_id, "DOC-1")

    def test_collect_evidence_from_document_handles_duplicates(self) -> None:
        self.engine.search_keyword("accident timeline")

        first_result = self.engine.collect_evidence_from_document("DOC-1", ["e1"])
        second_result = self.engine.collect_evidence_from_document("DOC-1", ["E1"])

        self.assertEqual(first_result.status, "success")
        self.assertEqual(second_result.status, "already_collected")
        self.assertEqual(self.state.collected_evidence_ids, {"E1"})

    def test_collect_evidence_from_document_can_return_partial_success(self) -> None:
        self.engine.search_keyword("accident timeline")
        self.engine.collect_evidence_from_document("DOC-1", ["E1"])

        result = self.engine.collect_evidence_from_document("DOC-1", ["E1", "E1B"])

        self.assertEqual(result.status, "partial_success")
        self.assertEqual(result.collected_evidence_ids, ("E1B",))
        self.assertEqual(result.already_collected_evidence_ids, ("E1",))

    def test_collect_evidence_from_document_rejects_wrong_document_evidence(self) -> None:
        self.engine.search_keyword("accident timeline")

        result = self.engine.collect_evidence_from_document("DOC-1", ["E2"])

        self.assertEqual(result.status, "invalid_evidence")
        self.assertEqual(result.invalid_evidence_ids, ("E2",))

    def test_get_collected_evidence_returns_items_in_case_order(self) -> None:
        self.engine.search_keyword("accident timeline")
        self.engine.search_keyword("witness testimony")
        self.engine.collect_evidence_from_document("DOC-5", ["E5"])
        self.engine.collect_evidence_from_document("DOC-1", ["E1"])

        collected = self.engine.get_collected_evidence()

        self.assertEqual([item.evidence_id for item in collected], ["E1", "E5"])

    def test_build_submission_keeps_only_collected_evidence_and_cleans_suspect(self) -> None:
        self.engine.search_keyword("accident timeline")
        self.engine.collect_evidence_from_document("DOC-1", ["E1"])

        submission = self.engine.build_submission("  Tyler Smith  ", ["e1", "E404"])

        self.assertEqual(submission.suspect_id, "Tyler Smith")
        self.assertEqual(submission.evidence_ids, frozenset({"E1"}))
        self.assertEqual(submission.rejected_evidence_ids, ("E404",))

    def test_submit_case_marks_game_over_and_ignores_uncollected_evidence(self) -> None:
        self.unlock_all_key_documents()
        self.engine.collect_evidence_from_document("DOC-2", ["E2"])
        self.engine.collect_evidence_from_document("DOC-3", ["E3"])
        self.engine.collect_evidence_from_document("DOC-4", ["E4"])

        result = self.engine.submit_case("Tyler Smith", ["E2", "E3", "E4", "E999"])

        self.assertTrue(result.is_win)
        self.assertTrue(self.state.game_over)
        self.assertTrue(self.state.player_won)
        self.assertEqual(self.state.selected_suspect, "Tyler Smith")
        self.assertIn("Ignored evidence that had not been collected: E999.", result.message)

    def test_submit_case_losing_path_sets_player_won_false(self) -> None:
        self.unlock_all_key_documents()
        self.engine.collect_evidence_from_document("DOC-2", ["E2"])
        self.engine.collect_evidence_from_document("DOC-3", ["E3"])
        self.engine.collect_evidence_from_document("DOC-4", ["E4"])

        result = self.engine.submit_case("Jordan Reed", ["E2", "E3", "E4"])

        self.assertFalse(result.is_win)
        self.assertFalse(self.state.player_won)
        self.assertEqual(result.message, "Case not solved: the suspect is incorrect.")

    def test_wrappers_collect_submit_and_game_over_work_together(self) -> None:
        self.unlock_all_key_documents()

        success, collect_message = collect_evidence_from_document_wrapper(self.state, "DOC-2", ["E2"])
        self.assertTrue(success)
        self.assertEqual(collect_message, "Collected evidence: E2.")

        win, submit_message = submit_case_answer(self.state, "Tyler Smith", {"E2"})

        self.assertFalse(win)
        self.assertTrue(is_game_over(self.state))
        self.assertIn("required evidence is missing", submit_message)

    def test_private_helper_functions_cover_input_normalization_paths(self) -> None:
        self.assertEqual(_as_value_list(None), [])
        self.assertEqual(_as_value_list("E1"), ["E1"])
        self.assertEqual(_as_value_list({"b", "A"}), ["A", "b"])
        self.assertEqual(_clean_text(None), "")
        self.assertEqual(_clean_text("  a   b "), "a b")
        self.assertEqual(_ordered_unique_strings([" A ", "a", "", "B"]), ["A", "B"])
        self.assertEqual(_find_matching_string(["Alpha", "Beta"], " beta "), "Beta")
        self.assertIsNone(_find_matching_string(["Alpha"], ""))
        self.assertEqual(_get_document_label(Document("DOC-X", "", "text")), "DOC-X")

    def test_wrapper_search_keyword_returns_documents_and_message(self) -> None:
        new_documents, message = search_keyword(self.state, "accident timeline")

        self.assertEqual({document.document_id for document in new_documents}, {"DOC-1", "DOC-6"})
        self.assertIn("Unlocked 2 new documents", message)


if __name__ == "__main__":
    unittest.main()
