# HƯỚNG DẪN TÍCH HỢP NHẬT KÝ MANH MỐI - CHI TIẾT TỪNG BƯỚC
# ============================================================

## BƯỚC 1: Cập nhật task4/__init__.py

Thêm dòng này vào imports ở đầu file task4/__init__.py:

```python
from .clue_notebook_scene import ClueNotebookScene
```

Sau đó thêm `ClueNotebookScene` vào `__all__`:

```python
__all__ = [
    "Clue", "ClueInventory", "DeductionTimelineBoard", "QuestState",
    "QuestStateMachine", "QuizSystem", "QuestManager", "build_save_json",
    "TIMELINE_QUEST_CONFIGS", "TimelineScene", "ClueNotebookScene",  # THÊM DÒY NÀY
]
```

---

## BƯỚC 2: Cập nhật main.py

Ở phần imports (dòng 22), thêm:

```python
from task4 import Clue, ClueInventory, DeductionTimelineBoard, QuizSystem, TimelineScene, QuestStateMachine, ClueNotebookScene  # THÊM ClueNotebookScene
```

Ở phần GameDirector.__init__ (khoảng dòng 130), thêm sau khi tạo TimelineScene:

```python
# Khởi tạo Clue Notebook Scene
self.clue_notebook_scene = ClueNotebookScene(WIDTH, HEIGHT)
self.clue_notebook_scene.load_all_clues()

# Khởi tạo font cho scene
import pygame
self.clue_notebook_scene.font_title = pygame.font.SysFont("segoeui,arial", 36, bold=True)
self.clue_notebook_scene.font_meta = pygame.font.SysFont("segoeui,arial", 20)
self.clue_notebook_scene.font_content = pygame.font.SysFont("segoeui,arial", 18)
self.clue_notebook_scene.font_button = pygame.font.SysFont("segoeui,arial", 20, bold=True)
```

---

## BƯỚC 3: Cập nhật vòng lặp chính trong main.py

Trong hàm GameDirector.update_scene() hoặc ở vòng while chính của game,
thêm xử lý cho Clue Notebook Scene:

```python
elif self.scene == "clue_notebook":
    action = self.clue_notebook_scene.handle_event(event)
    if action == 'back':
        self.scene = self.previous_scene  # Quay lại scene trước
    elif action == 'bookmark':
        # Thêm bookmark
        idx = self.clue_notebook_scene.get_current_index()
        self.clue_notebook_scene.bookmarked.add(idx)
    
    self.clue_notebook_scene.draw(screen)
```

---

## BƯỚC 4: Gọi Clue Notebook khi nhấp vào manh mối

Ở file scenes/investigation_scene.py hoặc task4/timeline_scene.py,
khi người chơi nhấp vào manh mối, thêm:

```python
# Khi người chơi muốn xem chi tiết manh mối
game_director.previous_scene = game_director.scene
game_director.scene = "clue_notebook"
game_director.clue_notebook_scene.set_current_clue(clue_index)
```

---

## CODE HOÀN CHỈNH clue_notebook_scene.py

Copy code dưới đây vào file c:/Users/tum/Desktop/PythonProject16/task4/clue_notebook_scene.py:

(See next file creation)
