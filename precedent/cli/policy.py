"""`precedent policy` CLI — author-side tooling for the deterministic policy pack.

Subcommands:
  precedent policy lint [PACK ...]   Validate action classes. With no PACK, lints the shipped
                                     packs (policy_pack.yaml + policy_pack_actions.yaml).
                                     Exit 0 = clean, 1 = at least one violation.

CLI-only by design: the pack is never edited in the running console. No LLM, no network —
the lint is a pure deterministic checker (precedent/policy_lint.py).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from precedent import policy_lint


def _cmd_lint(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="precedent policy lint",
        description="Reject any executable action class lacking a TRUE inverse or a "
                    "verification probe (credential rotations / password resets stay "
                    "rejected — §2.5).")
    ap.add_argument("packs", nargs="*", type=Path,
                    help="policy pack YAML files (default: the shipped packs)")
    ns = ap.parse_args(argv)

    paths = ns.packs or policy_lint.default_pack_paths()
    all_violations = []
    checked = 0
    for path in paths:
        checked += 1
        all_violations.extend(policy_lint.lint_file(path))

    if all_violations:
        print(f"policy lint: {len(all_violations)} violation(s) across {checked} pack(s):\n",
              file=sys.stderr)
        for v in all_violations:
            print(v.render(), file=sys.stderr)
        print("\nFAIL — fix the classes above or make them non-executable.", file=sys.stderr)
        return 1

    names = ", ".join(Path(p).name for p in paths)
    print(f"policy lint: OK — {checked} pack(s) clean ({names}).")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    ap = argparse.ArgumentParser(
        prog="precedent policy",
        description="Precedent policy-pack authoring tools (CLI-only).")
    ap.add_argument("subcommand", nargs="?", choices=["lint"],
                    help="the policy operation to run")

    # Support both `precedent policy lint ...` and (as the console_scripts entry) a bare
    # `policy lint ...`. Strip a leading literal 'policy' token if present so the same main()
    # works whether the entry point is `precedent = ...` or `precedent-policy = ...`.
    if argv and argv[0] == "policy":
        argv = argv[1:]

    if not argv:
        ap.print_help()
        return 2
    sub, rest = argv[0], argv[1:]
    if sub == "lint":
        return _cmd_lint(rest)
    ap.error(f"unknown subcommand {sub!r} (expected: lint)")
    return 2  # pragma: no cover - argparse.error exits


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
