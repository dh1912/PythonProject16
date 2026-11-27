"""Regression tests for Task 3's directed weighted history graph."""

import math

import pytest

from task3.map_graph import HistoryMapGraph


def test_default_graph_finds_directed_historical_path():
    graph = HistoryMapGraph()

    path = graph.find_path("Bến Nhà Rồng (Sài Gòn)", "Hang Pác Bó (Cao Bằng)")

    assert path[0] == "Bến Nhà Rồng (Sài Gòn)"
    assert path[-1] == "Hang Pác Bó (Cao Bằng)"
    assert len(path) == 4


def test_unknown_or_unreachable_nodes_have_no_fake_path():
    graph = HistoryMapGraph()
    graph.add_edge("isolated-start", "isolated-middle")
    graph.add_edge("other-start", "other-end")

    assert graph.find_path("unknown", "other-end") == []
    assert graph.find_path("isolated-start", "other-end") == []
    assert graph.find_path("isolated-start", "isolated-start") == ["isolated-start"]


def test_dijkstra_chooses_lowest_weight_path():
    graph = HistoryMapGraph()
    graph.add_edge("A", "B", 5)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 1)

    assert graph.find_path("A", "B") == ["A", "C", "B"]


@pytest.mark.parametrize("weight", [0, -1, math.inf, math.nan, True, "1"])
def test_edge_rejects_invalid_weight(weight):
    graph = HistoryMapGraph()

    with pytest.raises((TypeError, ValueError)):
        graph.add_edge("A", "B", weight)


def test_edge_rejects_empty_node_names():
    graph = HistoryMapGraph()

    with pytest.raises(ValueError):
        graph.add_edge("", "B")
    with pytest.raises(ValueError):
        graph.add_edge("A", "   ")
