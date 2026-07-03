"""Saturday live/realism commands: exit non-zero when unconfigured; the UCI pipeline runs
on a synthetic CSV so the code path is actually exercised (T3-14)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from precedent_memory.bench import uci_realism

_ROOT = Path(__file__).resolve().parent.parent

_SYNTH_CSV = """\
number,sys_mod_count,category,subcategory,closed_code,assignment_group,opened_at,resolved_at
INC001,0,Hardware,Server,code 5,Group A,01/01/2024 10:00,01/01/2024 12:00
INC001,1,Hardware,Server,code 5,Group A,01/01/2024 10:00,01/01/2024 12:00
INC002,0,Software,DB,code 6,Group B,02/01/2024 10:00,02/01/2024 11:00
INC003,0,Network,Router,code 7,Group C,03/01/2024 10:00,03/01/2024 15:00
INC004,0,Software,DB,code 6,?,04/01/2024 10:00,04/01/2024 12:00
INC005,0,Hardware,Disk,code 8,Group A,05/01/2024 10:00,05/01/2024 13:00
INC006,0,Software,App,code 9,Group B,06/01/2024 10:00,06/01/2024 12:00
"""


def test_uci_realism_exits_nonzero_without_csv():
    assert uci_realism.main(["/no/such/uci-file.csv"]) == 2


def test_uci_realism_pipeline_runs_on_synthetic_csv(tmp_path):
    csv_path = tmp_path / "incident_event_log.csv"
    csv_path.write_text(_SYNTH_CSV)

    incidents = uci_realism.load_incidents(csv_path)
    assert len(incidents) == 6                       # INC001's two events collapse to one

    result = uci_realism.run_uci_realism(csv_path, n_queries=500)
    assert result["caption"] == "25k-record store"   # never "141k events"
    assert result["n_records"] == 6
    assert result["n_groups"] == 3                    # Group A/B/C; '?' is not a group
    # compiler agrees with the independent oracle over real-shaped data
    assert result["fnr_leaks"] == 0
    assert result["fpr_outages"] == 0
    assert result["deny_expected"] + result["allow_expected"] > 0


def test_uci_realism_is_deterministic(tmp_path):
    csv_path = tmp_path / "incident_event_log.csv"
    csv_path.write_text(_SYNTH_CSV)
    a = uci_realism.run_uci_realism(csv_path, n_queries=500)
    b = uci_realism.run_uci_realism(csv_path, n_queries=500)
    for k in ("n_records", "deny_expected", "allow_expected", "fnr_leaks", "fpr_outages"):
        assert a[k] == b[k]


def _run_script(script: str, env_extra: dict) -> int:
    import os
    env = {k: v for k, v in os.environ.items() if not k.startswith("JIRA_")}
    env.update(env_extra)
    proc = subprocess.run([sys.executable, str(_ROOT / "scripts" / script)],
                          cwd=_ROOT, capture_output=True, text=True, env=env)
    return proc.returncode


def test_live_drift_ttc_exits_nonzero_unconfigured():
    # no JIRA_* env -> unconfigured -> non-zero, whether or not the live flag is set
    assert _run_script("live_drift_ttc.py", {"PRECEDENT_LIVE_DRIFT": "1"}) == 1
    assert _run_script("live_drift_ttc.py", {}) == 1
