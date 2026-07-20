"""WP-API finding 1 — every sim-db copy is HERMETIC (no torn copy, no missing rows).

The intermittent gate/sim RED came from a NON-hermetic copy: ``shutil.copyfile`` copies only the
main db file, so a source with a live ``-wal`` sidecar (committed-but-un-checkpointed frames) is
copied TORN — silently dropping rows. This suite proves:

  * ``_copy_sqlite_db`` produces a COMPLETE db even when the source has a live WAL (the exact
    hazard) — and that plain ``shutil.copyfile`` does NOT (the red-was-red control);
  * ``sim_template()`` leaves NO ``-wal``/``-shm`` sidecars (single complete file, like
    ``memory_template``);
  * seeding MANY sim worlds in one process (both the console Session path and the gate
    ``build_seeded_world`` path) yields, every time, an integrity-clean db with all seed rows.
"""
from __future__ import annotations

import os
import shutil
import sqlite3

from console import session as sessionmod
from gate.world import build_seeded_world

# Cold-open sim seed cardinalities (data/raw + data/kb, seeded via sim.core.reset).
_EXPECTED = {"demo_incident": 3, "channel": 8, "programme": 54, "schedule_slot": 114,
             "vod_item": 12, "rights_record": 400, "kb_article": 10}


def _assert_complete_sim(path: str) -> None:
    conn = sqlite3.connect(path)
    try:
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "torn/corrupt copy"
        for table, n in _EXPECTED.items():
            got = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert got == n, f"{table}: expected {n} seed rows, got {got} (torn copy)"
    finally:
        conn.close()


def test_copy_is_hermetic_with_a_live_wal(tmp_path):
    """The core guarantee: a source with committed-but-un-checkpointed WAL frames copies WHOLE
    through the production helper. The ``shutil.copyfile`` control shows the torn-copy bug is real
    (red-was-red) — it drops the WAL-only rows."""
    src = str(tmp_path / "src.db")
    live = sqlite3.connect(src)
    live.execute("PRAGMA journal_mode=WAL")
    live.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)")
    live.executemany("INSERT INTO t(v) VALUES(?)", [(f"row-{i}",) for i in range(400)])
    live.commit()  # committed, but the frames still live in the -wal sidecar (no checkpoint)
    assert os.path.exists(src + "-wal"), "precondition: a live WAL sidecar exists"

    # Control: a naive main-file-only copy is TORN — the WAL-resident rows (and here even the
    # schema) are missing, so it reads < 400 rows or cannot read the table at all.
    torn = str(tmp_path / "torn.db")
    shutil.copyfile(src, torn)
    torn_conn = sqlite3.connect(torn)
    try:
        try:
            torn_count = torn_conn.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        except sqlite3.OperationalError:
            torn_count = 0  # table itself was WAL-resident — the most torn outcome
    finally:
        torn_conn.close()
    assert torn_count < 400, "control: shutil.copyfile must lose WAL-only rows (torn copy)"

    # The production helper reads a consistent image through SQLite — every committed row lands.
    dst = str(tmp_path / "dst.db")
    sessionmod._copy_sqlite_db(src, dst)
    live.close()
    whole = sqlite3.connect(dst)
    try:
        assert whole.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert whole.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 400
    finally:
        whole.close()


def test_sim_template_leaves_no_sidecars():
    """The cold-open sim template is ONE complete file — no -wal/-shm to be missed by a copy."""
    path = sessionmod.sim_template()
    _assert_complete_sim(path)
    assert not os.path.exists(path + "-wal"), "sim template must not carry a live WAL sidecar"
    assert not os.path.exists(path + "-shm"), "sim template must not carry a live SHM sidecar"


def test_many_session_sim_copies_are_all_complete(tmp_path):
    """Seed MANY sessions in one process; every per-session sim copy is integrity-clean with the
    full seed present (the WP-HOST-SESSION latent-copy bug guard)."""
    store = sessionmod.SessionStore(ttl_seconds=1800, max_sessions=64)
    try:
        for _ in range(16):
            sess = store.resolve(None)
            sess.sim_client()  # materialise the per-session sim copy
            _assert_complete_sim(sess.sim_path)
    finally:
        store.close_all()


def test_many_gate_seeded_world_sim_copies_are_all_complete(tmp_path):
    """The gate's build_seeded_world sim copy (gate/world.py) is hermetic too — seed many worlds
    in one process and assert every gate_sim.db is a complete, valid db."""
    for i in range(16):
        d = tmp_path / f"world-{i}"
        world = build_seeded_world(d)
        try:
            _assert_complete_sim(str(d / "gate_sim.db"))
        finally:
            world.close()
