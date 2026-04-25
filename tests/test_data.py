"""Tests for data.py — case structure, keyword chains, evidence, win conditions."""

import unittest
from data import build_demo_case, ALL_CASES
from models import CaseData, CaseSolution
from game_engine import create_new_game, search_keyword, get_unlocked_documents, \
    collect_evidence_from_document, submit_case_answer


def _win_case(state):
    """Play through a case to the win condition automatically."""
    searched = set()
    for _ in range(20):
        remaining = state.available_keywords - state.used_keywords
        if not remaining:
            break
        for kw in list(remaining):
            if kw not in searched:
                search_keyword(state, kw)
                searched.add(kw)
    for doc in get_unlocked_documents(state):
        for item in doc.evidence_items:
            collect_evidence_from_document(state, doc.document_id, [item.evidence_id])
    correct = state.case_data.solution.correct_suspect
    won, msg = submit_case_answer(state, correct, set(state.collected_evidence_ids))
    return won, msg


class TestAllCasesList(unittest.TestCase):
    def test_four_cases_defined(self):
        self.assertEqual(len(ALL_CASES), 4)

    def test_case_names_are_strings(self):
        for name in ALL_CASES:
            self.assertIsInstance(name, str)
            self.assertTrue(len(name) > 0)


class TestBuildDemoCase(unittest.TestCase):
    def test_returns_case_data_for_all_indices(self):
        for i in range(4):
            case = build_demo_case(i)
            self.assertIsInstance(case, CaseData)

    def test_invalid_index_returns_first_case(self):
        case_neg = build_demo_case(-1)
        case_over = build_demo_case(99)
        case_zero = build_demo_case(0)
        self.assertEqual(case_neg.title, case_zero.title)
        self.assertEqual(case_over.title, case_zero.title)

    def test_each_case_has_required_fields(self):
        for i in range(4):
            case = build_demo_case(i)
            self.assertTrue(len(case.title) > 0)
            self.assertTrue(len(case.intro_text) > 0)
            self.assertIsInstance(case.suspects, list)
            self.assertIsInstance(case.documents, list)
            self.assertIsInstance(case.starting_keywords, list)
            self.assertIsNotNone(case.solution)

    def test_each_case_has_eight_documents(self):
        for i in range(4):
            self.assertEqual(len(build_demo_case(i).documents), 8)

    def test_each_case_has_three_starting_keywords(self):
        for i in range(4):
            self.assertEqual(len(build_demo_case(i).starting_keywords), 3)

    def test_each_case_has_at_least_two_suspects(self):
        for i in range(4):
            self.assertGreaterEqual(len(build_demo_case(i).suspects), 2)

    def test_solution_has_correct_suspect_and_evidence(self):
        for i in range(4):
            case = build_demo_case(i)
            self.assertIsInstance(case.solution, CaseSolution)
            self.assertTrue(len(case.solution.correct_suspect) > 0)
            self.assertIsInstance(case.solution.required_evidence_ids, set)
            self.assertGreater(len(case.solution.required_evidence_ids), 0)

    def test_correct_suspect_is_in_suspects_list(self):
        for i in range(4):
            case = build_demo_case(i)
            self.assertIn(case.solution.correct_suspect, case.suspects)

    def test_document_ids_are_unique(self):
        for i in range(4):
            case = build_demo_case(i)
            ids = [d.document_id for d in case.documents]
            self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_ids_are_unique_within_case(self):
        for i in range(4):
            case = build_demo_case(i)
            all_ids = [item.evidence_id for doc in case.documents for item in doc.evidence_items]
            self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_required_evidence_ids_exist_in_documents(self):
        for i in range(4):
            case = build_demo_case(i)
            all_ev_ids = {item.evidence_id for doc in case.documents for item in doc.evidence_items}
            for req_id in case.solution.required_evidence_ids:
                self.assertIn(req_id, all_ev_ids)

    def test_key_evidence_matches_required_ids(self):
        for i in range(4):
            case = build_demo_case(i)
            key_ids = {item.evidence_id for doc in case.documents
                       for item in doc.evidence_items if item.is_key_evidence}
            for req_id in case.solution.required_evidence_ids:
                self.assertIn(req_id, key_ids)

    def test_all_documents_reachable_via_keyword_chain(self):
        for i in range(4):
            case = build_demo_case(i)
            available = set(case.starting_keywords)
            unlocked, used = set(), set()
            for _ in range(20):
                searchable = available - used
                if not searchable:
                    break
                for kw in list(searchable):
                    used.add(kw)
                    for doc in case.documents:
                        if kw in doc.unlock_keywords and doc.document_id not in unlocked:
                            unlocked.add(doc.document_id)
                            for new_kw in doc.discovered_keywords:
                                available.add(new_kw)
            self.assertEqual(len(unlocked), len(case.documents),
                f"Case {i}: only {len(unlocked)}/{len(case.documents)} docs reachable")

    def test_documents_have_required_fields(self):
        for i in range(4):
            for doc in build_demo_case(i).documents:
                self.assertTrue(len(doc.document_id) > 0)
                self.assertTrue(len(doc.title) > 0)
                self.assertTrue(len(doc.text) > 0)
                self.assertIsInstance(doc.unlock_keywords, list)
                self.assertIsInstance(doc.evidence_items, list)

    def test_each_document_has_at_least_one_evidence_item(self):
        for i in range(4):
            for doc in build_demo_case(i).documents:
                self.assertGreater(len(doc.evidence_items), 0, f"Case {i} doc '{doc.title}' has no evidence")

    def test_evidence_items_have_required_fields(self):
        for i in range(4):
            for doc in build_demo_case(i).documents:
                for item in doc.evidence_items:
                    self.assertTrue(len(item.evidence_id) > 0)
                    self.assertTrue(len(item.label) > 0)
                    self.assertTrue(len(item.description) > 0)

    def test_starting_keywords_unlock_at_least_one_document(self):
        for i in range(4):
            case = build_demo_case(i)
            for kw in case.starting_keywords:
                matches = [d for d in case.documents if kw in d.unlock_keywords]
                self.assertGreater(len(matches), 0, f"Case {i}: keyword '{kw}' unlocks nothing")


class TestWinConditions(unittest.TestCase):
    def test_correct_suspect_and_evidence_wins_all_cases(self):
        for i in range(4):
            state = create_new_game(build_demo_case(i))
            won, msg = _win_case(state)
            self.assertTrue(won, f"Case {i} should be winnable but got: {msg}")

    def test_wrong_suspect_loses(self):
        state = create_new_game(build_demo_case(0))
        for _ in range(20):
            remaining = state.available_keywords - state.used_keywords
            if not remaining: break
            for kw in list(remaining): search_keyword(state, kw)
        for doc in get_unlocked_documents(state):
            for item in doc.evidence_items:
                collect_evidence_from_document(state, doc.document_id, [item.evidence_id])
        wrong = [s for s in state.case_data.suspects if s != state.case_data.solution.correct_suspect][0]
        won, _ = submit_case_answer(state, wrong, set(state.collected_evidence_ids))
        self.assertFalse(won)

    def test_missing_key_evidence_loses(self):
        state = create_new_game(build_demo_case(0))
        for _ in range(20):
            remaining = state.available_keywords - state.used_keywords
            if not remaining: break
            for kw in list(remaining): search_keyword(state, kw)
        won, _ = submit_case_answer(state, state.case_data.solution.correct_suspect, set())
        self.assertFalse(won)


if __name__ == "__main__":
    unittest.main(verbosity=2)
