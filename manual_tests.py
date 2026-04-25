"""Manual/integration verification flows for File Not Found.

These checks exercise the professor-facing manual test cases MT-01 through
MT-04 without requiring interactive terminal input.
"""

from __future__ import annotations

from data import build_demo_case
from game_engine import (
    GameEngine,
    collect_evidence_from_document,
    create_new_game,
    get_unlocked_documents,
    search_keyword,
    submit_case_answer,
)


def search_all_available_keywords(state) -> None:
    """Search every reachable keyword in the current case."""
    for _ in range(20):
        remaining_keywords = state.available_keywords - state.used_keywords
        if not remaining_keywords:
            return
        for keyword in sorted(remaining_keywords):
            search_keyword(state, keyword)


def build_fully_investigated_state():
    """Create a state with all reachable documents and evidence collected."""
    state = create_new_game(build_demo_case(0))
    search_all_available_keywords(state)
    for document in get_unlocked_documents(state):
        for evidence_item in document.evidence_items:
            collect_evidence_from_document(
                state,
                document.document_id,
                [evidence_item.evidence_id],
            )
    return state


def mt_01_successful_full_case_solution() -> None:
    """MT-01: correct suspect plus collected required evidence wins the case."""
    state = build_fully_investigated_state()
    correct_suspect = state.case_data.solution.correct_suspect

    won, message = submit_case_answer(
        state,
        correct_suspect,
        set(state.collected_evidence_ids),
    )

    assert won is True
    assert state.game_over is True
    assert state.player_won is True
    assert "Case solved" in message


def mt_02_wrong_suspect_submission() -> None:
    """MT-02: wrong suspect loses even with complete evidence."""
    state = build_fully_investigated_state()
    correct_suspect = state.case_data.solution.correct_suspect
    wrong_suspect = next(
        suspect for suspect in state.case_data.suspects if suspect != correct_suspect
    )

    won, message = submit_case_answer(
        state,
        wrong_suspect,
        set(state.collected_evidence_ids),
    )

    assert won is False
    assert state.game_over is True
    assert state.player_won is False
    assert "suspect is incorrect" in message


def mt_03_missing_evidence_submission() -> None:
    """MT-03: correct suspect without required evidence loses."""
    state = create_new_game(build_demo_case(0))
    search_all_available_keywords(state)
    correct_suspect = state.case_data.solution.correct_suspect

    won, message = submit_case_answer(state, correct_suspect, set())

    assert won is False
    assert state.game_over is True
    assert state.player_won is False
    assert "required evidence is missing" in message


def mt_04_invalid_and_reused_keyword_handling() -> None:
    """MT-04: invalid and reused keywords do not unlock extra documents."""
    state = create_new_game(build_demo_case(0))
    engine = GameEngine.from_state(state)

    invalid_result = engine.search_keyword("not a real lead")
    first_result = engine.search_keyword("accident timeline")
    reused_result = engine.search_keyword("Accident Timeline")

    assert invalid_result.status == "no_results"
    assert first_result.status == "success"
    assert reused_result.status == "reused"
    assert reused_result.unlocked_documents == ()


def main() -> None:
    """Run all manual/integration checks."""
    checks = [
        ("MT-01", mt_01_successful_full_case_solution),
        ("MT-02", mt_02_wrong_suspect_submission),
        ("MT-03", mt_03_missing_evidence_submission),
        ("MT-04", mt_04_invalid_and_reused_keyword_handling),
    ]
    for label, check in checks:
        check()
        print(f"{label} passed")


if __name__ == "__main__":
    main()
