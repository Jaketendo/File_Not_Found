"""Game-state logic for the File Not Found terminal demo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal

from models import CaseData, Document, EvidenceItem, GameState
from validation import (
    ValidationResult,
    filter_new_documents,
    find_matching_documents,
    is_reused_keyword,
    is_valid_keyword,
    normalize_text,
    validate_submission,
)

SearchStatus = Literal[
    "success",
    "empty_input",
    "reused",
    "no_results",
    "no_new_documents",
]
EvidenceStatus = Literal[
    "success",
    "partial_success",
    "empty_selection",
    "already_collected",
    "invalid_document",
    "locked_document",
    "invalid_evidence",
]


@dataclass(slots=True)
class SearchResult:
    """Outcome of a keyword search."""

    status: SearchStatus
    message: str
    searched_keyword: str
    unlocked_documents: tuple[Document, ...] = ()
    discovered_keywords: tuple[str, ...] = ()


@dataclass(slots=True)
class EvidenceCollectionResult:
    """Outcome of an evidence collection attempt."""

    status: EvidenceStatus
    message: str
    document_id: str | None = None
    collected_evidence_ids: tuple[str, ...] = ()
    already_collected_evidence_ids: tuple[str, ...] = ()
    invalid_evidence_ids: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class CaseSubmission:
    """Final suspect and evidence package sent to validation."""

    suspect_id: str
    evidence_ids: frozenset[str] = field(default_factory=frozenset)
    rejected_evidence_ids: tuple[str, ...] = ()


class GameEngine:
    """Handles keyword search, document access, evidence, and submission."""

    def __init__(self, case_data: CaseData, state: GameState | None = None) -> None:
        self.case_data = case_data
        self.state = state if state is not None else create_new_game(case_data)

    @classmethod
    def from_state(cls, state: GameState) -> GameEngine:
        """Wrap an existing game state."""

        return cls(state.case_data, state)

    def get_case_summary(self) -> str:
        """Return the case intro text."""

        return _clean_text(self.case_data.intro_text)

    def get_suspects(self) -> list[str]:
        """Return the case suspect list."""

        return list(self.case_data.suspects)

    def get_available_keywords(self, include_used: bool = False) -> list[str]:
        """Return known keywords, optionally including used ones."""

        known_keywords = _ordered_unique_strings(self.state.available_keywords)
        if include_used:
            return sorted(known_keywords, key=normalize_text)

        return sorted(
            [
                keyword
                for keyword in known_keywords
                if _find_matching_string(self.state.used_keywords, keyword) is None
            ],
            key=normalize_text,
        )

    def get_used_keywords(self) -> list[str]:
        """Return the keywords already searched."""

        return sorted(
            _ordered_unique_strings(self.state.used_keywords),
            key=normalize_text,
        )

    def search_keyword(self, keyword: str) -> SearchResult:
        """Process one keyword search and update the state."""

        cleaned_keyword = _clean_text(keyword)
        if not cleaned_keyword:
            return SearchResult(
                status="empty_input",
                message="Enter a keyword before searching.",
                searched_keyword="",
            )

        searched_keyword = (
            _find_matching_string(self.state.available_keywords, cleaned_keyword)
            or cleaned_keyword
        )

        if is_reused_keyword(self.state, searched_keyword):
            return SearchResult(
                status="reused",
                message="That keyword has already been searched. Try a different lead.",
                searched_keyword=searched_keyword,
            )

        if not is_valid_keyword(self.state, searched_keyword):
            return SearchResult(
                status="no_results",
                message="No results matched that keyword.",
                searched_keyword=searched_keyword,
            )

        matching_documents = find_matching_documents(self.case_data, searched_keyword)
        self._mark_keyword_used(searched_keyword)

        if not matching_documents:
            return SearchResult(
                status="no_results",
                message="No results matched that keyword.",
                searched_keyword=searched_keyword,
            )

        new_documents = filter_new_documents(self.state, matching_documents)
        if not new_documents:
            return SearchResult(
                status="no_new_documents",
                message="That keyword is relevant, but it did not reveal any new documents.",
                searched_keyword=searched_keyword,
            )

        for document in new_documents:
            self._unlock_document(document)

        discovered_keywords = self._add_discovered_keywords(new_documents)
        return SearchResult(
            status="success",
            message=self._build_search_message(new_documents, discovered_keywords),
            searched_keyword=searched_keyword,
            unlocked_documents=tuple(new_documents),
            discovered_keywords=tuple(discovered_keywords),
        )

    def get_unlocked_documents(self) -> list[Document]:
        """Return every unlocked document."""

        return [
            document
            for document in self.case_data.documents
            if self._is_document_unlocked(document)
        ]

    def get_document(self, document_id: str | int) -> Document | None:
        """Return an unlocked document by ID."""

        document = self._find_document(document_id)
        if document is None or not self._is_document_unlocked(document):
            return None
        return document

    def get_collected_evidence(self) -> list[EvidenceItem]:
        """Return collected evidence in document order."""

        collected_items: list[EvidenceItem] = []
        for document in self.case_data.documents:
            for evidence_item in document.evidence_items:
                if _find_matching_string(
                    self.state.collected_evidence_ids,
                    evidence_item.evidence_id,
                ):
                    collected_items.append(evidence_item)

        return collected_items

    def collect_evidence(self, evidence_id: str | int) -> EvidenceCollectionResult:
        """Collect one evidence item from any unlocked document."""

        cleaned_evidence_id = _clean_text(evidence_id)
        if not cleaned_evidence_id:
            return EvidenceCollectionResult(
                status="empty_selection",
                message="Select at least one evidence item.",
            )

        document, evidence_item = self._find_unlocked_evidence(cleaned_evidence_id)
        if document is None or evidence_item is None:
            return EvidenceCollectionResult(
                status="invalid_evidence",
                message="That evidence item is not available from your unlocked documents.",
                invalid_evidence_ids=(cleaned_evidence_id,),
            )

        canonical_evidence_id = evidence_item.evidence_id
        if _find_matching_string(self.state.collected_evidence_ids, canonical_evidence_id):
            return EvidenceCollectionResult(
                status="already_collected",
                message="That evidence item has already been collected.",
                document_id=document.document_id,
                already_collected_evidence_ids=(canonical_evidence_id,),
            )

        self._collect_evidence(canonical_evidence_id)
        return EvidenceCollectionResult(
            status="success",
            message=f"Collected evidence: {canonical_evidence_id}.",
            document_id=document.document_id,
            collected_evidence_ids=(canonical_evidence_id,),
        )

    def collect_evidence_from_document(
        self,
        document_id: str | int,
        evidence_ids: Iterable[str] | str,
    ) -> EvidenceCollectionResult:
        """Collect one or more evidence items from a specific document."""

        document = self._find_document(document_id)
        cleaned_document_id = _clean_text(document_id)

        if document is None:
            return EvidenceCollectionResult(
                status="invalid_document",
                message="That document does not exist.",
                document_id=cleaned_document_id or None,
            )

        if not self._is_document_unlocked(document):
            return EvidenceCollectionResult(
                status="locked_document",
                message="You can only collect evidence from unlocked documents.",
                document_id=document.document_id,
            )

        requested_evidence_ids = _ordered_unique_strings(_as_value_list(evidence_ids))
        if not requested_evidence_ids:
            return EvidenceCollectionResult(
                status="empty_selection",
                message="Select at least one evidence item.",
                document_id=document.document_id,
            )

        evidence_lookup = {
            normalize_text(evidence_item.evidence_id): evidence_item.evidence_id
            for evidence_item in document.evidence_items
        }

        invalid_evidence_ids = [
            evidence_id
            for evidence_id in requested_evidence_ids
            if normalize_text(evidence_id) not in evidence_lookup
        ]
        if invalid_evidence_ids:
            invalid_text = ", ".join(invalid_evidence_ids)
            return EvidenceCollectionResult(
                status="invalid_evidence",
                message=(
                    "The selected evidence does not belong to this document: "
                    f"{invalid_text}."
                ),
                document_id=document.document_id,
                invalid_evidence_ids=tuple(invalid_evidence_ids),
            )

        collected_evidence_ids: list[str] = []
        already_collected_ids: list[str] = []
        for requested_id in requested_evidence_ids:
            canonical_id = evidence_lookup[normalize_text(requested_id)]
            if _find_matching_string(self.state.collected_evidence_ids, canonical_id):
                already_collected_ids.append(canonical_id)
                continue

            self._collect_evidence(canonical_id)
            collected_evidence_ids.append(canonical_id)

        message, status = self._build_evidence_message(
            collected_evidence_ids,
            already_collected_ids,
        )
        return EvidenceCollectionResult(
            status=status,
            message=message,
            document_id=document.document_id,
            collected_evidence_ids=tuple(collected_evidence_ids),
            already_collected_evidence_ids=tuple(already_collected_ids),
        )

    def build_submission(
        self,
        suspect_id: str,
        evidence_ids: Iterable[str] | str,
    ) -> CaseSubmission:
        """Keep only collected evidence for the final submission."""

        cleaned_suspect_id = _clean_text(suspect_id)
        requested_evidence_ids = _ordered_unique_strings(_as_value_list(evidence_ids))

        accepted_evidence_ids: list[str] = []
        rejected_evidence_ids: list[str] = []
        for evidence_id in requested_evidence_ids:
            canonical_id = _find_matching_string(self.state.collected_evidence_ids, evidence_id)
            if canonical_id is None:
                rejected_evidence_ids.append(evidence_id)
                continue
            accepted_evidence_ids.append(canonical_id)

        return CaseSubmission(
            suspect_id=cleaned_suspect_id,
            evidence_ids=frozenset(accepted_evidence_ids),
            rejected_evidence_ids=tuple(rejected_evidence_ids),
        )

    def submit_case(
        self,
        suspect_id: str,
        evidence_ids: Iterable[str] | str,
    ) -> ValidationResult:
        """Validate the final accusation and lock in the game result."""

        submission = self.build_submission(suspect_id, evidence_ids)
        result = validate_submission(
            submission.suspect_id,
            submission.evidence_ids,
            self.case_data,
        )

        if submission.rejected_evidence_ids:
            rejected_text = ", ".join(submission.rejected_evidence_ids)
            result.message = (
                f"{result.message} Ignored evidence that had not been collected: "
                f"{rejected_text}."
            )

        self.state.selected_suspect = submission.suspect_id or None
        self.state.game_over = True
        self.state.player_won = result.is_win
        return result

    def is_game_over(self) -> bool:
        """Check whether the case has already been submitted."""

        return bool(self.state.game_over)

    def _mark_keyword_used(self, keyword: str) -> None:
        canonical_keyword = _find_matching_string(self.state.available_keywords, keyword)
        self.state.used_keywords.add(canonical_keyword or _clean_text(keyword))

    def _unlock_document(self, document: Document) -> None:
        self.state.unlocked_document_ids.add(document.document_id)
        if hasattr(document, "is_unlocked"):
            document.is_unlocked = True

    def _collect_evidence(self, evidence_id: str) -> None:
        self.state.collected_evidence_ids.add(_clean_text(evidence_id))

    def _add_discovered_keywords(self, documents: list[Document]) -> list[str]:
        discovered_keywords: list[str] = []
        for document in documents:
            for keyword in document.discovered_keywords:
                cleaned_keyword = _clean_text(keyword)
                if not cleaned_keyword:
                    continue
                if _find_matching_string(self.state.available_keywords, cleaned_keyword):
                    continue
                self.state.available_keywords.add(cleaned_keyword)
                discovered_keywords.append(cleaned_keyword)

        return discovered_keywords

    def _find_document(self, document_id: str | int) -> Document | None:
        normalized_document_id = normalize_text(_clean_text(document_id))
        for document in self.case_data.documents:
            if normalize_text(document.document_id) == normalized_document_id:
                return document
        return None

    def _is_document_unlocked(self, document: Document) -> bool:
        return _find_matching_string(self.state.unlocked_document_ids, document.document_id) is not None

    def _find_unlocked_evidence(
        self,
        evidence_id: str,
    ) -> tuple[Document | None, EvidenceItem | None]:
        normalized_evidence_id = normalize_text(evidence_id)
        for document in self.get_unlocked_documents():
            for evidence_item in document.evidence_items:
                if normalize_text(evidence_item.evidence_id) == normalized_evidence_id:
                    return document, evidence_item
        return None, None

    def _build_search_message(
        self,
        new_documents: list[Document],
        discovered_keywords: list[str],
    ) -> str:
        document_labels = ", ".join(_get_document_label(document) for document in new_documents)
        if len(new_documents) == 1:
            message = f"Unlocked 1 new document: {document_labels}."
        else:
            message = f"Unlocked {len(new_documents)} new documents: {document_labels}."

        if discovered_keywords:
            keyword_text = ", ".join(discovered_keywords)
            message += f" New keywords discovered: {keyword_text}."

        return message

    def _build_evidence_message(
        self,
        collected_ids: list[str],
        already_collected_ids: list[str],
    ) -> tuple[str, EvidenceStatus]:
        if collected_ids and already_collected_ids:
            collected_text = ", ".join(collected_ids)
            duplicate_text = ", ".join(already_collected_ids)
            return (
                f"Collected evidence: {collected_text}. Already collected: {duplicate_text}.",
                "partial_success",
            )

        if collected_ids:
            collected_text = ", ".join(collected_ids)
            return f"Collected evidence: {collected_text}.", "success"

        duplicate_text = ", ".join(already_collected_ids)
        return (
            f"That evidence was already collected: {duplicate_text}.",
            "already_collected",
        )


def create_new_game(case_data: CaseData) -> GameState:
    """Build a fresh game state."""

    state = GameState(
        case_data=case_data,
        available_keywords=set(_ordered_unique_strings(case_data.starting_keywords)),
    )

    initially_unlocked_documents: list[Document] = []
    for document in case_data.documents:
        starts_unlocked = bool(getattr(document, "starts_unlocked", False))
        if hasattr(document, "is_unlocked"):
            document.is_unlocked = starts_unlocked
        if starts_unlocked:
            state.unlocked_document_ids.add(document.document_id)
            initially_unlocked_documents.append(document)

    if initially_unlocked_documents:
        GameEngine.from_state(state)._add_discovered_keywords(initially_unlocked_documents)

    return state


def search_keyword(state: GameState, keyword: str) -> tuple[list[Document], str]:
    """Search one keyword and return new documents plus a status message."""

    result = GameEngine.from_state(state).search_keyword(keyword)
    return list(result.unlocked_documents), result.message


def add_discovered_keywords(state: GameState, documents: list[Document]) -> None:
    """Add keywords revealed by newly unlocked documents."""

    GameEngine.from_state(state)._add_discovered_keywords(documents)


def get_unlocked_documents(state: GameState) -> list[Document]:
    """Return all unlocked documents."""

    return GameEngine.from_state(state).get_unlocked_documents()


def read_document(state: GameState, document_id: str) -> Document | None:
    """Return an unlocked document by ID."""

    return GameEngine.from_state(state).get_document(document_id)


def collect_evidence_from_document(
    state: GameState,
    document_id: str,
    evidence_ids: list[str],
) -> tuple[bool, str]:
    """Collect evidence from a specific document."""

    result = GameEngine.from_state(state).collect_evidence_from_document(
        document_id,
        evidence_ids,
    )
    return result.status in {"success", "partial_success"}, result.message


def submit_case_answer(
    state: GameState,
    suspect_name: str,
    evidence_ids: set[str],
) -> tuple[bool, str]:
    """Validate the player's final accusation."""

    result = GameEngine.from_state(state).submit_case(suspect_name, evidence_ids)
    return result.is_win, result.message


def is_game_over(state: GameState) -> bool:
    """Check whether the current session has ended."""

    return GameEngine.from_state(state).is_game_over()


def _as_value_list(value: Iterable[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (set, frozenset)):
        return sorted((str(item) for item in value), key=normalize_text)
    return [str(item) for item in value]


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _ordered_unique_strings(values: Iterable[object]) -> list[str]:
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned_value = _clean_text(value)
        normalized_value = normalize_text(cleaned_value)
        if not normalized_value or normalized_value in seen:
            continue
        seen.add(normalized_value)
        unique_values.append(cleaned_value)
    return unique_values


def _find_matching_string(values: Iterable[object], target: object) -> str | None:
    normalized_target = normalize_text(_clean_text(target))
    if not normalized_target:
        return None

    for value in values:
        cleaned_value = _clean_text(value)
        if normalize_text(cleaned_value) == normalized_target:
            return cleaned_value

    return None


def _get_document_label(document: Document) -> str:
    title = _clean_text(document.title)
    return title or _clean_text(document.document_id)


__all__ = [
    "CaseSubmission",
    "EvidenceCollectionResult",
    "GameEngine",
    "SearchResult",
    "add_discovered_keywords",
    "collect_evidence_from_document",
    "create_new_game",
    "get_unlocked_documents",
    "is_game_over",
    "read_document",
    "search_keyword",
    "submit_case_answer",
]
