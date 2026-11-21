"""Chính sách mở khóa giữ đúng _refresh_unlocks của QuestManager Task 4."""
from __future__ import annotations


def unlocked_names(locations: list[dict], completed: set[str]) -> set[str]:
    unlocked = set(completed)
    first = next((location for location in sorted(locations, key=lambda item: item.get("start", 0))
                  if location["name"] not in completed), None)
    if first:
        unlocked.add(first["name"])
    if "Ba Dinh" in completed:
        unlocked.add("Dien Bien Phu")
    return unlocked


def validate_progress(locations: list[dict], completed: set[str], requested_completed: list[str], location_id: int) -> dict:
    """Client chỉ chọn địa điểm đã mở; không có quyền tự đánh dấu hoàn thành."""
    if not set(requested_completed).issubset(completed):
        raise ValueError("Không thể tự khai hoàn thành địa điểm qua API lưu tiến độ.")
    location = next((item for item in locations if item["id"] == location_id), None)
    if location is None:
        raise ValueError("Địa điểm không tồn tại.")
    if location["name"] not in unlocked_names(locations, completed):
        raise ValueError("Địa điểm chưa được mở khóa.")
    return location