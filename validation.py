"""Search and win/loss validation for File Not Found."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from models import CaseData, Document, GameState


@dataclass(slots=True)
class ValidationResult:
    """Outcome of a final suspect and evidence submission."""

    is_win: bool
    suspect_correct: bool
    evidence_correct: bool
    missing_evidence_ids: tuple[str, ...] = ()
    submitted_suspect: str = ""
    correct_suspect: str = ""
    submitted_evidence_ids: frozenset[str] = field(default_factory=frozenset)
    required_evidence_ids: tuple[str, ...] = ()
    message: str = ""


def normalize_text(value: object) -> str:
    """Normalize text for case-insensitive comparisons."""

    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())


def find_matching_documents(case_data: CaseData, keyword: str) -> list[Document]:
    """Return all documents unlocked by a keyword."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return []

    return [
        document
        for document in case_data.documents
        if any(
            normalize_text(item) == normalized_keyword
            for item in document.unlock_keywords
        )
    ]


def filter_new_documents(
    state: GameState,
    documents: list[Document],
) -> list[Document]:
    """Keep only documents the player has not unlocked yet."""

    unlocked_ids = _normalized_string_set(state.unlocked_document_ids)
    return [
        document
        for document in documents
        if normalize_text(document.document_id) not in unlocked_ids
    ]


def is_valid_keyword(state: GameState, keyword: str) -> bool:
    """Check whether a keyword is currently available."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    return any(
        normalize_text(item) == normalized_keyword
        for item in state.available_keywords
    )


def is_reused_keyword(state: GameState, keyword: str) -> bool:
    """Check whether a keyword has already been searched."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    return any(
        normalize_text(item) == normalized_keyword
        for item in state.used_keywords
    )


def has_required_evidence(state: GameState) -> bool:
    """Check whether the player has the evidence needed to win."""

    solution = state.case_data.solution
    if solution is None:
        return False

    required_evidence_ids = _ordered_unique_strings(
        _as_value_list(solution.required_evidence_ids)
    )
    collected_evidence_ids = _normalized_string_set(state.collected_evidence_ids)
    return all(
        normalize_text(evidence_id) in collected_evidence_ids
        for evidence_id in required_evidence_ids
    )


def is_correct_suspect(state: GameState, suspect_name: str) -> bool:
    """Check whether the submitted suspect matches the solution."""

    solution = state.case_data.solution
    if solution is None:
        return False
    return _suspects_match(suspect_name, solution.correct_suspect)


def validate_submission(
    submitted_suspect_id: str,
    submitted_evidence_ids: Iterable[str] | str,
    case_data: CaseData,
) -> ValidationResult:
    """Validate a final accusation against the case solution."""

    submitted_suspect = _clean_text(submitted_suspect_id)
    submitted_evidence = _ordered_unique_strings(_as_value_list(submitted_evidence_ids))

    solution = case_data.solution
    correct_suspect = _clean_text(solution.correct_suspect) if solution else ""
    required_evidence = (
        _ordered_unique_strings(_as_value_list(solution.required_evidence_ids))
        if solution is not None
        else []
    )

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
    """Return the final case result in the older wrapper format."""

    result = validate_submission(suspect_name, submitted_evidence_ids, state.case_data)
    return result.is_win, result.message


def _build_validation_message(result: ValidationResult) -> str:
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


def _normalized_string_set(values: Iterable[object]) -> set[str]:
    return {
        normalize_text(_clean_text(value))
        for value in values
        if normalize_text(_clean_text(value))
    }


def _suspects_match(submitted_value: object, correct_value: object) -> bool:
    submitted = normalize_text(_clean_text(submitted_value))
    correct = normalize_text(_clean_text(correct_value))
    return bool(submitted and correct and submitted == correct)


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
