"""Scaffold smoke tests — prove the skeleton is wired (these PASS, unlike the spec
skeletons in precedent_memory/tests which skip until implemented).

If any of these fail, the scaffold itself is broken — fix before building on it.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_open_weight_registry_loads_and_guards():
    from precedent import models

    # all four roles resolve to a pinned id
    for role in ("FAST", "SMART", "HEAVY", "EMBED"):
        assert models.model_id(role)
    # the guard rejects a closed model whose source isn't huggingface.co
    import pytest

    bad = {"qwen3-5-35b-a3b": "https://huggingface.co/Qwen/Qwen3.5-35B-A3B",
           "deepseek-v4-flash": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash",
           "deepseek-v4-pro": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro",
           "text-embedding-bge-m3": "https://openai.com/nope"}  # EMBED faked to a non-HF source
    with pytest.raises(RuntimeError):
        models.assert_open_weight(bad)


def test_contracts_import_and_construct():
    from precedent.contracts import IncidentEvent

    ev = IncidentEvent(
        incident_id="I1", raw_text="epg publish failed", source="sim", observed_at="now"
    )
    assert ev.source == "sim"


def test_schema_executes():
    sql = (ROOT / "precedent_memory" / "schema.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(sql)  # raises if the DDL is malformed
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"memory_record", "effective_policy", "audit_log", "class_ladder"} <= tables


def test_fingerprint_is_deterministic():
    from precedent.contracts import Extracted
    from precedent.extractor import fingerprint

    e = Extracted(service="publisher", error_code="PUB-4012", target_object_type="schedule_item")
    assert fingerprint(e) == fingerprint(e)
    assert len(fingerprint(e)) == 64  # sha256 hex
