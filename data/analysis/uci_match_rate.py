"""UCI Incident Management event log — match-rate & baseline stats.

Run 3 Jul 2026 against UCI dataset #498 (CC BY 4.0, 141,712 events / 24,918 incidents).
Reproduces the slide-10 numbers. Download:
https://archive.ics.uci.edu/static/public/498/incident+management+process+enriched+event+log.zip
"""
import numpy as np
import pandas as pd

df = pd.read_csv("incident_event_log.csv", na_values=["?"], low_memory=False)
for c in ("opened_at", "resolved_at"):
    df[c] = pd.to_datetime(df[c], format="%d/%m/%Y %H:%M", errors="coerce")

# collapse events to per-incident records (last event per incident)
df = df.sort_values(["number", "sys_mod_count"])
inc = df.groupby("number").last().reset_index()

inc["fp"] = inc["category"].astype(str) + "|" + inc["subcategory"].astype(str) + "|" + inc["closed_code"].astype(str)
inc["sfp"] = inc["category"].astype(str) + "|" + inc["subcategory"].astype(str)
inc["fp_valid"] = inc["category"].notna() & inc["subcategory"].notna() & inc["closed_code"].notna()
inc["res_h"] = (inc["resolved_at"] - inc["opened_at"]).dt.total_seconds() / 3600

# chronological match rate: fingerprint seen in a prior incident at arrival time
v = inc[inc["fp_valid"]].sort_values("opened_at").copy()
for col, key in (("matched_prior", "fp"), ("sym_matched_prior", "sfp")):
    seen, m = set(), []
    for x in v[key]:
        m.append(x in seen)
        seen.add(x)
    v[col] = m

ok = v[v["res_h"].between(0, 24 * 90)]  # drop negatives and >90-day outliers
cc = v["fp"].value_counts()

print("fix-class match rate:", round(v["matched_prior"].mean() * 100, 1), "%")
print("symptom-class match rate:", round(v["sym_matched_prior"].mean() * 100, 1), "%")
print("median res_h precedented:", round(ok[ok["matched_prior"]]["res_h"].median(), 1))
print("median res_h first-of-class:", round(ok[~ok["matched_prior"]]["res_h"].median(), 1))
print("SLA breach share (precedented):", round((ok[ok["matched_prior"]]["made_sla"] == False).mean(), 3))
print("reassigned>0 share (precedented):", round((ok[ok["matched_prior"]]["reassignment_count"] > 0).mean(), 3))
print("classes >=4 occurrences:", (cc >= 4).sum(), "covering", round(cc[cc >= 4].sum() / len(v) * 100, 1), "%")

# --- Arrival-time top-1/top-3 precedent precision (added after judge round 2) ---
from collections import defaultdict, Counter

hist, hist_last = defaultdict(Counter), {}
modal1, recent1, top3, n = 0, 0, 0, 0
for _, row in v.iterrows():
    s, f = row["sfp"], row["fp"]
    if hist[s]:
        n += 1
        ranked = [k for k, _ in hist[s].most_common(3)]
        if ranked[0] == f: modal1 += 1
        if f in ranked: top3 += 1
        if hist_last[s] == f: recent1 += 1
    hist[s][f] += 1
    hist_last[s] = f
print("arrival-time top-1 (modal prior):", round(100 * modal1 / n, 1), "%")
print("arrival-time top-1 (most recent):", round(100 * recent1 / n, 1), "%")
print("arrival-time top-3 (modal prior):", round(100 * top3 / n, 1), "%")
