"""Tests for main.py — action handlers, command routing, game loop."""

import io
import sys
import unittest
from unittest.mock import patch

from data import build_demo_case, ALL_CASES
from game_engine import create_new_game, search_keyword, get_unlocked_documents, \
    collect_evidence_from_document, submit_case_answer, is_game_over
import main


def _make_state(case_index=0):
    return create_new_game(build_demo_case(case_index))


def _full_state(case_index=0):
    """Return a state where all keywords are searched and all evidence collected."""
    state = _make_state(case_index)
    for _ in range(20):
        remaining = state.available_keywords - state.used_keywords
        if not remaining:
            break
        for kw in list(remaining):
            search_keyword(state, kw)
    for doc in get_unlocked_documents(state):
        for item in doc.evidence_items:
            collect_evidence_from_document(state, doc.document_id, [item.evidence_id])
    return state


def _captured_output(func, *args, **kwargs):
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        func(*args, **kwargs)
    return buf.getvalue()


class TestHandleSearchAction(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(0)

    def test_valid_keyword_unlocks_document(self):
        with patch("cli.prompt_keyword", return_value="accident timeline"):
            with patch("sys.stdout", io.StringIO()):
                main.handle_search_action(self.state)
        self.assertIn("DOC-001", self.state.unlocked_document_ids)

    def test_empty_keyword_prints_error(self):
        with patch("cli.prompt_keyword", return_value=""):
            out = _captured_output(main.handle_search_action, self.state)
        self.assertIn("no keyword", out.lower())

    def test_reused_keyword_does_not_unlock_again(self):
        with patch("cli.prompt_keyword", return_value="accident timeline"):
            with patch("sys.stdout", io.StringIO()):
                main.handle_search_action(self.state)
        count = len(self.state.unlocked_document_ids)
        with patch("cli.prompt_keyword", return_value="accident timeline"):
            with patch("sys.stdout", io.StringIO()):
                main.handle_search_action(self.state)
        self.assertEqual(len(self.state.unlocked_document_ids), count)

    def test_invalid_keyword_shows_no_results(self):
        with patch("cli.prompt_keyword", return_value="banana"):
            out = _captured_output(main.handle_search_action, self.state)
        self.assertIn("no results", out.lower())


class TestHandleReadAction(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(0)

    def test_no_unlocked_docs_shows_info(self):
        self.state.unlocked_document_ids.clear()
        out = _captured_output(main.handle_read_action, self.state)
        self.assertIn("you have not unlocked", out.lower())

    def test_valid_selection_displays_document(self):
        search_keyword(self.state, "accident timeline")
        with patch("cli.prompt_document_choice", return_value="DOC-001"):
            out = _captured_output(main.handle_read_action, self.state)
        self.assertIn("police report", out.lower())

    def test_empty_selection_shows_info(self):
        search_keyword(self.state, "accident timeline")
        with patch("cli.prompt_document_choice", return_value=""):
            out = _captured_output(main.handle_read_action, self.state)
        self.assertIn("no document selected", out.lower())


class TestHandleCollectAction(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(0)
        search_keyword(self.state, "traffic camera footage")

    def test_no_unlocked_docs_shows_info(self):
        state = _make_state(0)
        state.unlocked_document_ids.clear()
        out = _captured_output(main.handle_collect_action, state)
        self.assertIn("you have not unlocked", out.lower())

    def test_collecting_evidence_adds_to_state(self):
        with patch("cli.prompt_document_choice", return_value="DOC-004"):
            with patch("cli.prompt_evidence_ids", return_value=["EV-CAM"]):
                with patch("sys.stdout", io.StringIO()):
                    main.handle_collect_action(self.state)
        self.assertIn("EV-CAM", self.state.collected_evidence_ids)

    def test_empty_evidence_selection_shows_info(self):
        with patch("cli.prompt_document_choice", return_value="DOC-004"):
            with patch("cli.prompt_evidence_ids", return_value=[]):
                out = _captured_output(main.handle_collect_action, self.state)
        self.assertIn("no evidence selected", out.lower())

    def test_empty_document_selection_shows_info(self):
        with patch("cli.prompt_document_choice", return_value=""):
            out = _captured_output(main.handle_collect_action, self.state)
        self.assertIn("no document selected", out.lower())


class TestHandleSubmitAction(unittest.TestCase):
    def test_correct_suspect_wins(self):
        state = _full_state(0)
        correct = state.case_data.solution.correct_suspect
        with patch("cli.prompt_suspect", return_value=correct):
            out = _captured_output(main.handle_submit_action, state)
        self.assertIn("win", out.lower())

    def test_wrong_suspect_loses(self):
        state = _full_state(0)
        wrong = [s for s in state.case_data.suspects
                 if s != state.case_data.solution.correct_suspect][0]
        with patch("cli.prompt_suspect", return_value=wrong):
            out = _captured_output(main.handle_submit_action, state)
        self.assertIn("lose", out.lower())

    def test_empty_suspect_cancels(self):
        state = _full_state(0)
        with patch("cli.prompt_suspect", return_value=""):
            out = _captured_output(main.handle_submit_action, state)
        self.assertIn("cancelled", out.lower())

    def test_no_evidence_shows_info(self):
        state = _make_state(0)
        correct = state.case_data.solution.correct_suspect
        with patch("cli.prompt_suspect", return_value=correct):
            out = _captured_output(main.handle_submit_action, state)
        self.assertIn("you have not collected", out.lower())

    def test_game_over_set_after_submit(self):
        state = _full_state(0)
        correct = state.case_data.solution.correct_suspect
        with patch("cli.prompt_suspect", return_value=correct):
            with patch("sys.stdout", io.StringIO()):
                main.handle_submit_action(state)
        self.assertTrue(is_game_over(state))


class TestCommandLoop(unittest.TestCase):
    def _run_commands(self, commands, case_index=0):
        commands_iter = iter(commands + ["quit"])
        with patch("cli.display_case_select", return_value=case_index):
            with patch("cli.prompt_main_menu_action", side_effect=commands_iter):
                with patch("sys.stdout", io.StringIO()):
                    try:
                        main.run_game()
                    except SystemExit:
                        pass

    def test_quit_exits_cleanly(self):
        try:
            self._run_commands([])
        except Exception as e:
            self.fail(f"quit raised: {e}")

    def test_help_command_does_not_crash(self):
        try:
            self._run_commands(["h"])
        except Exception as e:
            self.fail(f"help raised: {e}")

    def test_unknown_command_does_not_crash(self):
        try:
            self._run_commands(["zzz_invalid"])
        except Exception as e:
            self.fail(f"Unknown command raised: {e}")

    def test_blank_input_does_not_crash(self):
        try:
            self._run_commands(["", ""])
        except Exception as e:
            self.fail(f"Blank input raised: {e}")

    def test_status_command_does_not_crash(self):
        try:
            self._run_commands(["st"])
        except Exception as e:
            self.fail(f"status raised: {e}")

    def test_search_shorthand_works(self):
        with patch("cli.display_case_select", return_value=0):
            with patch("cli.prompt_main_menu_action", side_effect=["s", "quit"]):
                with patch("cli.prompt_keyword", return_value="accident timeline"):
                    with patch("sys.stdout", io.StringIO()):
                        try:
                            main.run_game()
                        except SystemExit:
                            pass

    def test_all_four_cases_launch_without_error(self):
        for i in range(4):
            try:
                self._run_commands([], case_index=i)
            except Exception as e:
                self.fail(f"Case {i} failed to launch: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
