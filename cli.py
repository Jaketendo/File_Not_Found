"""Command-line interface helpers for the File Not Found demo.

This module should handle all printing and user input for the terminal demo.
Keep display logic here so the engine stays focused on game rules.
"""

from __future__ import annotations

from models import CaseData, Document, GameState


def display_welcome(case_data: CaseData) -> None:
    """Print the game title and introduction text to the terminal.

    This should give the player enough context to start the case.
    """
    pass


def display_help() -> None:
    """Print the available commands and what each one does.

    This should be shown at the start and whenever the player asks for help.
    """
    pass


def display_status(state: GameState) -> None:
    """Print a summary of the player's current progress.

    This should show useful information such as available keywords, unlocked
    documents, and collected evidence count.
    """
    pass


def display_search_results(documents: list[Document], message: str) -> None:
    """Print the outcome of a keyword search.

    This should show the engine message and list any newly unlocked documents.
    """
    pass


def display_document(document: Document) -> None:
    """Print the title, text, and evidence options for a document.

    This should make the document easy to read during the class demo.
    """
    pass


def display_submission_result(player_won: bool, message: str) -> None:
    """Print the final game result after case submission.

    This should clearly show whether the player won or lost and why.
    """
    pass


def prompt_main_menu_action() -> str:
    """Ask the player for the next action and return their choice.

    This should support the main command loop in the entry-point module.
    """
    pass


def prompt_keyword() -> str:
    """Ask the player to enter a keyword for searching.

    This should return the raw user input for the engine to process.
    """
    pass


def prompt_document_id() -> str:
    """Ask the player which document they want to open.

    This should return the chosen document ID.
    """
    pass


def prompt_evidence_ids() -> list[str]:
    """Ask the player which evidence items they want to collect or submit.

    This should support comma-separated or space-separated input.
    """
    pass


def prompt_suspect(case_data: CaseData) -> str:
    """Ask the player which suspect they want to accuse.

    This should display the suspect list before accepting input.
    """
    pass
