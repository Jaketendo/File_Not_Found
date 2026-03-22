"""Validation helpers for searches, evidence, and final case outcomes.

This module should contain pure logic helpers that are easy to test in
isolation. Avoid printing from this file so it stays reusable.
"""

from __future__ import annotations

from models import CaseData, Document, GameState


def normalize_text(value: str) -> str:
    """Normalize user input for safe internal comparisons.

    This should support case-insensitive matching for keywords and suspects.
    """
    pass


def find_matching_documents(case_data: CaseData, keyword: str) -> list[Document]:
    """Return all documents unlocked by the given keyword.

    This should search the case data and return every matching document.
    """
    pass


def filter_new_documents(state: GameState, documents: list[Document]) -> list[Document]:
    """Return only documents that have not already been unlocked.

    This should prevent the engine from treating old documents as newly found.
    """
    pass


def is_valid_keyword(state: GameState, keyword: str) -> bool:
    """Return True when the keyword is available to the player.

    This should check whether the player is allowed to search the keyword.
    """
    pass


def is_reused_keyword(state: GameState, keyword: str) -> bool:
    """Return True when the player already searched this keyword before.

    This should help the UI show a special reused-keyword message.
    """
    pass


def has_required_evidence(state: GameState) -> bool:
    """Return True when the player collected all evidence required to win.

    This should compare the player's evidence against the case solution.
    """
    pass


def is_correct_suspect(state: GameState, suspect_name: str) -> bool:
    """Return True when the submitted suspect is the correct one.

    This should compare the player's chosen suspect to the case solution.
    """
    pass


def evaluate_case_submission(
    state: GameState,
    suspect_name: str,
    submitted_evidence_ids: set[str],
) -> tuple[bool, str]:
    """Evaluate the final submission and return outcome plus explanation.

    The returned tuple should contain:
    1. whether the player won
    2. a message explaining why they won or lost
    """
    pass
