"""Bản đồ đồ thị có hướng (DAG) và thuật toán Dijkstra tìm đường ngắn nhất giữa các cứ điểm lịch sử."""
import heapq
from typing import Dict, List, Optional, Tuple


class HistoryMapGraph:
    def __init__(self):
        self.adj: Dict[str, List[Tuple[str, float]]] = {}
        self._init_default_graph()

    def add_edge(self, u: str, v: str, weight: float = 1.0):
        self.adj.setdefault(u, []).append((v, weight))
        self.adj.setdefault(v, [])

    def _init_default_graph(self):
        # Thiết lập các cung đồ thị lịch sử thuần Việt 100% trên Bản đồ Việt Nam từ 1858 đến 1975
        edges = [
            ("Bến Nhà Rồng (Sài Gòn)", "Huế - Kinh thành Huế", 1.2),
            ("Huế - Kinh thành Huế", "Vinh - Bến Thủy (Nghệ An)", 1.0),
            ("Vinh - Bến Thủy (Nghệ An)", "Hang Pác Bó (Cao Bằng)", 1.8),
            ("Hang Pác Bó (Cao Bằng)", "Tân Trào (Tuyên Quang)", 0.8),
            ("Tân Trào (Tuyên Quang)", "Quảng trường Ba Đình (Hà Nội)", 0.7),
            ("Quảng trường Ba Đình (Hà Nội)", "Căn cứ địa Việt Bắc", 0.9),
            ("Căn cứ địa Việt Bắc", "Lòng chảo Điện Biên Phủ", 1.4),
            ("Lòng chảo Điện Biên Phủ", "Dinh Độc Lập (Sài Gòn)", 2.5),
        ]
        for u, v, w in edges:
            self.add_edge(u, v, w)

    def find_path(self, start: str, end: str) -> List[str]:
        """Thuật toán Dijkstra tìm đường ngắn nhất giữa hai địa điểm lịch sử."""
        if start not in self.adj or end not in self.adj:
            # Fallback đơn giản nếu nút chưa có trong đồ thị
            return [start, end]

        distances = {node: float("inf") for node in self.adj}
        distances[start] = 0.0
        previous = {node: None for node in self.adj}
        pq = [(0.0, start)]

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_node == end:
                break

            if current_dist > distances[current_node]:
                continue

            for neighbor, weight in self.adj.get(current_node, []):
                distance = current_dist + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        # Tái dựng đường đi
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()

        return path if path and path[0] == start else [start, end]
