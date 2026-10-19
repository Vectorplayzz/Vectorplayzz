#!/usr/bin/env python3
"""Fill in the GitHub profile fields and each repo's About box.

Recruiters skim the pinned cards, and a card with "No description" reads as
unfinished. This sets the description, website and topics on every repo worth
showing, plus the profile name / bio / location / website.

Safe by default:
  * Dry run unless you pass --apply. It prints every change first.
  * Only edits metadata. It never deletes, archives, renames or changes
    visibility of anything.
  * Uses your own `gh` login; no tokens are read, stored or printed here.

Requirements: GitHub CLI (https://cli.github.com) logged in as Vectorplayzz.
Profile fields need the `user` scope once:   gh auth refresh -h github.com -s user

Usage:
  python3 scripts/polish_repos.py              # preview
  python3 scripts/polish_repos.py --apply      # repos + profile
  python3 scripts/polish_repos.py --apply --repos-only
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

OWNER = "Vectorplayzz"

PROFILE = {
    # Kept deliberately free of personal details: no real name, location or dates.
    "name": "Vector",
    "bio": "I build AI agents, ship full-stack apps and run the servers they live on.",
    "location": "",  # empty clears any location already set
    "blog": "https://nagarjuna.ourspaces.net",
    "hireable": True,
}

REPOS: dict[str, dict] = {
    "sitrep-incident-commander": {
        "description": "Autonomous incident commander: investigates production incidents with "
                       "statistics, delegates to subagents, and stops for human approval before "
                       "touching prod. Built on TrueForge.",
        "homepage": "",
        "topics": ["ai-agents", "aiops", "incident-response", "mcp", "sre", "llm",
                   "human-in-the-loop", "python", "docker", "hackathon"],
    },
    "devops-failure-recovery-agent": {
        "description": "OpsLoop: chat-driven SRE agent that diagnoses from cited evidence, gates "
                       "fixes on human approval, then verifies recovery held and rolls back if not.",
        "homepage": "",
        "topics": ["ai-agents", "aiops", "sre", "devops", "llm", "prompt-injection",
                   "discord-bot", "observability", "python"],
    },
    "cognify": {
        "description": "AI learning platform: any topic becomes lessons, quizzes and coding "
                       "practice with an AI tutor. Self-hosted RAG, sandboxed code runner, web search.",
        "homepage": "https://cognify.ourspaces.net",
        "topics": ["edtech", "rag", "llm", "ollama", "react", "nodejs", "mysql",
                   "code-execution", "self-hosted", "typescript"],
    },
    "clutchr": {
        "description": "Esports tournament platform: teams, matches, leaderboards and a wallet, "
                       "with JWT auth, role-based access and rate limiting.",
        "homepage": "https://clutchr.ourspaces.net",
        "topics": ["esports", "tournament", "typescript", "express", "prisma", "react",
                   "mysql", "rbac", "jwt"],
    },
    "minimart": {
        "description": "Multi-branch retail inventory system: stock transfers, role-based views, "
                       "reports and demand forecasting.",
        "homepage": "https://minimart.ourspaces.net",
        "topics": ["inventory-management", "forecasting", "react", "express", "mysql",
                   "flask", "rbac", "dashboard"],
    },
    "worst-captcha": {
        "description": "CAPTCHA Pro: the world's most frustrating verification. A joke, and a tour "
                       "of the dark patterns real products use.",
        "homepage": "",
        "topics": ["captcha", "dark-patterns", "ux", "react", "zustand", "web-audio-api",
                   "framer-motion", "humor"],
    },
}

TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def validate() -> None:
    errors = []
    if len(PROFILE["bio"]) > 160:
        errors.append(f"bio is {len(PROFILE['bio'])} chars (GitHub max 160)")
    for repo, meta in REPOS.items():
        if len(meta["description"]) > 350:
            errors.append(f"{repo}: description over 350 chars")
        if len(meta["topics"]) > 20:
            errors.append(f"{repo}: more than 20 topics")
        for t in meta["topics"]:
            if not TOPIC_RE.match(t):
                errors.append(f"{repo}: bad topic {t!r}")
        if meta["homepage"] and not meta["homepage"].startswith("https://"):
            errors.append(f"{repo}: homepage must be https")
    if errors:
        sys.exit("Config errors:\n  " + "\n  ".join(errors))


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    # List form, never shell=True: no value here is ever interpreted by a shell.
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=check)


def preflight() -> None:
    if shutil.which("gh") is None:
        sys.exit("GitHub CLI not found. Install it from https://cli.github.com")
    who = gh("api", "user", "--jq", ".login", check=False)
    if who.returncode != 0:
        sys.exit("Not logged in. Run: gh auth login")
    if who.stdout.strip().lower() != OWNER.lower():
        sys.exit(f"Logged in as {who.stdout.strip()!r}, expected {OWNER!r}. Switch with: gh auth switch")


def current_repo(repo: str) -> dict | None:
    res = gh("repo", "view", f"{OWNER}/{repo}", "--json",
             "description,homepageUrl,repositoryTopics", check=False)
    if res.returncode != 0:
        return None
    data = json.loads(res.stdout)
    topics = [t["name"] for t in (data.get("repositoryTopics") or [])]
    return {"description": data.get("description") or "",
            "homepage": data.get("homepageUrl") or "", "topics": topics}


def polish_repos(apply: bool) -> int:
    failures = 0
    for repo, want in REPOS.items():
        have = current_repo(repo)
        if have is None:
            print(f"  ! {repo}: not found or not accessible, skipped")
            failures += 1
            continue
        args = []
        if have["description"] != want["description"]:
            args += ["--description", want["description"]]
        if have["homepage"].rstrip("/") != want["homepage"].rstrip("/"):
            args += ["--homepage", want["homepage"]]
        add = [t for t in want["topics"] if t not in have["topics"]]
        for t in add:
            args += ["--add-topic", t]
        if not args:
            print(f"  = {repo}: already up to date")
            continue
        print(f"  ~ {repo}: description/homepage/topics (+{len(add)} topics)")
        if apply:
            res = gh("repo", "edit", f"{OWNER}/{repo}", *args, check=False)
            if res.returncode != 0:
                print(f"    failed: {res.stderr.strip()}")
                failures += 1
    return failures


def polish_profile(apply: bool) -> int:
    print(f"  ~ profile: name={PROFILE['name']!r}, location={PROFILE['location']!r}, "
          f"website={PROFILE['blog']!r}, hireable={PROFILE['hireable']}")
    print(f"    bio ({len(PROFILE['bio'])}/160): {PROFILE['bio']}")
    if not apply:
        return 0
    res = gh("api", "-X", "PATCH", "user",
             "-f", f"name={PROFILE['name']}",
             "-f", f"bio={PROFILE['bio']}",
             "-f", f"location={PROFILE['location']}",
             "-f", f"blog={PROFILE['blog']}",
             "-F", f"hireable={'true' if PROFILE['hireable'] else 'false'}",
             check=False)
    if res.returncode != 0:
        print("    failed. If it mentions scopes, run: gh auth refresh -h github.com -s user")
        print(f"    {res.stderr.strip()}")
        return 1
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--apply", action="store_true", help="make the changes (default is a dry run)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--repos-only", action="store_true")
    g.add_argument("--profile-only", action="store_true")
    a = p.parse_args()

    validate()
    preflight()
    print("APPLYING changes" if a.apply else "DRY RUN (nothing will change; add --apply)")
    failures = 0
    if not a.profile_only:
        print("Repositories:")
        failures += polish_repos(a.apply)
    if not a.repos_only:
        print("Profile:")
        failures += polish_profile(a.apply)
    print("Done." if failures == 0 else f"Finished with {failures} problem(s).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
