"""Structural check for the organisation profile page.

`profile/README.md` in a repository named `.github` is what GitHub renders on the
organisation's front page. It is the first thing a stranger sees, and it is easy to break
without noticing because nothing here is ever built or run.

So "works" means: the page is where GitHub expects it, it is not empty, the asset it embeds
resolves, and every repository it advertises actually exists and is public. That last check
is the one that catches real drift - a repo linked here that has been renamed or made
private renders as a dead link on the org front page.

Standard library only, so it runs anywhere with no install step.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "profile" / "README.md"

failures: list[str] = []
UA = {"User-Agent": "cdi-verify/1.0"}


def head_ok(url: str) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="HEAD", headers=UA)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return (resp.status == 200, f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        return (False, f"HTTP {e.code}")
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")


# --- GitHub renders profile/README.md and nothing else -------------------
if not PAGE.exists():
    print("FAIL profile/README.md missing - GitHub renders that exact path and nothing else")
    sys.exit(1)

text = PAGE.read_text(encoding="utf-8")
if len(text.strip()) < 200:
    failures.append("profile page is under 200 characters")
if not re.search(r"(?m)^#\s+\S", text):
    failures.append("no top-level heading")

# --- the embedded asset must resolve -------------------------------------
assets = sorted(set(re.findall(r"https://assets\.carpedieminnovationsinc\.com/[^\s\"')>]+", text)))
for url in assets:
    ok, why = head_ok(url)
    print(("ok  " if ok else "FAIL ") + url + ("" if ok else f" -> {why}"))
    if not ok:
        failures.append(f"{url} -> {why}")

# --- every repository advertised here must exist and be public -----------
repos = sorted(set(re.findall(r"https://github\.com/([\w.-]+)/([\w.-]+)", text)))
for owner, name in repos:
    name = name.rstrip(").,")
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{name}", headers=UA)
        with urllib.request.urlopen(req, timeout=20) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
        if meta.get("private"):
            failures.append(f"{owner}/{name} is PRIVATE but linked from the public org page")
        else:
            print(f"ok  {owner}/{name} (public)")
    except urllib.error.HTTPError as e:
        failures.append(f"{owner}/{name} -> HTTP {e.code} (renamed, deleted, or private)")
    except Exception as e:
        failures.append(f"{owner}/{name} -> {type(e).__name__}: {e}")

print(f"checked: {len(assets)} asset URL(s), {len(repos)} repository link(s)")
for f in failures:
    print(f"  FAIL {f}")
sys.exit(1 if failures else 0)
