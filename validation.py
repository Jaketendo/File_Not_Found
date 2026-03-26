"""Validation helpers for searches, evidence, and final case outcomes.

anyways so here are the assumptions i had to make about the data model to keep this module flexible and adaptable:
- ``CaseData`` exposes ``documents``, ``starting_keywords``, and ``solution``.
- ``Document`` exposes ``document_id``, ``unlock_keywords``, and
  ``evidence_items``.
- The case solution exposes ``correct_suspect`` and
  ``required_evidence_ids``.

The helper functions use small attribute fallbacks so the module stays easy to
adapt if teammates choose slightly different model field names.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from models import CaseData, Document, GameState

_DOCUMENT_COLLECTION_ATTRS = ("documents", "docs")
_DOCUMENT_ID_ATTRS = ("document_id", "doc_id", "id")
_DOCUMENT_KEYWORD_ATTRS = ("unlock_keywords", "keywords", "search_keywords")
_SOLUTION_ATTRS = ("solution", "case_solution", "answer")
_CORRECT_SUSPECT_ATTRS = (
    "correct_suspect",
    "correct_suspect_id",
    "correct_answer",
    "correct_suspect_name",
)
_REQUIRED_EVIDENCE_ATTRS = (
    "required_evidence_ids",
    "required_evidence",
    "key_evidence_ids",
)
_SUSPECT_VALUE_ATTRS = ("suspect_id", "id", "name", "label", "display_name")


@dataclass(slots=True)
class ValidationResult:
    """Describe the outcome of a final suspect and evidence submission."""

    is_win: bool
    suspect_correct: bool
    evidence_correct: bool
    missing_evidence_ids: tuple[str, ...] = ()
    submitted_suspect: str = ""
    correct_suspect: str = ""
    submitted_evidence_ids: frozenset[str] = field(default_factory=frozenset)
    required_evidence_ids: tuple[str, ...] = ()
    message: str = ""


def normalize_text(value: str) -> str:
    """Normalize user input for safe internal comparisons."""

    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())


def find_matching_documents(case_data: CaseData, keyword: str) -> list[Document]:
    """Return all documents unlocked by the given keyword."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return []

    matches: list[Document] = []
    for document in _get_documents(case_data):
        document_keywords = _as_iterable(
            _read_attr(document, _DOCUMENT_KEYWORD_ATTRS, default=[])
        )
        if any(normalize_text(str(item)) == normalized_keyword for item in document_keywords):
            matches.append(document)

    return matches


def filter_new_documents(
    state: GameState,
    documents: list[Document],
) -> list[Document]:
    """Return only documents that have not already been unlocked."""

    unlocked_ids = _normalized_string_set(getattr(state, "unlocked_document_ids", set()))
    return [
        document
        for document in documents
        if normalize_text(_get_document_id(document)) not in unlocked_ids
    ]


def is_valid_keyword(state: GameState, keyword: str) -> bool:
    """Return True when the keyword is available to the player."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    return any(
        normalize_text(str(item)) == normalized_keyword
        for item in getattr(state, "available_keywords", set())
    )


def is_reused_keyword(state: GameState, keyword: str) -> bool:
    """Return True when the player already searched this keyword before."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    return any(
        normalize_text(str(item)) == normalized_keyword
        for item in getattr(state, "used_keywords", set())
    )


def has_required_evidence(state: GameState) -> bool:
    """Return True when the player collected all evidence required to win."""

    if _get_solution(state.case_data) is None:
        return False

    required_evidence_ids = _get_required_evidence_ids(state.case_data)
    collected_evidence_ids = _normalized_string_set(
        getattr(state, "collected_evidence_ids", set())
    )
    return all(
        normalize_text(evidence_id) in collected_evidence_ids
        for evidence_id in required_evidence_ids
    )


def is_correct_suspect(state: GameState, suspect_name: str) -> bool:
    """Return True when the submitted suspect is the correct one."""

    correct_suspect = _get_correct_suspect(state.case_data)
    if not correct_suspect:
        return False
    return _suspects_match(suspect_name, correct_suspect)


def validate_submission(
    submitted_suspect_id: str,
    submitted_evidence_ids: Iterable[str] | str,
    case_data: CaseData,
) -> ValidationResult:
    """Validate the player's final accusation against the case solution."""

    submitted_suspect = _clean_text(submitted_suspect_id)
    submitted_evidence = _ordered_unique_strings(_as_iterable(submitted_evidence_ids))

    solution = _get_solution(case_data)
    correct_suspect = _get_correct_suspect(case_data)
    required_evidence = _get_required_evidence_ids(case_data)

    if solution is None or not correct_suspect:
        return ValidationResult(
            is_win=False,
            suspect_correct=False,
            evidence_correct=False,
            missing_evidence_ids=tuple(required_evidence),
            submitted_suspect=submitted_suspect,
            correct_suspect=correct_suspect,
            submitted_evidence_ids=frozenset(submitted_evidence),
            required_evidence_ids=tuple(required_evidence),
            message="The case solution is not configured, so submissions cannot be validated yet.",
        )

    submitted_evidence_lookup = _normalized_string_set(submitted_evidence)
    missing_evidence = tuple(
        evidence_id
        for evidence_id in required_evidence
        if normalize_text(evidence_id) not in submitted_evidence_lookup
    )

    suspect_correct = _suspects_match(submitted_suspect, correct_suspect)
    evidence_correct = not missing_evidence
    result = ValidationResult(
        is_win=suspect_correct and evidence_correct,
        suspect_correct=suspect_correct,
        evidence_correct=evidence_correct,
        missing_evidence_ids=missing_evidence,
        submitted_suspect=submitted_suspect,
        correct_suspect=correct_suspect,
        submitted_evidence_ids=frozenset(submitted_evidence),
        required_evidence_ids=tuple(required_evidence),
    )
    result.message = _build_validation_message(result)
    return result


def evaluate_case_submission(
    state: GameState,
    suspect_name: str,
    submitted_evidence_ids: set[str],
) -> tuple[bool, str]:
    """Evaluate the final submission and return outcome plus explanation."""

    result = validate_submission(suspect_name, submitted_evidence_ids, state.case_data)
    return result.is_win, result.message


def _build_validation_message(result: ValidationResult) -> str:
    """Create a short explanation for the player-facing validation result."""

    if result.is_win:
        return (
            "Case solved. You identified the correct suspect and submitted all "
            "required evidence."
        )

    reasons: list[str] = []
    if not result.suspect_correct:
        reasons.append("the suspect is incorrect")
    if not result.evidence_correct:
        if result.missing_evidence_ids:
            missing = ", ".join(result.missing_evidence_ids)
            reasons.append(f"required evidence is missing ({missing})")
        else:
            reasons.append("required evidence is missing")

    return f"Case not solved: {' and '.join(reasons)}."


def _read_attr(obj: Any, names: tuple[str, ...], default: Any = None) -> Any:
    """Return the first matching attribute found on an object."""

    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def _as_iterable(value: Any) -> list[Any]:
    """Normalize supported collection-like values into a list."""

    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=lambda item: normalize_text(str(item)))
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _clean_text(value: Any) -> str:
    """Return a trimmed string while preserving original character case."""

    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _ordered_unique_strings(values: Iterable[Any]) -> list[str]:
    """Return cleaned strings in stable order without case-insensitive duplicates."""

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


def _normalized_string_set(values: Iterable[Any]) -> set[str]:
    """Return a case-insensitive lookup set for the given values."""

    return {
        normalize_text(_clean_text(value))
        for value in values
        if normalize_text(_clean_text(value))
    }


def _get_documents(case_data: CaseData) -> list[Document]:
    """Return the case documents using a small set of supported field names."""

    return [
        document
        for document in _as_iterable(
            _read_attr(case_data, _DOCUMENT_COLLECTION_ATTRS, default=[])
        )
        if document is not None
    ]


def _get_document_id(document: Document) -> str:
    """Return a document identifier as a clean string."""

    return _clean_text(_read_attr(document, _DOCUMENT_ID_ATTRS, default=""))


def _get_solution(case_data: CaseData) -> Any:
    """Return the case solution object if one exists."""

    return _read_attr(case_data, _SOLUTION_ATTRS, default=None)


def _get_correct_suspect(case_data: CaseData) -> str:
    """Return the configured correct suspect value as a clean string."""

    source = _get_solution(case_data) or case_data
    raw_suspect = _read_attr(source, _CORRECT_SUSPECT_ATTRS, default=None)
    return _display_value(raw_suspect, _SUSPECT_VALUE_ATTRS)


def _get_required_evidence_ids(case_data: CaseData) -> list[str]:
    """Return the ordered list of required evidence IDs for the case."""

    source = _get_solution(case_data) or case_data
    raw_evidence_ids = _read_attr(source, _REQUIRED_EVIDENCE_ATTRS, default=[])
    return _ordered_unique_strings(_as_iterable(raw_evidence_ids))


def _display_value(value: Any, attr_names: tuple[str, ...]) -> str:
    """Convert a simple object or dataclass-like value into display text."""

    if value is None:
        return ""
    if isinstance(value, str):
        return _clean_text(value)

    for attr_name in attr_names:
        if hasattr(value, attr_name):
            attr_value = _clean_text(getattr(value, attr_name))
            if attr_value:
                return attr_value

    return _clean_text(value)


def _suspects_match(submitted_value: Any, correct_value: Any) -> bool:
    """Return True when two suspect references describe the same suspect."""

    submitted_options = {
        normalize_text(option)
        for option in _candidate_values(submitted_value, _SUSPECT_VALUE_ATTRS)
        if normalize_text(option)
    }
    correct_options = {
        normalize_text(option)
        for option in _candidate_values(correct_value, _SUSPECT_VALUE_ATTRS)
        if normalize_text(option)
    }
    return bool(submitted_options and correct_options and submitted_options & correct_options)


def _candidate_values(value: Any, attr_names: tuple[str, ...]) -> list[str]:
    """Return likely identifier/display strings for a value."""

    if value is None:
        return []
    if isinstance(value, str):
        return [_clean_text(value)]

    candidates: list[str] = []
    for attr_name in attr_names:
        if hasattr(value, attr_name):
            cleaned_value = _clean_text(getattr(value, attr_name))
            if cleaned_value:
                candidates.append(cleaned_value)

    if not candidates:
        fallback = _clean_text(value)
        if fallback:
            candidates.append(fallback)

    return _ordered_unique_strings(candidates)


__all__ = [
    "ValidationResult",
    "evaluate_case_submission",
    "filter_new_documents",
    "find_matching_documents",
    "has_required_evidence",
    "is_correct_suspect",
    "is_reused_keyword",
    "is_valid_keyword",
    "normalize_text",
    "validate_submission",
]
