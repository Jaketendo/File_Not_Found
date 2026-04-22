"""Tests for main.py — File Not Found 

Run with:
    python -m unittest test_main -v

Coverage:
  handle_search_action, handle_read_action, handle_collect_action,
  handle_submit_action, run_game (command loop)
"""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, "/home/claude")

from models import CaseData, CaseSolution, Document, EvidenceItem, GameState
import main


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ─────────────────────────────────────────────────────────────────────────────

def make_evidence(ev_id="EV-001", label="Deleted Log", desc="A deleted log file.",
                  source="DOC-001", is_key=False):
    return EvidenceItem(
        evidence_id=ev_id,
        label=label,
        description=desc,
        source_document_id=source,
        is_key_evidence=is_key,
    )


def make_document(doc_id="DOC-001", title="Server Logs",
                  text="Login at 03:00 from unknown IP.",
                  unlock_keywords=None, discovered_keywords=None,
                  evidence_items=None, is_unlocked=False):
    return Document(
        document_id=doc_id,
        title=title,
        text=text,
        unlock_keywords=unlock_keywords or ["server logs"],
        discovered_keywords=discovered_keywords or [],
        evidence_items=evidence_items or [make_evidence()],
        is_unlocked=is_unlocked,
    )


def make_case(title="Hit and Run", suspects=None, documents=None,
              starting_keywords=None, solution=None):
    return CaseData(
        title=title,
        intro_text="A hit-and-run occurred at Fulton and Mercer.",
        suspects=suspects or ["Tyler Smith", "Emily Carter", "Marcus Webb"],
        documents=documents or [make_document()],
        starting_keywords=starting_keywords or ["accident timeline"],
        solution=solution or CaseSolution(
            correct_suspect="Tyler Smith",
            required_evidence_ids={"EV-001"},
        ),
    )


def make_state(case=None, unlocked=None, collected=None, available_keywords=None,
               game_over=False):
    case = case or make_case()
    return GameState(
        case_data=case,
        available_keywords=set(available_keywords or case.starting_keywords),
        unlocked_document_ids=set(unlocked or []),
        collected_evidence_ids=set(collected or []),
        game_over=game_over,
    )


# ─────────────────────────────────────────────────────────────────────────────
# handle_search_action
# ─────────────────────────────────────────────────────────────────────────────

class TestHandleSearchAction(unittest.TestCase):

    def test_calls_prompt_keyword(self):
        state = make_state()
        with patch("cli.prompt_keyword", return_value="") as mock_kw, \
             patch("cli.print_error"), patch("cli.print_info"):
            main.handle_search_action(state)
        mock_kw.assert_called_once()

    def test_shows_error_on_empty_keyword(self):
        state = make_state()
        with patch("cli.prompt_keyword", return_value=""), \
             patch("cli.print_error") as mock_err:
            main.handle_search_action(state)
        mock_err.assert_called_once()

    def test_displays_search_results_on_valid_keyword(self):
        state = make_state()
        with patch("cli.prompt_keyword", return_value="accident timeline"), \
             patch("main.search_keyword", return_value=([], "No results.")), \
             patch("cli.display_search_results") as mock_display:
            main.handle_search_action(state)
        mock_display.assert_called_once()

    def test_passes_keyword_to_engine(self):
        state = make_state()
        with patch("cli.prompt_keyword", return_value="traffic camera footage"), \
             patch("main.search_keyword", return_value=([], "ok.")) as mock_eng, \
             patch("cli.display_search_results"):
            main.handle_search_action(state)
        call_args = mock_eng.call_args
        self.assertIsNotNone(call_args, "search_keyword was never called")
        self.assertIn("traffic camera footage",
                      call_args.args + tuple(call_args.kwargs.values()))

    def test_newly_unlocked_docs_passed_to_display(self):
        doc = make_document(doc_id="DOC-004")
        state = make_state()
        with patch("cli.prompt_keyword", return_value="traffic camera footage"), \
             patch("main.search_keyword", return_value=([doc], "Unlocked 1 document.")), \
             patch("cli.display_search_results") as mock_display:
            main.handle_search_action(state)
        self.assertTrue(mock_display.called, "display_search_results was not called")
        args, _ = mock_display.call_args
        self.assertIn(doc, args[0])


# ─────────────────────────────────────────────────────────────────────────────
# handle_read_action
# ─────────────────────────────────────────────────────────────────────────────

class TestHandleReadAction(unittest.TestCase):

    def test_prints_info_when_no_unlocked_documents(self):
        state = make_state(unlocked=[])
        with patch("main.get_unlocked_documents", return_value=[]), \
             patch("cli.print_info") as mock_info:
            main.handle_read_action(state)
        mock_info.assert_called_once()

    def test_prompts_document_choice_when_docs_available(self):
        doc = make_document(doc_id="DOC-001")
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="") as mock_choice, \
             patch("cli.print_info"):
            main.handle_read_action(state)
        mock_choice.assert_called_once()

    def test_shows_info_when_player_cancels_selection(self):
        doc = make_document(doc_id="DOC-001")
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value=""), \
             patch("cli.print_info") as mock_info:
            main.handle_read_action(state)
        mock_info.assert_called()

    def test_displays_document_on_valid_choice(self):
        doc = make_document(doc_id="DOC-001")
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=doc), \
             patch("cli.display_document") as mock_display, \
             patch("cli.print_info"):
            main.handle_read_action(state)
        mock_display.assert_called_once_with(doc)

    def test_shows_error_when_document_not_found(self):
        doc = make_document(doc_id="DOC-001")
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=None), \
             patch("cli.print_info"), \
             patch("cli.print_error") as mock_err:
            main.handle_read_action(state)
        mock_err.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# handle_collect_action
# ─────────────────────────────────────────────────────────────────────────────

class TestHandleCollectAction(unittest.TestCase):

    def test_prints_info_when_no_unlocked_documents(self):
        state = make_state(unlocked=[])
        with patch("main.get_unlocked_documents", return_value=[]), \
             patch("cli.print_info") as mock_info:
            main.handle_collect_action(state)
        mock_info.assert_called_once()

    def test_prompts_document_choice(self):
        doc = make_document(doc_id="DOC-001")
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="") as mock_choice, \
             patch("cli.print_info"):
            main.handle_collect_action(state)
        mock_choice.assert_called_once()

    def test_displays_document_before_collecting_evidence(self):
        ev = make_evidence()
        doc = make_document(doc_id="DOC-001", evidence_items=[ev])
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=doc), \
             patch("cli.display_document") as mock_display, \
             patch("cli.prompt_evidence_ids", return_value=[]), \
             patch("cli.print_info"):
            main.handle_collect_action(state)
        mock_display.assert_called_once_with(doc)

    def test_shows_info_when_no_evidence_selected(self):
        ev = make_evidence()
        doc = make_document(doc_id="DOC-001", evidence_items=[ev])
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=doc), \
             patch("cli.display_document"), \
             patch("cli.prompt_evidence_ids", return_value=[]), \
             patch("cli.print_info") as mock_info:
            main.handle_collect_action(state)
        mock_info.assert_called()

    def test_shows_info_on_successful_collection(self):
        ev = make_evidence()
        doc = make_document(doc_id="DOC-001", evidence_items=[ev])
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=doc), \
             patch("cli.display_document"), \
             patch("cli.prompt_evidence_ids", return_value=["EV-001"]), \
             patch("main.collect_evidence_from_document", return_value=(True, "Collected.")), \
             patch("cli.print_info") as mock_info:
            main.handle_collect_action(state)
        mock_info.assert_called()

    def test_shows_error_on_failed_collection(self):
        ev = make_evidence()
        doc = make_document(doc_id="DOC-001", evidence_items=[ev])
        state = make_state(unlocked=["DOC-001"])
        with patch("main.get_unlocked_documents", return_value=[doc]), \
             patch("cli.prompt_document_choice", return_value="DOC-001"), \
             patch("main.read_document", return_value=doc), \
             patch("cli.display_document"), \
             patch("cli.prompt_evidence_ids", return_value=["EV-BAD"]), \
             patch("main.collect_evidence_from_document", return_value=(False, "Not found.")), \
             patch("cli.print_error") as mock_err:
            main.handle_collect_action(state)
        mock_err.assert_called()


# ─────────────────────────────────────────────────────────────────────────────
# handle_submit_action
# ─────────────────────────────────────────────────────────────────────────────

class TestHandleSubmitAction(unittest.TestCase):

    def test_prompts_suspect(self):
        state = make_state(collected={"EV-001"})
        with patch("cli.prompt_suspect", return_value="Tyler Smith") as mock_sus, \
             patch("main.submit_case_answer", return_value=(True, "Win!")), \
             patch("cli.display_submission_result"), \
             patch("cli.print_info"):
            main.handle_submit_action(state)
        mock_sus.assert_called_once()

    def test_shows_error_when_no_suspect_entered(self):
        state = make_state(collected={"EV-001"})
        with patch("cli.prompt_suspect", return_value=""), \
             patch("cli.print_info"), \
             patch("cli.print_error") as mock_err:
            main.handle_submit_action(state)
        mock_err.assert_called_once()

    def test_displays_submission_result_on_success(self):
        state = make_state(collected={"EV-001"})
        with patch("cli.prompt_suspect", return_value="Tyler Smith"), \
             patch("main.submit_case_answer", return_value=(True, "Case solved.")), \
             patch("cli.display_submission_result") as mock_result, \
             patch("cli.print_info"):
            main.handle_submit_action(state)
        mock_result.assert_called_once()

    def test_passes_win_flag_to_display(self):
        state = make_state(collected={"EV-001"})
        with patch("cli.prompt_suspect", return_value="Tyler Smith"), \
             patch("main.submit_case_answer", return_value=(True, "You win!")), \
             patch("cli.display_submission_result") as mock_result, \
             patch("cli.print_info"):
            main.handle_submit_action(state)
        args, _ = mock_result.call_args
        self.assertTrue(args[0])

    def test_passes_loss_flag_to_display(self):
        state = make_state(collected={"EV-001"})
        with patch("cli.prompt_suspect", return_value="Wrong Person"), \
             patch("main.submit_case_answer", return_value=(False, "You lose.")), \
             patch("cli.display_submission_result") as mock_result, \
             patch("cli.print_info"):
            main.handle_submit_action(state)
        args, _ = mock_result.call_args
        self.assertFalse(args[0])

    def test_collected_evidence_passed_to_engine(self):
        state = make_state(collected={"EV-001", "EV-CAM"})
        with patch("cli.prompt_suspect", return_value="Tyler Smith"), \
             patch("main.submit_case_answer", return_value=(True, "Win!")) as mock_eng, \
             patch("cli.display_submission_result"), \
             patch("cli.print_info"):
            main.handle_submit_action(state)
        call_args = mock_eng.call_args
        self.assertIsNotNone(call_args, "submit_case_answer was never called")
        submitted_evidence = (call_args.args[2] if len(call_args.args) >= 3
                              else call_args.kwargs.get("evidence_ids"))
        self.assertIn("EV-001", submitted_evidence)


# ─────────────────────────────────────────────────────────────────────────────
# run_game — command loop
# ─────────────────────────────────────────────────────────────────────────────

class TestRunGame(unittest.TestCase):
    """run_game should route all commands and exit cleanly."""

    def _base_patches(self, actions, extra=None):
        """Return a dict of standard patch targets for run_game tests."""
        p = {
            "main.build_demo_case": MagicMock(return_value=make_case()),
            "main.create_new_game": MagicMock(return_value=make_state()),
            "cli.display_welcome": MagicMock(),
            "cli.display_help": MagicMock(),
            "cli.prompt_main_menu_action": MagicMock(side_effect=iter(actions)),
            "main.is_game_over": MagicMock(return_value=False),
            "cli.print_info": MagicMock(),
            "cli.print_error": MagicMock(),
        }
        if extra:
            p.update(extra)
        return p

    def test_calls_display_welcome_on_start(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome") as mock_welcome, \
             patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", return_value="quit"), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_welcome.assert_called_once()

    def test_calls_display_help_on_start(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), \
             patch("cli.display_help") as mock_help, \
             patch("cli.prompt_main_menu_action", return_value="quit"), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_help.assert_called_once()

    def test_quit_exits_game(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", return_value="quit"), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"), \
             self.assertRaises(SystemExit):
            main.run_game()

    def test_q_alias_exits_game(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", return_value="q"), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"), \
             self.assertRaises(SystemExit):
            main.run_game()

    def test_loop_exits_when_game_over(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action") as mock_prompt, \
             patch("main.is_game_over", return_value=True):
            main.run_game()
        mock_prompt.assert_not_called()

    def test_help_command_shows_help(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), \
             patch("cli.display_help") as mock_help, \
             patch("cli.prompt_main_menu_action", side_effect=iter(["help", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        # Once at startup + once for the "help" command
        self.assertGreaterEqual(mock_help.call_count, 2)

    def test_status_command_calls_display_status(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["status", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.display_status") as mock_status, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_status.assert_called_once()

    def test_search_command_calls_handle_search(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["search", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("main.handle_search_action") as mock_search, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_search.assert_called_once()

    def test_s_alias_triggers_search(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["s", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("main.handle_search_action") as mock_search, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_search.assert_called_once()

    def test_read_command_calls_handle_read(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["read", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("main.handle_read_action") as mock_read, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_read.assert_called_once()

    def test_collect_command_calls_handle_collect(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["collect", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("main.handle_collect_action") as mock_collect, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_collect.assert_called_once()

    def test_submit_command_calls_handle_submit(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["submit", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("main.handle_submit_action") as mock_submit, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_submit.assert_called_once()

    def test_unknown_command_shows_error(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["zzz_unknown", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_error") as mock_err, \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass
        mock_err.assert_called_once()

    def test_blank_input_does_not_crash(self):
        with patch("main.build_demo_case", return_value=make_case()), \
             patch("main.create_new_game", return_value=make_state()), \
             patch("cli.display_welcome"), patch("cli.display_help"), \
             patch("cli.prompt_main_menu_action", side_effect=iter(["", "quit"])), \
             patch("main.is_game_over", return_value=False), \
             patch("cli.print_info"):
            try:
                main.run_game()
            except SystemExit:
                pass  # Reached quit safely — blank input did not crash


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
