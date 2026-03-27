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
        """Return True when the given keyword unlocks this document."""
        return keyword in self.unlock_keywords

    def get_evidence_by_id(self, evidence_id: str) -> EvidenceItem | None:
        """Return the matching evidence item from this document, if present."""
        # BUG FIX: was `self.evidence_items[i.evidence_id]` — i is an int,
        # not an object. Also returns None implicitly when not found.
        for item in self.evidence_items:
            if evidence_id == item.evidence_id:
                return item
        return None


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
        """Return the document with the given ID, if it exists."""
        # BUG FIX: was comparing self.documents[i] (a Document object) to a
        # string, and had a typo self.doucuments[i] on the return.
        for doc in self.documents:
            if document_id == doc.document_id:
                return doc
        return None


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
        """Store a keyword in the set of already-used keywords."""
        # Was missing entirely from the original implementation.
        self.used_keywords.add(keyword)

    def unlock_document(self, document_id: str) -> None:
        """Mark a document as unlocked in the current game state."""
        # BUG FIX: was `Document.is_unlocked[document_id] = True` which tries
        # to subscript the class itself. Correct approach: add to the set and
        # also flip is_unlocked on the matching Document object.
        self.unlocked_document_ids.add(document_id)
        doc = self.case_data.get_document_by_id(document_id)
        if doc is not None:
            doc.is_unlocked = True

    def collect_evidence(self, evidence_id: str) -> None:
        """Add an evidence item to the player's collected evidence set."""
        # BUG FIX: collected_evidence_ids is a set, not a list. Can't index
        # into a set with [i] or append with +=. set.add() handles duplicates
        # automatically, so the manual duplicate-check loop is also removed.
        self.collected_evidence_ids.add(evidence_id)
