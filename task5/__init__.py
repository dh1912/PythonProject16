"""Task 5 scoring, review and knowledge-retention tools."""
from .scoring_system import ScoringEngine
from .review_system import ReviewManager, ReviewQuestion, ReviewStatus


def __getattr__(name: str):
    """Chỉ nạp giao diện khi cần; server tính điểm không phụ thuộc Pygame."""
    if name == "DisplaySettingsScene":
        from .settings_scene import DisplaySettingsScene
        return DisplaySettingsScene
    if name == "LeaderboardScene":
        from .leaderboard_scene import LeaderboardScene
        return LeaderboardScene
    raise AttributeError(name)

__all__ = ["ScoringEngine", "ReviewManager", "ReviewQuestion", "ReviewStatus", "DisplaySettingsScene", "LeaderboardScene"]
