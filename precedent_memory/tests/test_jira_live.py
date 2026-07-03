"""Live JiraPermissionSource — exercised with a MOCKED httpx transport (no network).

Proves: green path writes ACL and permits the right principal; tightening a level
denies; a 404 revokes and fans out; any outage/malformed response fails closed;
missing creds fail closed; and a token is never leaked into results/audit/errors.
"""
from __future__ import annotations

import json

import httpx

from precedent_memory import retrieve, store
from precedent_memory.sync import JiraPermissionSource, sync

JENV = {"JIRA_BASE_URL": "https://jira.test", "JIRA_EMAIL": "a@b.c",
        "JIRA_API_TOKEN": "FAKE-TOKEN-DO-NOT-LOG", "JIRA_PROJECT_KEY": "MEDIA"}
RUNBOOKS = {"jira:MEDIA-113": "MEDIA-113"}


def _src(handler, env=None):
    client = httpx.Client(base_url="https://jira.test", transport=httpx.MockTransport(handler))
    src = JiraPermissionSource(env or JENV, client=client, runbooks=RUNBOOKS,
                               level_owner={"10000": "Rights Ops"})
    return src, client


def test_jira_green_path_sets_acl_and_permits(conn):
    def handler(_req):
        return httpx.Response(200, json={"fields": {"security": {"id": "10000",
                                                                 "name": "Rights Ops Only"}}})
    src, client = _src(handler)
    res = sync(src, conn=conn)
    client.close()
    assert res["available"] is True
    cid = store.ensure_constraint(conn, "jira", "issue-security:10000", "Rights Ops")
    store.put_principal(conn, "rights", [cid])
    store.put_principal(conn, "nobody2", [])
    store.store({"fingerprint": "fp-j", "body": {"fix": "x"}}, ["jira:MEDIA-113"], conn=conn)
    assert retrieve.retrieve("rights", {"fingerprint": "fp-j"}, conn=conn).hits
    assert retrieve.retrieve("nobody2", {"fingerprint": "fp-j"}, conn=conn).hits == []


def test_jira_tightening_denies(conn):
    state = {"sec": None}

    def handler(_req):
        sec = ({"id": "10000", "name": "Rights Ops Only"} if state["sec"] else None)
        return httpx.Response(200, json={"fields": {"security": sec}})
    src, client = _src(handler)
    sync(src, conn=conn)                                   # public
    store.put_principal(conn, "sched", [])                 # no grants
    store.store({"fingerprint": "fp-j2", "body": {"fix": "x"}}, ["jira:MEDIA-113"], conn=conn)
    assert retrieve.retrieve("sched", {"fingerprint": "fp-j2"}, conn=conn).hits    # public ok
    state["sec"] = "on"
    sync(src, conn=conn)                                   # tighten -> requires Rights
    client.close()
    assert retrieve.retrieve("sched", {"fingerprint": "fp-j2"}, conn=conn).hits == []


def test_jira_404_revokes_and_fans_out(conn):
    state = {"mode": "ok"}

    def handler(_req):
        if state["mode"] == "404":
            return httpx.Response(404, json={})
        return httpx.Response(200, json={"fields": {"security": None}})  # public, exists
    src, client = _src(handler)
    sync(src, conn=conn)
    store.put_principal(conn, "any", [])
    store.store({"fingerprint": "fp-j3", "body": {"fix": "x"}}, ["jira:MEDIA-113"], conn=conn)
    assert retrieve.retrieve("any", {"fingerprint": "fp-j3"}, conn=conn).hits       # public ok
    state["mode"] = "404"
    sync(src, conn=conn)                                   # source revoked -> fan out
    client.close()
    assert retrieve.retrieve("any", {"fingerprint": "fp-j3"}, conn=conn).hits == []


def test_jira_outage_fails_closed(conn):
    ok, client_ok = _src(lambda _r: httpx.Response(
        200, json={"fields": {"security": {"id": "10000", "name": "R"}}}))
    sync(ok, conn=conn)
    client_ok.close()
    cid = store.ensure_constraint(conn, "jira", "issue-security:10000", "Rights Ops")
    store.put_principal(conn, "rights", [cid])
    store.store({"fingerprint": "fp-j4", "body": {"fix": "x"}}, ["jira:MEDIA-113"], conn=conn)
    assert retrieve.retrieve("rights", {"fingerprint": "fp-j4"}, conn=conn).hits    # readable

    bad, client_bad = _src(lambda _r: httpx.Response(500, json={}))
    res = sync(bad, conn=conn)                             # outage
    client_bad.close()
    assert res["available"] is False
    assert retrieve.retrieve("rights", {"fingerprint": "fp-j4"}, conn=conn).hits == []  # dark


def test_jira_no_credentials_unavailable(conn):
    src = JiraPermissionSource(env={})
    assert src.configured is False
    assert sync(src, conn=conn)["available"] is False


def test_jira_never_leaks_token(conn):
    token = "SUPER-SECRET-TOKEN-42"
    env = dict(JENV, JIRA_API_TOKEN=token)
    src, client = _src(lambda _r: httpx.Response(500, json={"error": "boom"}), env=env)
    res = sync(src, conn=conn)
    client.close()
    audit_blob = "".join(r["payload"] or "" for r in conn.execute("SELECT payload FROM audit_log"))
    assert token not in json.dumps(res)
    assert token not in audit_blob
    assert token not in str(res.get("reason", ""))
