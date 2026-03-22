"""Core game flow for the File Not Found demo.

This module should coordinate state changes and call validation helpers.
It should not directly handle user-facing formatting beyond returning useful
results to the CLI layer.
"""

from __future__ import annotations

from models import CaseData, Document, GameState


def create_new_game(case_data: CaseData) -> GameState:
    """Create and return a fresh game state for a new play session.

    This should copy the starting keywords into the game state and reset all
    progress tracking fields.
    """
    pass


def search_keyword(state: GameState, keyword: str) -> tuple[list[Document], str]:
    """Process one keyword search and return new documents plus a status message.

    This should validate the input, find matching documents, unlock newly found
    ones, add discovered keywords, and return a user-friendly result message.
    """
    pass


def add_discovered_keywords(state: GameState, documents: list[Document]) -> None:
    """Add new keywords revealed by newly unlocked documents.

    This should update the player's available keyword set.
    """
    pass


def get_unlocked_documents(state: GameState) -> list[Document]:
    """Return all documents currently unlocked by the player.

    This should be used by the CLI when showing the readable document list.
    """
    pass


def read_document(state: GameState, document_id: str) -> Document | None:
    """Return the requested unlocked document, if it is available to read.

    This should prevent the player from reading documents that are still
    locked.
    """
    pass


def collect_evidence_from_document(
    state: GameState,
    document_id: str,
    evidence_ids: list[str],
) -> tuple[bool, str]:
    """Collect one or more evidence items from a document.

    This should verify that the document is unlocked and that each evidence
    item belongs to that document before updating the game state.
    """
    pass


def submit_case_answer(
    state: GameState,
    suspect_name: str,
    evidence_ids: set[str],
) -> tuple[bool, str]:
    """Evaluate the player's suspect and evidence submission.

    This should call the validation logic, set game-over fields, and return a
    message that explains the outcome.
    """
    pass


def is_game_over(state: GameState) -> bool:
    """Return True when the current game has already ended.

    This should help the main loop decide when to stop asking for actions.
    """
    pass
