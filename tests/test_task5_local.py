"""Kiểm thử Task 5 không dùng database hoặc ghi dữ liệu thật."""
import tempfile
import unittest
from pathlib import Path

from task5.review_system import ReviewManager, ReviewStatus, review_path_for_user
from task5.scoring_system import ScoringEngine


class TestTask5Local(unittest.TestCase):
    def test_scoring_correct_wrong_clamps_and_ranks(self):
        engine = ScoringEngine()
        self.assertEqual(engine.record_answer(True, 30), 30)
        self.assertEqual(engine.record_answer(False, 0), -10)
        self.assertEqual(ScoringEngine(0).calculate_rank(100), "C")
        self.assertEqual(ScoringEngine(0).calculate_rank(300), "B")
        self.assertEqual(ScoringEngine(0).calculate_rank(600), "A")
        self.assertEqual(ScoringEngine(0).calculate_rank(1000), "S")

    def test_same_wrong_question_penalized_once_in_session(self):
        engine = ScoringEngine(50)
        self.assertEqual(engine.record_wrong_once("q"), -10)
        self.assertEqual(engine.record_wrong_once("q"), 0)
        self.assertEqual(engine.total_score, 40)

    def test_review_reward_once_and_retry_mastered(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ReviewManager(storage_path=Path(directory) / "one.json")
            manager.record_mistake("q1", "Pác Bó", "Câu?", ["sai", "đúng"], 1, 0)
            result = manager.retry_answer("q1", 1)
            self.assertTrue(result.is_correct)
            self.assertEqual(result.status, ReviewStatus.MASTERED)
            engine = ScoringEngine()
            self.assertEqual(engine.record_review_reward("q1"), 15)
            self.assertEqual(engine.record_review_reward("q1"), 0)

    def test_review_profiles_are_separate_and_guest_not_shared(self):
        player_one = review_path_for_user(11)
        player_two = review_path_for_user(12)
        guest_one = review_path_for_user(0, "session-a")
        guest_two = review_path_for_user(0, "session-b")
        self.assertNotEqual(player_one, player_two)
        self.assertNotEqual(guest_one, guest_two)
        self.assertNotEqual(guest_one.name, "review_progress.json")
        with tempfile.TemporaryDirectory() as directory:
            one = ReviewManager(storage_path=Path(directory) / "player_11.json")
            two = ReviewManager(storage_path=Path(directory) / "player_12.json")
            one.record_mistake("q1", "A", "Câu A", ["x", "y"], 1, 0)
            self.assertEqual(two.questions, {})


if __name__ == "__main__":
    unittest.main()