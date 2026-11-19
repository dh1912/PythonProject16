"""Persistent mistake-review bank with citations and retry tracking."""
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re
import uuid

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "reviews"


def review_path_for_user(user_id=None, guest_id=None):
    """Chọn file riêng cho từng người; không bao giờ dùng file chung mặc định."""
    raw = str(user_id) if user_id not in (None, 0, "0") else f"guest_{guest_id or uuid.uuid4().hex}"
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", raw)
    if not safe.startswith("guest_"):
        safe = f"player_{safe}"
    return _DATA_DIR / f"{safe}.json"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    MASTERED = "MASTERED"


@dataclass
class ReviewQuestion:
    id: str
    location_name: str
    question: str
    options: list
    correct_index: int
    user_choice: int = -1
    explanation: str = ""
    source_title: str = ""
    source_author: str = ""
    source_publisher: str = ""
    source_citation: str = ""
    status: ReviewStatus = ReviewStatus.PENDING
    retry_count: int = 0


@dataclass(frozen=True)
class RetryResult:
    is_correct: bool
    question_id: str
    status: ReviewStatus


class ReviewManager:
    def __init__(self, storage_path=None, user_id=None, guest_id=None):
        self.storage_path = Path(storage_path) if storage_path else review_path_for_user(user_id, guest_id)
        self.questions = {}
        self._load()

    @staticmethod
    def _to_question(question_id, data):
        status = data.get("status", "PENDING")
        try:
            status = ReviewStatus(status)
        except ValueError:
            status = ReviewStatus.PENDING
        return ReviewQuestion(
            id=str(data.get("id", question_id)),
            location_name=str(data.get("location_name", "")),
            question=str(data.get("question", data.get("question_text", ""))),
            options=list(data.get("options", [])),
            correct_index=int(data.get("correct_index", 0)),
            user_choice=int(data.get("user_choice", -1)),
            explanation=str(data.get("explanation", "")),
            source_title=str(data.get("source_title", "")),
            source_author=str(data.get("source_author", "")),
            source_publisher=str(data.get("source_publisher", "")),
            source_citation=str(data.get("source_citation", "")),
            status=status,
            retry_count=int(data.get("retry_count", 0)),
        )

    def _load(self):
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return
        if isinstance(raw, dict):
            self.questions = {key: self._to_question(key, value) for key, value in raw.items() if isinstance(value, dict)}

    def _save(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {}
            for key, q in self.questions.items():
                payload[key] = {"id": q.id, "location_name": q.location_name, "question": q.question, "options": q.options, "correct_index": q.correct_index, "user_choice": q.user_choice, "explanation": q.explanation, "source_title": q.source_title, "source_author": q.source_author, "source_publisher": q.source_publisher, "source_citation": q.source_citation, "status": q.status.value, "retry_count": q.retry_count}
            self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def record_mistake(self, question_id, location_name, question_text, options, correct_index, user_choice, explanation="", source_title="", source_author="", source_publisher="", source_citation=""):
        question_id = str(question_id)
        old = self.questions.get(question_id)
        if old:
            old.user_choice = int(user_choice)
            old.status = ReviewStatus.PENDING
            old.retry_count += 1
            q = old
        else:
            q = ReviewQuestion(question_id, str(location_name), str(question_text), list(options), int(correct_index), int(user_choice), str(explanation), str(source_title), str(source_author), str(source_publisher), str(source_citation), ReviewStatus.PENDING, 1)
            self.questions[question_id] = q
        self._save()
        return q

    def get_pending_questions(self):
        return [q for q in self.questions.values() if q.status == ReviewStatus.PENDING]

    def get_mastered_questions(self):
        return [q for q in self.questions.values() if q.status == ReviewStatus.MASTERED]

    def retry_answer(self, question_id, choice_index):
        question = self.questions[str(question_id)]
        if not isinstance(choice_index, int) or not 0 <= choice_index < len(question.options):
            raise ValueError("choice_index is outside the available options")
        question.user_choice = choice_index
        question.retry_count += 1
        correct = choice_index == question.correct_index
        if correct:
            question.status = ReviewStatus.MASTERED
        self._save()
        return RetryResult(correct, question.id, question.status)
