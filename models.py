"""Domain models for the File Not Found demo game.

This module should contain the core data structures used by the rest of the
project. Keep this file focused on data and model-related helper methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceItem:
    """Represent one piece of evidence the player can collect."""

    evidence_id: str
    label: str
    description: str
    source_document_id: str
    is_key_evidence: bool = False


@dataclass(slots=True)
class Document:
    """Represent one in-game document that can be unlocked and read."""

    document_id: str
    title: str
    text: str
    unlock_keywords: list[str] = field(default_factory=list)
    discovered_keywords: list[str] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    is_unlocked: bool = False

    def matches_keyword(self, keyword: str) -> bool:
        """Return True when the given keyword unlocks this document.

        This should perform the keyword comparison logic used by the game
        search flow.
        """
        pass

    def get_evidence_by_id(self, evidence_id: str) -> EvidenceItem | None:
        """Return the matching evidence item from this document, if present.

        This should help the engine find evidence inside a document without
        duplicating lookup logic in multiple places.
        """
        pass


@dataclass(slots=True)
class CaseSolution:
    """Represent the correct suspect and evidence required to win."""

    correct_suspect: str
    required_evidence_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class CaseData:
    """Represent all static data needed to run one case."""

    title: str
    intro_text: str
    suspects: list[str] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    starting_keywords: list[str] = field(default_factory=list)
    solution: CaseSolution | None = None

    def get_document_by_id(self, document_id: str) -> Document | None:
        """Return the document with the given ID, if it exists.

        This should provide one standard way to retrieve a document from the
        case data.
        """
        pass


@dataclass(slots=True)
class GameState:
    """Track the current player progress for the active play session."""

    case_data: CaseData
    available_keywords: set[str] = field(default_factory=set)
    used_keywords: set[str] = field(default_factory=set)
    unlocked_document_ids: set[str] = field(default_factory=set)
    collected_evidence_ids: set[str] = field(default_factory=set)
    selected_suspect: str | None = None
    game_over: bool = False
    player_won: bool = False

    def mark_keyword_used(self, keyword: str) -> None:
        """Store a keyword in the set of already-used keywords.

        This should update the game state after a search attempt.
        """
        pass

    def unlock_document(self, document_id: str) -> None:
        """Mark a document as unlocked in the current game state.

        This should update both the state tracking and any related document
        status if needed.
        """
        pass

    def collect_evidence(self, evidence_id: str) -> None:
        """Add an evidence item to the player's collected evidence set.

        This should prevent duplicates and keep state updates in one place.
        """
        pass
