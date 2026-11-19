"""Quest finite-state machine, immutable clues and timeline deduction board."""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional


class QuestState(str, Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    DEDUCTION_PHASE = "deduction_phase"
    COMPLETED = "completed"


@dataclass(frozen=True)
class Clue:
    id: str
    title: str
    clue_type: str
    detail: str
    source: str
    timeline_stage: int

    def __post_init__(self):
        for name in ("id", "title", "clue_type", "detail", "source"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must not be empty")
        if not isinstance(self.timeline_stage, int) or not 0 <= self.timeline_stage <= 3:
            raise ValueError("timeline_stage must be from 0 to 3")


class ClueInventory:
    def __init__(self):
        self.clues = {}

    def add(self, clue: Clue):
        if not isinstance(clue, Clue):
            raise TypeError("inventory accepts Clue objects")
        self.clues[clue.id] = clue
        return True

    def get(self, clue_id):
        return self.clues.get(clue_id)

    def __contains__(self, clue_id):
        return clue_id in self.clues


class QuestStateMachine:
    def __init__(self, required_clue_ids: Iterable[str] = ()):
        self.required_clue_ids = set(required_clue_ids)
        self.collected_clue_ids = set()
        self.state = QuestState.LOCKED
        self.timeline_verified = False
        self.quiz_completed = False
        self.lives = 3

    def lose_life(self):
        """Giam mang song. Neu het mang -> QUAY LAI LOCKED."""
        self.lives -= 1
        if self.lives <= 0:
            self.state = QuestState.LOCKED
            self.collected_clue_ids = set()
            self.timeline_verified = False
            self.quiz_completed = False
        return self.lives

    def start(self):
        if self.state == QuestState.LOCKED:
            self.state = QuestState.IN_PROGRESS
            return True
        return self.state in (QuestState.IN_PROGRESS, QuestState.DEDUCTION_PHASE)

    def collect_clue(self, clue_id):
        if clue_id not in self.required_clue_ids or self.state not in (QuestState.IN_PROGRESS, QuestState.DEDUCTION_PHASE):
            return False
        self.collected_clue_ids.add(clue_id)
        if self.collected_clue_ids >= self.required_clue_ids:
            self.state = QuestState.DEDUCTION_PHASE
        return True

    def complete_timeline(self, is_correct):
        if self.state != QuestState.DEDUCTION_PHASE or not is_correct:
            return False
        self.timeline_verified = True
        return True

    def mark_quiz_completed(self):
        if not self.timeline_verified or self.state != QuestState.DEDUCTION_PHASE:
            return False
        self.quiz_completed = True
        return True

    def complete(self):
        if self.timeline_verified and self.quiz_completed:
            self.state = QuestState.COMPLETED
            return True
        return False


class DeductionTimelineBoard:
    def __init__(self, inventory=None, state_machine=None):
        self.inventory = inventory or ClueInventory()
        self.state_machine = state_machine
        self.slots = [None] * 4
        self.verified = False
        self.message = ""

    def place(self, clue_id, slot_index):
        if clue_id not in self.inventory or not 0 <= slot_index < 4:
            return False
        for i, value in enumerate(self.slots):
            if value == clue_id:
                self.slots[i] = None
        displaced = self.slots[slot_index]
        self.slots[slot_index] = clue_id
        if displaced is not None and displaced != clue_id:
            empty = next((i for i, value in enumerate(self.slots) if value is None), None)
            if empty is not None:
                self.slots[empty] = displaced
        self.verified = False
        return True

    def swap(self, first, second):
        if not (0 <= first < 4 and 0 <= second < 4):
            return False
        self.slots[first], self.slots[second] = self.slots[second], self.slots[first]
        self.verified = False
        return True
    def remove(self, slot_index):
        if not 0 <= slot_index < 4:
            return None
        clue_id = self.slots[slot_index]
        self.slots[slot_index] = None
        self.verified = False
        return clue_id



    def reset(self):
        self.slots = [None] * 4
        self.verified = False
        self.message = ""

    def check(self):
        if any(clue_id is None for clue_id in self.slots):
            self.message = "Còn ô trống trên dòng thời gian."
            self.verified = False
            return False
        clues = [self.inventory.get(clue_id) for clue_id in self.slots]
        if any(clue is None for clue in clues) or [c.timeline_stage for c in clues] != [0, 1, 2, 3]:
            self.message = "MÂU THUẪN LỊCH SỬ: hãy sắp xếp lại các giai đoạn."
            self.verified = False
            if self.state_machine:
                self.state_machine.complete_timeline(False)
            return False
        self.verified = True
        self.message = "ĐÃ XÁC THỰC LỊCH SỬ: dòng thời gian chính xác."
        if self.state_machine:
            self.state_machine.complete_timeline(True)
        return True


class QuizSystem:
    """Sequential multiple-choice quiz; each correct answer awards 30 points."""
    def __init__(self, questions):
        self.questions = list(questions or [])
        self.score = 0
        self._next_index = 0
        self.results = []

    def answer(self, question_index, choice_index):
        if question_index != self._next_index:
            raise ValueError("Questions must be answered in order")
        if question_index >= len(self.questions):
            raise ValueError("No unanswered questions remain")
        question = self.questions[question_index]
        options = question.get("options", [])
        if not isinstance(choice_index, int) or not 0 <= choice_index < len(options):
            raise ValueError("choice_index is outside the available options")
        correct = choice_index == question.get("answer")
        points = 30 if correct else 0
        self.score += points
        self.results.append({"correct": correct, "points": points, "question": question})
        self._next_index += 1
        return {"correct": correct, "points": points, "explanation": question.get("explanation", ""), "source": question.get("source", "")}


class QuestManager:
    """Tracks per-location progress and unlocks locations in chronological order."""
    def __init__(self, locations, completed=None, progress=None):
        self.locations = list(locations or [])
        self.completed = set(completed or ())
        self.collected_clues = {}
        self.quiz_attempts = {}
        self._progress = progress or {}
        for location in self.locations:
            saved = self._progress.get(str(location.get("id", location.get("name", ""))), {})
            if isinstance(saved, dict):
                self.collected_clues[location["name"]] = set(saved.get("clue_ids", []))
                self.quiz_attempts[location["name"]] = int(saved.get("quiz_attempts", 0))
        self._refresh_unlocks()

    def _refresh_unlocks(self):
        self.unlocked = set(self.completed)
        first_open = next((loc for loc in sorted(self.locations, key=lambda item: item.get("start", 0)) if loc.get("name") not in self.completed), None)
        if first_open:
            self.unlocked.add(first_open["name"])
        if "Ba Dinh" in self.completed:
            self.unlocked.add("Dien Bien Phu")

    def state(self, location):
        name = location.get("name") if isinstance(location, dict) else str(location)
        if name in self.completed:
            return "completed"
        return "open" if name in self.unlocked else "locked"

    def start(self, location):
        name = location["name"]
        self.collected_clues.setdefault(name, set())
        self.quiz_attempts.setdefault(name, 0)
        self.unlocked.add(name)
        return True

    def collect_clue(self, location, clue_id, required_ids=None):
        name = location["name"]
        self.collected_clues.setdefault(name, set()).add(clue_id)
        return True

    def clues_complete(self, location):
        name = location["name"]
        return bool(self.collected_clues.get(name))

    def record_quiz_answer(self, location, is_correct):
        name = location["name"]
        self.quiz_attempts[name] = self.quiz_attempts.get(name, 0) + 1
        return self.quiz_attempts[name]

    def complete(self, location):
        name = location["name"]
        if self.state(location) == "locked":
            return False
        self.completed.add(name)
        self._refresh_unlocks()
        return True

    def export_location_progress(self, location):
        name = location["name"]
        return {"clue_ids": sorted(self.collected_clues.get(name, set())), "quiz_attempts": self.quiz_attempts.get(name, 0)}

    def restore_location_progress(self, location, clue_ids, quiz_attempts, required_ids=None):
        name = location["name"]
        required = set(required_ids or ())
        self.collected_clues[name] = set(clue_ids or ()) & required if required else set(clue_ids or ())
        self.quiz_attempts[name] = int(quiz_attempts or 0)
        return True

    def timeline(self):
        """Return chronological milestone states for the map timeline widget."""
        timeline_items = []
        for location in sorted(self.locations, key=lambda item: (item.get("start", 0), item.get("id", 0))):
            name = location.get("name", "")
            if name in self.completed:
                state = "completed"
            elif self.collected_clues.get(name):
                state = "investigating"
            elif self.quiz_attempts.get(name, 0):
                state = "quiz"
            elif name in self.unlocked:
                state = "available"
            else:
                state = "locked"
            timeline_items.append({"year": location.get("start", ""), "state": state, "name": name})
        return timeline_items


def build_save_json(quest_id, state_machine=None, inventory=None, quiz_system=None):
    """Serialize Task 4 quest progress into a standardized JSON string."""
    import json
    # Normalize state_machine: if a string is passed, use it as the state value
    raw_state = state_machine
    if isinstance(raw_state, str):
        # String passed – treat as ready-made state value
        state_value = raw_state
        timeline_verified = False
        quiz_completed = False
        collected_clue_ids = []
    else:
        # Proper QuestStateMachine instance
        state_obj = getattr(raw_state, "state", None)
        state_value = state_obj.value if (state_obj and hasattr(state_obj, "value")) else str(state_obj or "locked")
        timeline_verified = getattr(raw_state, "timeline_verified", False) if raw_state else False
        quiz_completed = getattr(raw_state, "quiz_completed", False) if raw_state else False
        collected_clue_ids = sorted(list(getattr(raw_state, "collected_clue_ids", []))) if raw_state else []
    # Handle inventory fallback when no state_machine provided
    if isinstance(raw_state, str):
        col_ids = sorted(list(inventory.clues.keys())) if inventory else []
    else:
        col_ids = collected_clue_ids
    # Handle quiz_system
    if quiz_system is not None:
        qs = quiz_system
        quiz_score = getattr(qs, "score", 0)
        quiz_attempts = len(getattr(qs, "results", []))
    else:
        quiz_score = 0
        quiz_attempts = 0
    data = {
        "quest_id": quest_id,
        "state": state_value,
        "timeline_verified": timeline_verified,
        "quiz_completed": quiz_completed,
        "collected_clue_ids": col_ids,
        "quiz_score": quiz_score,
        "quiz_attempts": quiz_attempts,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)

