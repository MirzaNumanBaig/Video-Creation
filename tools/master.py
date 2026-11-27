#!/usr/bin/env python3
"""Master CLI: registry status, submodule sync, task routing, agent handoffs.

Stdlib only. Reads master.json at the repo root.

  python3 tools/master.py status
  python3 tools/master.py sync [name ...]
  python3 tools/master.py route "audit the xplorekit site and write 3 reels"
  python3 tools/master.py handoff new --from A --to B --subject S [--body B] [--ref PATH]
  python3 tools/master.py handoff list [--to B] [--status open|done|all]
  python3 tools/master.py handoff done ID [--note N]
  python3 tools/master.py validate
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "master.json"
QUEUE = ROOT / "handoffs" / "queue"
HUMAN = {"owner", "master"}  # valid handoff endpoints besides agents


def load(registry: Path | None = None) -> dict:
    return json.loads((registry or REGISTRY).read_text(encoding="utf-8"))


def git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


# ---------------------------------------------------------------- status
def pinned_sha(path: str, root: Path = ROOT) -> str | None:
    rc, out = git("ls-files", "-s", "--", path, cwd=root)  # index: works before the first commit too
    m = re.match(r"160000 ([0-9a-f]{40}) 0\t", out) if rc == 0 else None
    return m.group(1) if m else None


def repo_state(name: str, r: dict, root: Path = ROOT) -> dict:
    status = r.get("status", "?")
    path = r.get("path")
    if not path:
        return {"name": name, "state": status, "detail": "not installed (" + status + ")"}
    full = root / path
    pinned = pinned_sha(path, root)
    if pinned is None:  # vendored plain files
        ok = full.is_dir() and any(full.iterdir())
        return {"name": name, "state": "vendored" if ok else "MISSING", "detail": path}
    if not (full / ".git").exists():
        return {"name": name, "state": "not-synced", "detail": f"pinned {pinned[:7]}; run: master.py sync {name}"}
    rc, head = git("rev-parse", "HEAD", cwd=full)
    _, dirty = git("status", "--porcelain", cwd=full)
    if head != pinned:
        st = "moved"
    else:
        st = "ok"
    if dirty:
        st += "+dirty"
    return {"name": name, "state": st, "detail": f"head {head[:7]} pinned {pinned[:7]}"}


def cmd_status(a, reg):
    rows = [repo_state(n, r) for n, r in reg["repos"].items()]
    w = max(len(r["name"]) for r in rows)
    for r in rows:
        agent = reg["repos"][r["name"]].get("agent") or "-"
        print(f"{r['name']:<{w}}  {r['state']:<14} {agent:<20} {r['detail']}")
    bad = [r for r in rows if r["state"] == "MISSING"]
    return 1 if bad else 0


# ---------------------------------------------------------------- sync
def cmd_sync(a, reg):
    names = a.names or [n for n, r in reg["repos"].items() if r.get("path") and pinned_sha(r["path"])]
    rc_all = 0
    for n in names:
        r = reg["repos"].get(n)
        if not r or not r.get("path") or not pinned_sha(r["path"]):
            print(f"skip {n}: not a submodule")
            continue
        rc, out = git("submodule", "update", "--init", "--depth", "1", "--", r["path"])
        print(f"{'ok  ' if rc == 0 else 'FAIL'} {n}" + ("" if rc == 0 else f": {out.splitlines()[-1] if out else ''}"))
        rc_all |= rc != 0
    return rc_all


# ---------------------------------------------------------------- route
def tokens(text: str) -> str:
    """Lowercase words with a crude plural strip so 'reels' matches 'reel'."""
    words = re.sub(r"[^a-z0-9+]+", " ", text.lower()).split()
    return " " + " ".join(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w for w in words) + " "


def route(text: str, reg: dict, top: int = 5) -> list[dict]:
    """Score each repo by keyword hits (multi-word keywords weigh more) and repo name hits."""
    t = tokens(text)
    out = []
    for name, r in reg["repos"].items():
        score, hits = 0.0, []
        for kw in r.get("keywords", []):
            k = tokens(kw)
            if k in t:
                w = 1.0 + 0.5 * (len(k.split()) - 1)
                score += w
                hits.append(kw)
        if tokens(name.replace("-", " ")) in t:
            score += 2
            hits = [h for h in hits if h != name] + [name]
        if score:
            out.append({"repo": name, "agent": r.get("agent"), "score": score, "hits": hits})
    out.sort(key=lambda x: (-x["score"], x["repo"]))
    return out[:top]


def cmd_route(a, reg):
    res = route(" ".join(a.text), reg)
    if not res:
        print("no match: ask the owner or use repo-scout")
        return 0
    for r in res:
        print(f"{r['score']:>4.1f}  {r['repo']:<26} -> {r['agent'] or '(no agent)':<20} [{', '.join(r['hits'])}]")
    return 0


# ---------------------------------------------------------------- handoff
def valid_endpoints(reg: dict) -> set[str]:
    return set(reg.get("agents", {})) | HUMAN


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "item"


def new_handoff(reg: dict, frm: str, to: str, subject: str, body: str = "", ref: str = "",
                queue: Path = QUEUE, now: datetime | None = None) -> dict:
    ok = valid_endpoints(reg)
    for who in (frm, to):
        if who not in ok:
            raise ValueError(f"unknown endpoint '{who}'. Valid: {', '.join(sorted(ok))}")
    now = now or datetime.now(timezone.utc)
    hid = f"{now:%Y%m%dT%H%M%S}-{slug(to)}-{slug(subject)}"
    item = {"id": hid, "from": frm, "to": to, "subject": subject, "body": body, "ref": ref,
            "status": "open", "created": now.isoformat(timespec="seconds"), "closed": None, "note": ""}
    queue.mkdir(parents=True, exist_ok=True)
    p = queue / f"{hid}.json"
    if p.exists():
        raise ValueError(f"handoff {hid} already exists")
    p.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    return item


def list_handoffs(queue: Path = QUEUE, to: str | None = None, status: str = "open") -> list[dict]:
    items = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(queue.glob("*.json"))] if queue.exists() else []
    return [i for i in items if (not to or i["to"] == to) and (status == "all" or i["status"] == status)]


def close_handoff(hid: str, note: str = "", queue: Path = QUEUE, now: datetime | None = None) -> dict:
    p = queue / f"{hid}.json"
    if not p.exists():
        raise ValueError(f"no such handoff: {hid}")
    item = json.loads(p.read_text(encoding="utf-8"))
    if item["status"] == "done":
        raise ValueError(f"{hid} is already done")
    item.update(status="done", note=note, closed=(now or datetime.now(timezone.utc)).isoformat(timespec="seconds"))
    p.write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
    return item


def cmd_handoff(a, reg):
    try:
        if a.action == "new":
            i = new_handoff(reg, a.frm, a.to, a.subject, a.body, a.ref)
            print(i["id"])
        elif a.action == "list":
            for i in list_handoffs(to=a.to, status=a.status):
                print(f"{i['id']}  {i['from']} -> {i['to']}  [{i['status']}]  {i['subject']}")
        elif a.action == "done":
            print("closed", close_handoff(a.id, a.note)["id"])
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


# ---------------------------------------------------------------- validate
def validate(reg: dict, root: Path = ROOT) -> list[str]:
    errs: list[str] = []
    agents = set(reg.get("agents", {}))
    gm = (root / ".gitmodules").read_text(encoding="utf-8") if (root / ".gitmodules").exists() else ""
    for name, r in reg["repos"].items():
        for f in ("summary", "status"):
            if not r.get(f):
                errs.append(f"{name}: missing {f}")
        ag = r.get("agent")
        if ag and ag not in agents:
            errs.append(f"{name}: agent '{ag}' not in registry agents")
        if r.get("status") in ("active", "vendored") and not ag:
            errs.append(f"{name}: active repo without an agent")
        p = r.get("path")
        if p and pinned_sha(p, root) and f'path = {p}' not in gm:
            errs.append(f"{name}: gitlink {p} missing from .gitmodules")
    for a in agents:
        if not (root / ".claude" / "agents" / f"{a}.md").exists():
            errs.append(f"agent '{a}': .claude/agents/{a}.md missing")
    ids = {r_id for r_id in reg["repos"]}
    for fl in reg.get("flows", []):
        for end in (fl["from"], fl["to"]):
            if ":" not in end and end not in ids:
                errs.append(f"flow {fl['id']}: unknown repo '{end}'")
    return errs


def cmd_validate(a, reg):
    errs = validate(reg)
    for e in errs:
        print("ERROR", e)
    print("registry OK" if not errs else f"{len(errs)} problem(s)")
    return 1 if errs else 0


# ---------------------------------------------------------------- main
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="master.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status").set_defaults(fn=cmd_status)
    s = sp.add_parser("sync"); s.add_argument("names", nargs="*"); s.set_defaults(fn=cmd_sync)
    r = sp.add_parser("route"); r.add_argument("text", nargs="+"); r.set_defaults(fn=cmd_route)
    h = sp.add_parser("handoff"); h.set_defaults(fn=cmd_handoff)
    hs = h.add_subparsers(dest="action", required=True)
    n = hs.add_parser("new"); n.add_argument("--from", dest="frm", required=True); n.add_argument("--to", required=True)
    n.add_argument("--subject", required=True); n.add_argument("--body", default=""); n.add_argument("--ref", default="")
    l = hs.add_parser("list"); l.add_argument("--to"); l.add_argument("--status", default="open", choices=["open", "done", "all"])
    d = hs.add_parser("done"); d.add_argument("id"); d.add_argument("--note", default="")
    sp.add_parser("validate").set_defaults(fn=cmd_validate)
    return p


def main(argv=None) -> int:
    a = parser().parse_args(argv)
    return a.fn(a, load())


if __name__ == "__main__":
    sys.exit(main())
