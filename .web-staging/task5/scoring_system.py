"""Score calculation and rank badges for the history game."""


class ScoringEngine:
    RANKS = ((1000, "S"), (600, "A"), (300, "B"), (100, "C"), (0, "D"))
    TITLES = {"S": "Bậc Thầy Sử Học Việt Nam", "A": "Nhà Nghiên cứu Lịch sử", "B": "Học giả Sử học", "C": "Người Tìm kiếm Tư liệu", "D": "Tập sự Lịch sử"}

    def __init__(self, total_score=0):
        self.total_score = max(0, int(total_score))
        self.correct_streak = 0
        self.awarded_reviews = set()
        self.penalized_questions = set()
        self.correct_answers = 0
        self.incorrect_answers = 0

    def calculate_rank(self, score):
        score = max(0, int(score))
        return next(rank for minimum, rank in self.RANKS if score >= minimum)

    def record_answer(self, is_correct, elapsed_seconds=0, base_points=30):
        if not is_correct:
            self.correct_streak = 0
            self.incorrect_answers += 1
            self.total_score = max(0, self.total_score - 10)
            return -10
        self.correct_streak += 1
        self.correct_answers += 1
        speed_bonus = max(0, (30 - max(0, float(elapsed_seconds))) * 0.8)
        multiplier = min(1.5, 1.0 + max(0, self.correct_streak - 1) * 0.1)
        earned = round((int(base_points) + speed_bonus) * multiplier)
        self.total_score += earned
        return earned

    def record_wrong_once(self, question_id):
        """Phạt một câu sai tối đa một lần trong phiên chơi hiện tại."""
        key = str(question_id)
        if key in self.penalized_questions:
            self.correct_streak = 0
            return 0
        self.penalized_questions.add(key)
        self.correct_streak = 0
        self.incorrect_answers += 1
        self.total_score = max(0, self.total_score - 10)
        return -10

    def record_review_reward(self, question_id):
        if question_id in self.awarded_reviews:
            return 0
        self.awarded_reviews.add(question_id)
        self.total_score += 15
        return 15

    def add_points(self, points):
        self.total_score = max(0, self.total_score + int(points))
        return self.total_score

    def export_summary(self):
        rank = self.calculate_rank(self.total_score)
        return {"total_score": self.total_score, "rank": rank, "rank_title": self.TITLES[rank], "correct_answers": self.correct_answers, "incorrect_answers": self.incorrect_answers}
