"""Entry point for the File Not Found.

Wires together case data, engine logic, and terminal UI.
Stays small and focused on program startup and the main command loop.
"""

from __future__ import annotations

import sys

from data import build_demo_case, ALL_CASES
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

    cli.print_info("Choose a document to read:")
    doc_id = cli.prompt_document_choice(unlocked)
    if not doc_id:
        cli.print_info("No document selected.")
        return

    document = read_document(state, doc_id)
    if document is None:
        cli.print_error(f"Could not load document '{doc_id}'.")
        return

    cli.display_document(document)


def handle_collect_action(state: GameState) -> None:
    """Run the evidence-collection interaction for one turn."""
    unlocked = get_unlocked_documents(state)
    if not unlocked:
        cli.print_info("You have not unlocked any documents yet. Try searching first.")
        return

    cli.print_info("Choose a document to collect evidence from:")
    doc_id = cli.prompt_document_choice(unlocked)
    if not doc_id:
        cli.print_info("No document selected.")
        return

    # Show the document so the player can see the evidence IDs
    document = read_document(state, doc_id)
    if document is None:
        cli.print_error(f"Could not load document '{doc_id}'.")
        return

    cli.display_document(document)

    evidence_ids = cli.prompt_evidence_ids(document.evidence_items)
    if not evidence_ids:
        cli.print_info("No evidence selected. Nothing collected.")
        return

    success, message = collect_evidence_from_document(state, doc_id, evidence_ids)
    if success:
        cli.print_info(message)
    else:
        cli.print_error(message)


def handle_submit_action(state: GameState) -> None:
    """Run the final accusation and evidence-submission flow.

    All collected evidence is submitted automatically — the engine's
    validate_submission call is what determines the win/loss outcome, and
    build_submission already filters out anything not in collected_evidence_ids,
    so there is no reason to ask the player to re-type IDs they already have.
    """
    if not state.collected_evidence_ids:
        cli.print_info(
            "You have not collected any evidence yet. "
            "Use  collect  to gather evidence before submitting."
        )

    suspect = cli.prompt_suspect(state.case_data)
    if not suspect:
        cli.print_error("No suspect entered. Submission cancelled.")
        return

    # Submit everything collected — the engine rejects any that don't satisfy
    # the solution's required_evidence_ids automatically.
    player_won, message = submit_case_answer(
        state, suspect, set(state.collected_evidence_ids)
    )
    cli.display_submission_result(player_won, message)


# ── Main game loop ────────────────────────────────────────────────────────────


def run_game() -> None:
    """Start the demo and keep the command loop running until the game ends."""
    case_index = cli.display_case_select(ALL_CASES)
    case_data = build_demo_case(case_index)
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
