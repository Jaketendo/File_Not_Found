"""Entry point for the File Not Found terminal demo.

Wires together case data, engine logic, and terminal UI.
Stays small and focused on program startup and the main command loop.
"""

from __future__ import annotations

import sys

from data import build_demo_case
from game_engine import (
    collect_evidence_from_document,
    create_new_game,
    get_unlocked_documents,
    is_game_over,
    read_document,
    search_keyword,
    submit_case_answer,
)
from models import GameState
import cli


# ── Action handlers ───────────────────────────────────────────────────────────


def handle_search_action(state: GameState) -> None:
    """Run the full keyword-search interaction for one turn."""
    keyword = cli.prompt_keyword()
    if not keyword:
        cli.print_error("No keyword entered.")
        return
    new_docs, message = search_keyword(state, keyword)
    cli.display_search_results(new_docs, message)


def handle_read_action(state: GameState) -> None:
    """Run the document-reading interaction for one turn."""
    unlocked = get_unlocked_documents(state)
    if not unlocked:
        cli.print_info("You have not unlocked any documents yet. Try searching first.")
        return

    cli.print_info(
        "Unlocked documents: "
        + ", ".join(f"[{d.document_id}] {d.title}" for d in unlocked)
    )
    doc_id = cli.prompt_document_id()
    if not doc_id:
        cli.print_error("No document ID entered.")
        return

    document = read_document(state, doc_id)
    if document is None:
        cli.print_error(
            f"Document '{doc_id}' is not available. "
            "It may be locked or the ID may be incorrect."
        )
        return

    cli.display_document(document)


def handle_collect_action(state: GameState) -> None:
    """Run the evidence-collection interaction for one turn."""
    unlocked = get_unlocked_documents(state)
    if not unlocked:
        cli.print_info("You have not unlocked any documents yet. Try searching first.")
        return

    cli.print_info(
        "Unlocked documents: "
        + ", ".join(f"[{d.document_id}] {d.title}" for d in unlocked)
    )
    doc_id = cli.prompt_document_id()
    if not doc_id:
        cli.print_error("No document ID entered.")
        return

    # Show the document first so the player can see evidence IDs
    document = read_document(state, doc_id)
    if document is None:
        cli.print_error(
            f"Document '{doc_id}' is not available. "
            "It may be locked or the ID may be incorrect."
        )
        return

    cli.display_document(document)

    evidence_ids = cli.prompt_evidence_ids()
    if not evidence_ids:
        cli.print_info("No evidence IDs entered. Nothing collected.")
        return

    success, message = collect_evidence_from_document(state, doc_id, evidence_ids)
    if success:
        cli.print_info(message)
    else:
        cli.print_error(message)


def handle_submit_action(state: GameState) -> None:
    """Run the final accusation and evidence-submission flow."""
    cli.print_info(
        "You are about to submit your final answer. "
        "Make sure you have collected all key evidence first."
    )

    suspect = cli.prompt_suspect(state.case_data)
    if not suspect:
        cli.print_error("No suspect entered. Submission cancelled.")
        return

    if state.collected_evidence_ids:
        cli.print_info(
            "Your collected evidence: "
            + ", ".join(sorted(state.collected_evidence_ids))
        )
        submitted_raw = cli.prompt_evidence_ids()
        submitted_ids: set[str] = set(submitted_raw)
    else:
        cli.print_info("You have not collected any evidence.")
        submitted_ids = set()

    player_won, message = submit_case_answer(state, suspect, submitted_ids)
    cli.display_submission_result(player_won, message)


# ── Main game loop ────────────────────────────────────────────────────────────


def run_game() -> None:
    """Start the demo and keep the command loop running until the game ends."""
    case_data = build_demo_case()
    state = create_new_game(case_data)

    cli.display_welcome(case_data)
    cli.display_help()

    while not is_game_over(state):
        action = cli.prompt_main_menu_action()

        if action in ("search", "s"):
            handle_search_action(state)

        elif action in ("read", "r"):
            handle_read_action(state)

        elif action in ("collect", "c"):
            handle_collect_action(state)

        elif action in ("status", "st"):
            cli.display_status(state)

        elif action == "submit":
            handle_submit_action(state)

        elif action in ("help", "h", "?"):
            cli.display_help()

        elif action in ("quit", "q", "exit"):
            cli.print_info("Exiting the game. Goodbye.")
            sys.exit(0)

        elif action == "":
            pass  # blank input — just re-prompt

        else:
            cli.print_error(
                f"Unknown command: '{action}'. Type  help  to see available commands."
            )


if __name__ == "__main__":
    run_game()
