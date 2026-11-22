"""Barrier không được kích hoạt bởi app production hay copy vào WASM."""
from pathlib import Path


def test_barrier_only_exists_in_separate_test_entrypoint():
    root = Path(__file__).resolve().parents[1]
    for source in (root/'task5/server').glob('*.py'):
        assert 'TASK5_TRANSACTION_BARRIER' not in source.read_text(encoding='utf-8')
    builder = (root/'task5/build_web.py').read_text(encoding='utf-8')
    assert "'test_'" in builder