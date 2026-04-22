"""Tests for cli.py — File Not Found terminal demo.

Run with:
    python -m unittest test_cli -v

Coverage:
  display_welcome, display_help, display_status, display_search_results,
  display_document, display_submission_result, print_error, print_info,
  prompt_main_menu_action, prompt_keyword, prompt_document_choice,
  prompt_evidence_ids, prompt_suspect
"""

from __future__ import annotations

import unittest
from unittest.mock import patch


from models import CaseData, CaseSolution, Document, EvidenceItem, GameState
import cli


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


def printed(mock_print):
    """Flatten all print() call args into one string for easy assertions."""
    return " ".join(str(a) for c in mock_print.call_args_list for a in c.args)


# ─────────────────────────────────────────────────────────────────────────────
# display_welcome
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplayWelcome(unittest.TestCase):
    """display_welcome should print the game name, case title, and intro text."""

    def _run(self, case):
        with patch("builtins.print") as mp:
            cli.display_welcome(case)
        return printed(mp)

    def test_prints_game_name(self):
        self.assertIn("FILE NOT FOUND", self._run(make_case()).upper())

    def test_prints_case_title(self):
        self.assertIn("HIT AND RUN", self._run(make_case(title="Hit and Run")).upper())

    def test_prints_intro_text(self):
        self.assertIn("Fulton", self._run(make_case()))

    def test_mentions_help_command(self):
        self.assertIn("help", self._run(make_case()).lower())


# ─────────────────────────────────────────────────────────────────────────────
# display_help
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplayHelp(unittest.TestCase):
    """display_help should list all valid game commands."""

    def _run(self):
        with patch("builtins.print") as mp:
            cli.display_help()
        return printed(mp).lower()

    def test_shows_search_command(self):
        self.assertIn("search", self._run())

    def test_shows_read_command(self):
        self.assertIn("read", self._run())

    def test_shows_collect_command(self):
        self.assertIn("collect", self._run())

    def test_shows_submit_command(self):
        self.assertIn("submit", self._run())

    def test_shows_status_command(self):
        self.assertIn("status", self._run())

    def test_shows_quit_command(self):
        self.assertIn("quit", self._run())

    def test_shows_help_command(self):
        self.assertIn("help", self._run())


# ─────────────────────────────────────────────────────────────────────────────
# display_status
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplayStatus(unittest.TestCase):
    """display_status should summarise keywords, documents, and evidence."""

    def _run(self, state):
        with patch("builtins.print") as mp:
            cli.display_status(state)
        return printed(mp)

    def test_shows_available_keyword(self):
        state = make_state(available_keywords=["accident timeline"])
        self.assertIn("accident timeline", self._run(state))

    def test_shows_unlocked_document_id(self):
        doc = make_document(doc_id="DOC-001", is_unlocked=True)
        case = make_case(documents=[doc])
        state = make_state(case=case, unlocked=["DOC-001"])
        self.assertIn("DOC-001", self._run(state))

    def test_shows_collected_evidence(self):
        state = make_state(collected=["EV-001"])
        self.assertIn("EV-001", self._run(state))

    def test_no_documents_message_when_none_unlocked(self):
        self.assertIn("no", self._run(make_state(unlocked=[])).lower())

    def test_no_evidence_message_when_none_collected(self):
        self.assertIn("no", self._run(make_state(collected=[])).lower())


# ─────────────────────────────────────────────────────────────────────────────
# display_search_results
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplaySearchResults(unittest.TestCase):
    """display_search_results should print the message and any new documents."""

    def _run(self, documents, message):
        with patch("builtins.print") as mp:
            cli.display_search_results(documents, message)
        return printed(mp)

    def test_prints_message(self):
        self.assertIn("No results", self._run([], "No results matched that keyword."))

    def test_prints_new_document_id(self):
        doc = make_document(doc_id="DOC-004", title="Traffic Camera Footage")
        self.assertIn("DOC-004", self._run([doc], "Unlocked 1 new document."))

    def test_prints_document_title(self):
        doc = make_document(title="Traffic Camera Footage")
        self.assertIn("Traffic Camera Footage", self._run([doc], "Unlocked 1 new document."))

    def test_empty_document_list_shows_only_message(self):
        self.assertIn("No new documents", self._run([], "No new documents."))


# ─────────────────────────────────────────────────────────────────────────────
# display_document
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplayDocument(unittest.TestCase):
    """display_document should print title, text, and all evidence items."""

    def _run(self, document):
        with patch("builtins.print") as mp:
            cli.display_document(document)
        return printed(mp)

    def test_prints_title(self):
        # _header() uppercases the title
        self.assertIn("SERVER LOGS", self._run(make_document(title="Server Logs")).upper())

    def test_prints_document_id(self):
        self.assertIn("DOC-001", self._run(make_document(doc_id="DOC-001")))

    def test_prints_document_text(self):
        self.assertIn("Login at 03:00", self._run(make_document(text="Login at 03:00 from unknown IP.")))

    def test_prints_evidence_label(self):
        doc = make_document(evidence_items=[make_evidence(label="Deleted Log")])
        self.assertIn("Deleted Log", self._run(doc))

    def test_prints_evidence_id(self):
        doc = make_document(evidence_items=[make_evidence(ev_id="EV-007")])
        self.assertIn("EV-007", self._run(doc))

    def test_key_evidence_marked(self):
        doc = make_document(evidence_items=[make_evidence(is_key=True)])
        self.assertIn("KEY", self._run(doc).upper())

    def test_no_evidence_items_shows_message(self):
        self.assertIn("no", self._run(make_document(evidence_items=[])).lower())


# ─────────────────────────────────────────────────────────────────────────────
# display_submission_result
# ─────────────────────────────────────────────────────────────────────────────

class TestDisplaySubmissionResult(unittest.TestCase):
    """display_submission_result should clearly show win or loss."""

    def _run(self, player_won, message):
        with patch("builtins.print") as mp:
            cli.display_submission_result(player_won, message)
        return printed(mp)

    def test_win_message_shown(self):
        output = self._run(True, "Case solved.")
        self.assertTrue(
            any(w in output.upper() for w in ("WIN", "CLOSED", "SOLVED")),
            f"Expected win indicator in: {output!r}"
        )

    def test_loss_message_shown(self):
        output = self._run(False, "Case not solved.")
        self.assertTrue(
            any(w in output.upper() for w in ("LOSE", "LOST", "DISMISSED", "FAIL")),
            f"Expected loss indicator in: {output!r}"
        )

    def test_message_text_printed(self):
        self.assertIn("incorrect", self._run(False, "The suspect you named was incorrect."))

    def test_win_and_loss_outputs_differ(self):
        self.assertNotEqual(self._run(True, "Good job."), self._run(False, "Good job."))


# ─────────────────────────────────────────────────────────────────────────────
# print_error / print_info
# ─────────────────────────────────────────────────────────────────────────────

class TestPrintHelpers(unittest.TestCase):
    """print_error and print_info should output clearly marked messages."""

    def test_print_error_includes_message(self):
        with patch("builtins.print") as mp:
            cli.print_error("Something went wrong.")
        self.assertIn("Something went wrong", printed(mp))

    def test_print_info_includes_message(self):
        with patch("builtins.print") as mp:
            cli.print_info("Just so you know.")
        self.assertIn("Just so you know", printed(mp))

    def test_print_error_has_visual_marker(self):
        with patch("builtins.print") as mp:
            cli.print_error("Oops.")
        output = printed(mp)
        self.assertTrue(
            any(m in output for m in ("!", "[", "ERROR", "error")),
            f"No error marker found in: {output!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# prompt_main_menu_action
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptMainMenuAction(unittest.TestCase):
    """prompt_main_menu_action should return lowercased, stripped user input."""

    def test_returns_lowercased_input(self):
        with patch("builtins.input", return_value="Search"):
            self.assertEqual(cli.prompt_main_menu_action(), "search")

    def test_strips_whitespace(self):
        with patch("builtins.input", return_value="  read  "):
            self.assertEqual(cli.prompt_main_menu_action(), "read")

    def test_returns_quit_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(cli.prompt_main_menu_action(), "quit")

    def test_returns_quit_on_keyboard_interrupt(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            self.assertEqual(cli.prompt_main_menu_action(), "quit")

    def test_empty_string_returned_as_empty(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(cli.prompt_main_menu_action(), "")


# ─────────────────────────────────────────────────────────────────────────────
# prompt_keyword
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptKeyword(unittest.TestCase):
    """prompt_keyword should return the raw stripped user input."""

    def test_returns_input_text(self):
        with patch("builtins.input", return_value="traffic camera footage"):
            self.assertEqual(cli.prompt_keyword(), "traffic camera footage")

    def test_strips_whitespace(self):
        with patch("builtins.input", return_value="  server logs  "):
            self.assertEqual(cli.prompt_keyword(), "server logs")

    def test_returns_empty_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(cli.prompt_keyword(), "")

    def test_prints_prompt_before_input(self):
        with patch("builtins.print") as mp, patch("builtins.input", return_value="x"):
            cli.prompt_keyword()
        self.assertTrue(mp.called, "prompt_keyword should print instructions before input")


# ─────────────────────────────────────────────────────────────────────────────
# prompt_document_choice
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptDocumentChoice(unittest.TestCase):
    """prompt_document_choice should return a document_id or empty string."""

    def _docs(self):
        return [
            make_document(doc_id="DOC-001", title="Police Report"),
            make_document(doc_id="DOC-002", title="Witness Statement"),
        ]

    def test_valid_choice_returns_document_id(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "DOC-001")

    def test_second_choice_returns_second_id(self):
        with patch("builtins.input", return_value="2"):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "DOC-002")

    def test_empty_input_returns_empty_string(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "")

    def test_non_numeric_input_returns_empty_string(self):
        with patch("builtins.input", return_value="abc"):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "")

    def test_out_of_range_returns_empty_string(self):
        with patch("builtins.input", return_value="99"):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "")

    def test_eof_returns_empty_string(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(cli.prompt_document_choice(self._docs()), "")

    def test_document_titles_are_printed(self):
        with patch("builtins.print") as mp, patch("builtins.input", return_value="1"):
            cli.prompt_document_choice(self._docs())
        output = printed(mp)
        self.assertIn("Police Report", output)
        self.assertIn("Witness Statement", output)


# ─────────────────────────────────────────────────────────────────────────────
# prompt_evidence_ids
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptEvidenceIds(unittest.TestCase):
    """prompt_evidence_ids should return a list of chosen evidence IDs."""

    def _items(self):
        return [
            make_evidence(ev_id="EV-001", label="Camera Footage"),
            make_evidence(ev_id="EV-002", label="Repair Receipt"),
        ]

    def test_single_valid_choice(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(cli.prompt_evidence_ids(self._items()), ["EV-001"])

    def test_comma_separated_choices(self):
        with patch("builtins.input", return_value="1,2"):
            result = cli.prompt_evidence_ids(self._items())
        self.assertIn("EV-001", result)
        self.assertIn("EV-002", result)

    def test_space_separated_choices(self):
        with patch("builtins.input", return_value="1 2"):
            result = cli.prompt_evidence_ids(self._items())
        self.assertIn("EV-001", result)
        self.assertIn("EV-002", result)

    def test_empty_input_returns_empty_list(self):
        with patch("builtins.input", return_value=""):
            self.assertEqual(cli.prompt_evidence_ids(self._items()), [])

    def test_eof_returns_empty_list(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(cli.prompt_evidence_ids(self._items()), [])

    def test_no_items_returns_empty_list(self):
        self.assertEqual(cli.prompt_evidence_ids([]), [])

    def test_none_items_returns_empty_list(self):
        self.assertEqual(cli.prompt_evidence_ids(None), [])

    def test_out_of_range_number_ignored(self):
        with patch("builtins.input", return_value="99"):
            self.assertEqual(cli.prompt_evidence_ids(self._items()), [])

    def test_evidence_labels_printed(self):
        items = self._items()
        with patch("builtins.print") as mp, patch("builtins.input", return_value="1"):
            cli.prompt_evidence_ids(items)
        self.assertIn("Camera Footage", printed(mp))


# ─────────────────────────────────────────────────────────────────────────────
# prompt_suspect
# ─────────────────────────────────────────────────────────────────────────────

class TestPromptSuspect(unittest.TestCase):
    """prompt_suspect should display suspects and return the player's input."""

    def _case(self):
        return make_case(suspects=["Tyler Smith", "Emily Carter", "Marcus Webb"])

    def test_returns_typed_suspect_name(self):
        with patch("builtins.input", return_value="Tyler Smith"):
            self.assertEqual(cli.prompt_suspect(self._case()), "Tyler Smith")

    def test_returns_empty_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(cli.prompt_suspect(self._case()), "")

    def test_suspect_list_is_printed(self):
        with patch("builtins.print") as mp, patch("builtins.input", return_value="Tyler Smith"):
            cli.prompt_suspect(self._case())
        output = printed(mp)
        self.assertIn("Tyler Smith", output)
        self.assertIn("Emily Carter", output)
        self.assertIn("Marcus Webb", output)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
