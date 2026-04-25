"""Tests for cli.py — display functions, prompt functions, input handling."""

import io
import unittest
from unittest.mock import patch

from data import build_demo_case, ALL_CASES
from game_engine import create_new_game, search_keyword, read_document, \
    collect_evidence_from_document
import cli


def _captured_output(func, *args, **kwargs):
    """Run func and return its stdout as a string."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        func(*args, **kwargs)
    return buf.getvalue()


def _make_state(case_index=0):
    return create_new_game(build_demo_case(case_index))


class TestDisplayWelcome(unittest.TestCase):
    def test_prints_title(self):
        out = _captured_output(cli.display_welcome, build_demo_case(0))
        self.assertIn("HIT AND RUN", out.upper())

    def test_prints_intro_text(self):
        out = _captured_output(cli.display_welcome, build_demo_case(0))
        self.assertIn("hit-and-run", out.lower())

    def test_prints_help_hint(self):
        out = _captured_output(cli.display_welcome, build_demo_case(0))
        self.assertIn("help", out.lower())


class TestDisplayHelp(unittest.TestCase):
    def test_prints_all_commands(self):
        out = _captured_output(cli.display_help)
        for cmd in ["search", "read", "collect", "status", "submit", "quit"]:
            self.assertIn(cmd, out.lower())


class TestDisplayStatus(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(0)

    def test_shows_available_keywords(self):
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("accident timeline", out.lower())

    def test_shows_no_documents_when_none_unlocked(self):
        self.state.unlocked_document_ids.clear()
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("no documents unlocked", out.lower())

    def test_shows_unlocked_document_titles(self):
        search_keyword(self.state, "accident timeline")
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("police report", out.lower())

    def test_shows_no_evidence_when_none_collected(self):
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("no evidence collected", out.lower())

    def test_shows_collected_evidence_ids(self):
        search_keyword(self.state, "traffic camera footage")
        collect_evidence_from_document(self.state, "DOC-004", ["EV-CAM"])
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("EV-CAM", out)

    def test_shows_used_keywords(self):
        search_keyword(self.state, "accident timeline")
        out = _captured_output(cli.display_status, self.state)
        self.assertIn("accident timeline", out.lower())


class TestDisplaySearchResults(unittest.TestCase):
    def test_prints_message(self):
        out = _captured_output(cli.display_search_results, [], "No results found.")
        self.assertIn("no results found", out.lower())

    def test_prints_document_titles_when_unlocked(self):
        case = build_demo_case(0)
        docs = [d for d in case.documents if d.document_id == "DOC-001"]
        out = _captured_output(cli.display_search_results, docs, "Unlocked 1 document.")
        self.assertIn("police report", out.lower())

    def test_no_document_list_when_empty(self):
        out = _captured_output(cli.display_search_results, [], "No results.")
        self.assertNotIn("newly unlocked", out.lower())


class TestDisplayDocument(unittest.TestCase):
    def setUp(self):
        self.state = _make_state(0)
        search_keyword(self.state, "accident timeline")
        self.doc = read_document(self.state, "DOC-001")

    def test_prints_title(self):
        out = _captured_output(cli.display_document, self.doc)
        self.assertIn("police report", out.lower())

    def test_prints_document_text(self):
        out = _captured_output(cli.display_document, self.doc)
        self.assertIn("fulton", out.lower())

    def test_prints_evidence_items(self):
        out = _captured_output(cli.display_document, self.doc)
        self.assertIn("EV-POL", out)

    def test_marks_key_evidence(self):
        state = _make_state(0)
        search_keyword(state, "traffic camera footage")
        doc = read_document(state, "DOC-004")
        out = _captured_output(cli.display_document, doc)
        self.assertIn("KEY", out.upper())


class TestDisplaySubmissionResult(unittest.TestCase):
    def test_win_message(self):
        out = _captured_output(cli.display_submission_result, True, "Case solved.")
        self.assertIn("win", out.lower())

    def test_loss_message(self):
        out = _captured_output(cli.display_submission_result, False, "Case not solved.")
        self.assertIn("lose", out.lower())

    def test_prints_result_message(self):
        out = _captured_output(cli.display_submission_result, True, "You got it right.")
        self.assertIn("you got it right", out.lower())


class TestDisplayCaseSelect(unittest.TestCase):
    def test_prints_all_case_names(self):
        with patch("builtins.input", return_value="1"):
            out = _captured_output(cli.display_case_select, ALL_CASES)
        for name in ALL_CASES:
            self.assertIn(name, out)

    def test_returns_correct_index(self):
        with patch("builtins.input", return_value="3"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.display_case_select(ALL_CASES)
        self.assertEqual(result, 2)

    def test_rejects_invalid_then_accepts_valid(self):
        with patch("builtins.input", side_effect=["9", "0", "2"]):
            with patch("sys.stdout", io.StringIO()):
                result = cli.display_case_select(ALL_CASES)
        self.assertEqual(result, 1)


class TestPrompts(unittest.TestCase):
    def test_prompt_main_menu_action_lowercases(self):
        with patch("builtins.input", return_value="SEARCH"):
            result = cli.prompt_main_menu_action()
        self.assertEqual(result, "search")

    def test_prompt_main_menu_action_strips_whitespace(self):
        with patch("builtins.input", return_value="  s  "):
            result = cli.prompt_main_menu_action()
        self.assertEqual(result, "s")

    def test_prompt_main_menu_action_returns_quit_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            result = cli.prompt_main_menu_action()
        self.assertEqual(result, "quit")

    def test_prompt_keyword_returns_input(self):
        with patch("builtins.input", return_value="accident timeline"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_keyword()
        self.assertEqual(result, "accident timeline")

    def test_prompt_keyword_returns_empty_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_keyword()
        self.assertEqual(result, "")

    def test_prompt_document_choice_returns_correct_id(self):
        docs = build_demo_case(0).documents[:3]
        with patch("builtins.input", return_value="2"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_document_choice(docs)
        self.assertEqual(result, docs[1].document_id)

    def test_prompt_document_choice_empty_input_returns_empty(self):
        docs = build_demo_case(0).documents[:3]
        with patch("builtins.input", return_value=""):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_document_choice(docs)
        self.assertEqual(result, "")

    def test_prompt_document_choice_invalid_number_returns_empty(self):
        docs = build_demo_case(0).documents[:3]
        with patch("builtins.input", return_value="99"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_document_choice(docs)
        self.assertEqual(result, "")

    def test_prompt_evidence_ids_returns_evidence_id_by_number(self):
        items = build_demo_case(0).documents[0].evidence_items
        with patch("builtins.input", return_value="1"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_evidence_ids(items)
        self.assertEqual(result, [items[0].evidence_id])

    def test_prompt_evidence_ids_returns_empty_when_no_items(self):
        with patch("sys.stdout", io.StringIO()):
            result = cli.prompt_evidence_ids([])
        self.assertEqual(result, [])

    def test_prompt_evidence_ids_handles_selection(self):
        items = build_demo_case(1).documents[0].evidence_items
        with patch("builtins.input", return_value="1"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_evidence_ids(items)
        self.assertIn(items[0].evidence_id, result)

    def test_prompt_suspect_returns_typed_name(self):
        with patch("builtins.input", return_value="Tyler Smith"):
            with patch("sys.stdout", io.StringIO()):
                result = cli.prompt_suspect(build_demo_case(0))
        self.assertEqual(result, "Tyler Smith")

    def test_print_error_contains_message(self):
        out = _captured_output(cli.print_error, "Something went wrong.")
        self.assertIn("something went wrong", out.lower())

    def test_print_info_contains_message(self):
        out = _captured_output(cli.print_info, "Here is some info.")
        self.assertIn("here is some info", out.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
