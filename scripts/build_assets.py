#!/usr/bin/env python3
"""Generate the profile README images (assets/*.svg), in light and dark themes.

Design: modern and calm, with retro as the accent (pixel wordmark, 8x8 pixel
icons, a contribution-style mosaic). Display type is drawn as pixel paths and
body text uses the system font stack, because GitHub blocks web fonts inside
README images. No scripts, no network requests. Motion is CSS only, kept
subtle, and switched off for visitors who prefer reduced motion.

Logos in the toolbox come from scripts/icons.json (Simple Icons, CC0).

Edit the CONTENT section, then run:   python3 scripts/build_assets.py
Standard library only.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICON_DATA = json.loads((Path(__file__).resolve().parent / "icons.json").read_text())["icons"]
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": {
        "bg": "#0f0b1a", "card": "#140f22", "border": "#2a2142", "dot": "#251d3b",
        "text": "#ece8ff", "muted": "#a39bc2", "accent": "#ff4fd8", "accent2": "#a08fff",
        "ok": "#3ddc84", "shadow": "#2e2150", "grad": ["#ff4fd8", "#b46cff", "#3ef0ff"],
        "ramp": ["#1a1430", "#2c2150", "#4b3a99", "#8b4fd6", "#ff4fd8"],
    },
    "light": {
        "bg": "#fbfaff", "card": "#ffffff", "border": "#e4defc", "dot": "#e7e1fb",
        "text": "#1d1530", "muted": "#5f5878", "accent": "#c4198d", "accent2": "#5a43e6",
        "ok": "#1a7f37", "shadow": "#e4dafd", "grad": ["#c4198d", "#6a3de8", "#0b7f8f"],
        "ramp": ["#f1edff", "#e0d7fe", "#c3b3fb", "#9f7cf0", "#e05cc0"],
    },
}

# ── 5x7 pixel font (display type only) ────────────────────────────────────
FONT = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
}


def pixel_text(text: str, x: float, y: float, s: int) -> str:
    out = []
    for i, ch in enumerate(text):
        for r, line in enumerate(FONT[ch]):
            c = 0
            while c < 5:
                if line[c] != "#":
                    c += 1
                    continue
                e = c
                while e < 5 and line[e] == "#":
                    e += 1
                out.append(f"M{x + i * 6 * s + c * s} {y + r * s}h{(e - c) * s}v{s}h-{(e - c) * s}z")
                c = e
    return "".join(out)


def pixel_icon(rows: list[str], x: float, y: float, s: float) -> str:
    return "".join(f"M{x + c * s} {y + r * s}h{s}v{s}h-{s}z"
                   for r, row in enumerate(rows) for c, ch in enumerate(row) if ch == "#")


def t(x: float, y: float, text: str, size: float, fill: str, weight: int = 400,
      family: str = SANS, anchor: str = "start", spacing: float = 0, cls: str = "") -> str:
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<text{c} x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{ls}>{escape(text)}</text>')


def wrap(text: str, max_chars: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + ([cur] if cur else [])


def luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def doc(w: int, h: int, title: str, desc: str, body: str, css: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d">\n<title id="t">{escape(title)}</title>\n'
            f'<desc id="d">{escape(desc)}</desc>\n<style>{css}</style>\n{body}\n</svg>\n')


# ── CONTENT ───────────────────────────────────────────────────────────────
HEADER = {
    "name": "VECTORPLAYZZ",
    "kicker": "AI ENGINEER  \u00b7  AGENTS  \u00b7  INFRA",
    "tagline": ["I build AI agents, and the", "infrastructure that keeps them honest."],
    "rotating": ["fine-tuning LLMs", "building agents that ask before acting", "running my own servers"],
}

ICONS = {
    "alert": ["..####..", ".#....#.", "#..##..#", "#..##..#", "#......#", "#..##..#", ".#....#.", "..####.."],
    "loop": ["..####..", ".#....#.", "#......#", "#....###", "###....#", "#......#", ".#....#.", "..####.."],
    "book": ["........", "###..###", "#..##..#", "#..##..#", "#..##..#", "#..##..#", "########", "........"],
    "trophy": ["########", "#.####.#", "#.####.#", ".######.", "..####..", "...##...", "..####..", ".######."],
    "star": ["...##...", "...##...", "########", ".######.", "..####..", ".##..##.", ".#....#.", "........"],
    "wrench": [".##.....", "#..#....", "#..#....", ".####...", "....##..", ".....##.", "......##", ".......#"],
    "user": ["..####..", ".######.", ".######.", "..####..", "........", ".######.", "########", "########"],
    "check": ["........", ".......#", "......##", "#....##.", "##..##..", ".####...", "..##....", "........"],
    "window": ["########", "#.#.#..#", "########", "#......#", "#.##...#", "#......#", "#.####.#", "########"],
    "server": ["########", "#......#", "#.#....#", "########", "#......#", "#.#....#", "########", "........"],
    "globe": ["..####..", ".#.##.#.", "#..##..#", "########", "#..##..#", "#..##..#", ".#.##.#.", "..####.."],
    "play": ["#.......", "##......", "###.....", "####....", "###.....", "##......", "#.......", "........"],
}

CARDS = [
    {
        "file": "card-sitrep", "icon": "alert", "tag": "HACKATHON \u00b7 AGENT", "title": "SITREP",
        "desc": "On-call agent that investigates incidents end to end, proves the root cause "
                "with statistics, and stops for a human before touching prod.",
        "metric": "77s to root cause \u00b7 4 approval gates",
        "stack": [("Python", "#3572A5"), ("MCP", "#8b78ff"), ("SciPy", "#0b7f8f")],
    },
    {
        "file": "card-opsloop", "icon": "loop", "tag": "AGENT \u00b7 SRE", "title": "OpsLoop",
        "desc": "SRE agent that doesn't stop at \u201cfix applied\u201d. It checks that health actually "
                "held, and rolls back on its own when it didn't.",
        "metric": "98 tests \u00b7 injection-hardened logs",
        "stack": [("Python", "#3572A5"), ("Discord", "#5865F2"), ("Loki", "#e8a33d")],
    },
    {
        "file": "card-cognify", "icon": "book", "tag": "LIVE \u00b7 FULL STACK", "title": "Cognify",
        "desc": "Learning platform that turns any topic into lessons, quizzes and coding practice, "
                "with self-hosted RAG and a sandboxed code runner.",
        "metric": "94 roadmaps \u00b7 7 sandboxed languages",
        "stack": [("TypeScript", "#3178c6"), ("React", "#1fa8c9"), ("Ollama", "#7a7a7a")],
    },
    {
        "file": "card-clutchr", "icon": "trophy", "tag": "LIVE \u00b7 FULL STACK", "title": "ClutchR",
        "desc": "Esports tournament platform with teams, matches, leaderboards and a wallet, "
                "behind JWT auth, role-based access and rate limits.",
        "metric": "11 data models \u00b7 3 roles",
        "stack": [("TypeScript", "#3178c6"), ("Express", "#8a8a8a"), ("Prisma", "#5a67d8")],
    },
]

# Each item is a Simple Icons slug (from icons.json) or plain text for a chip without a logo.
TOOLBOX = [
    ("AI / ML", ["python", "pytorch", "huggingface", "pandas", "scipy"]),
    ("AGENTS", ["modelcontextprotocol", "ollama", "RAG", "Approval gates"]),
    ("WEB", ["typescript", "react", "nodedotjs", "express", "prisma", "MySQL"]),
    ("INFRA", ["linux", "docker", "nginx", "systemd / PM2"]),
    ("CLOUD / CI", ["googlecloud", "cloudflare", "githubactions"]),
]
SHORT_NAMES = {"modelcontextprotocol": "MCP", "nodedotjs": "Node.js", "googlecloud": "Google Cloud",
               "githubactions": "GitHub Actions", "huggingface": "Hugging Face"}

ABOUT = [
    ("check", "Agents that ask first",
     "Evidence before conclusions, and a human approval before anything that can't be undone."),
    ("window", "Ship the whole thing",
     "Not just the model: the API, the interface, auth and the tests around it."),
    ("server", "Run what I build",
     "Every live demo runs on servers I set up, harden and keep alive myself."),
]

HEADINGS = {"about": ("user", "About"), "work": ("star", "Featured work"), "toolbox": ("wrench", "Toolbox")}

# (file, label, icon). README links each button; nothing personal is drawn in the images.
LINK_BUTTONS = [("btn-portfolio", "Portfolio", "globe"), ("btn-linkedin", "LinkedIn", "user")]
LIVE_BUTTONS = [("btn-cognify", "Play Cognify", "play"), ("btn-clutchr", "Play ClutchR", "play"),
                ("btn-minimart", "Play MiniMart", "play")]


# ── IMAGES ────────────────────────────────────────────────────────────────
MOTION_CSS = (
    ".cur{animation:blink 1.1s steps(1) infinite}"
    "@keyframes blink{50%{opacity:0}}"
    ".cell{animation:pulse 5s ease-in-out infinite}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}"
    ".rot{opacity:0;animation:rot 9s infinite}"
    "@keyframes rot{0%{opacity:0;transform:translateY(5px)}4%,30%{opacity:1;transform:none}34%,100%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){.cur,.cell,.rot{animation:none}.rot.first{opacity:1}}"
)


def header(th: dict) -> str:
    W, H = 840, 262
    rng = random.Random(42)
    cells, cs, gap, cols, rows = [], 12, 4, 15, 11
    x0, y0 = W - 32 - cols * (cs + gap) + gap, (H - rows * (cs + gap) + gap) // 2
    for c in range(cols):
        wgt = c / (cols - 1)
        for r in range(rows):
            if rng.random() < 0.18 * (1 - wgt):
                continue
            level = min(4, int((rng.random() ** 1.5) * 5 * (0.3 + wgt)))
            cells.append(f'<rect class="cell" style="animation-delay:{c * 0.18 + r * 0.05:.2f}s" '
                         f'x="{x0 + c * (cs + gap)}" y="{y0 + r * (cs + gap)}" width="{cs}" height="{cs}" '
                         f'rx="2" fill="{th["ramp"][level]}"/>')
    s, nx, ny = 6, 40, 82
    name_w = len(HEADER["name"]) * 6 * s - s
    g = th["grad"]
    rot_y = 232
    rot = t(nx, rot_y, "now:", 14, th["muted"], 500, MONO)
    for i, phrase in enumerate(HEADER["rotating"]):
        rot += (f'<g class="rot{" first" if i == 0 else ""}" style="animation-delay:{i * 3}s">'
                + t(nx + 44, rot_y, phrase, 14, th["accent2"], 600, MONO) + "</g>")
    body = (
        f'<defs><pattern id="g" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{th["dot"]}"/></pattern>'
        f'<linearGradient id="n" gradientUnits="userSpaceOnUse" x1="{nx}" x2="{nx + name_w}" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{g[0]}"/><stop offset=".55" stop-color="{g[1]}"/>'
        f'<stop offset="1" stop-color="{g[2]}"/></linearGradient>'
        f'<linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="{th["bg"]}" stroke="{th["border"]}"/>'
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#g)"/>'
        f'<g mask="url(#m)">{"".join(cells)}</g>'
        + t(nx, 58, HEADER["kicker"], 12, th["muted"], 500, MONO, spacing=1.2)
        + f'<path fill="{th["shadow"]}" d="{pixel_text(HEADER["name"], nx + 3, ny + 3, s)}" shape-rendering="crispEdges"/>'
        + f'<path fill="url(#n)" d="{pixel_text(HEADER["name"], nx, ny, s)}" shape-rendering="crispEdges"/>'
        + f'<rect class="cur" x="{nx + name_w + 10}" y="{ny}" width="{s * 3}" height="{s * 7}" fill="{g[2]}"/>'
        + t(nx, ny + 7 * s + 42, HEADER["tagline"][0], 21, th["text"], 500)
        + t(nx, ny + 7 * s + 70, HEADER["tagline"][1], 21, th["text"], 500)
        + rot
    )
    desc = (f"{HEADER['name']}. AI engineer: agents and infrastructure. "
            f"{' '.join(HEADER['tagline'])} Now: {'; '.join(HEADER['rotating'])}.")
    return doc(W, H, HEADER["name"], desc, body, MOTION_CSS)


def card(c: dict, th: dict) -> str:
    # Half the README width with a transparent margin: two cards at 50% each
    # sit side by side with a natural gutter.
    W, H, m = 420, 256, 6
    x, y = m + 24, m + 26
    g = th["grad"]
    tile = (f'<rect x="{x - 6}" y="{y - 6}" width="36" height="36" rx="9" fill="{th["bg"]}" stroke="{th["border"]}"/>'
            f'<path fill="{th["accent"]}" d="{pixel_icon(ICONS[c["icon"]], x, y, 3)}" shape-rendering="crispEdges"/>')
    tag_w = len(c["tag"]) * 7.2 + 20
    tx = W - m - 22 - tag_w
    tag = (f'<rect x="{tx}" y="{y}" width="{tag_w}" height="22" rx="11" fill="none" stroke="{th["border"]}"/>'
           + t(tx + tag_w / 2, y + 15, c["tag"], 10.5, th["muted"], 600, MONO, "middle", 0.6))
    title = t(x, y + 64, c["title"], 22, th["text"], 650)
    lines = wrap(c["desc"], 52)
    if len(lines) > 3:
        raise ValueError(f"{c['title']}: description needs {len(lines)} lines, max 3. Shorten it.")
    desc = "".join(t(x, y + 92 + i * 20, ln, 13.5, th["muted"]) for i, ln in enumerate(lines))
    metric = t(x, H - m - 58, c["metric"], 12, th["accent2"], 600, MONO)
    sx, stack = x, []
    for name, color in c["stack"]:
        stack.append(f'<circle cx="{sx + 5}" cy="{H - m - 27}" r="5" fill="{color}"/>'
                     + t(sx + 15, H - m - 22.5, name, 12, th["muted"]))
        sx += 15 + len(name) * 7 + 18
    body = (
        f'<defs><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="{g[0]}"/>'
        f'<stop offset=".55" stop-color="{g[1]}"/><stop offset="1" stop-color="{g[2]}"/></linearGradient>'
        f'<clipPath id="c"><rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" rx="12"/></clipPath></defs>'
        f'<rect x="{m + .5}" y="{m + .5}" width="{W - 2 * m - 1}" height="{H - 2 * m - 1}" rx="12" '
        f'fill="{th["card"]}" stroke="{th["border"]}"/>'
        f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="3" fill="url(#a)" clip-path="url(#c)"/>'
        + tile + tag + title + desc + metric + "".join(stack)
    )
    desc_txt = f"{c['title']}: {c['desc']} {c['metric']}. Built with " + ", ".join(n for n, _ in c["stack"]) + "."
    return doc(W, H, c["title"], desc_txt, body)


def toolbox(th: dict) -> str:
    W, row_h, top = 840, 50, 22
    parts, alt = [], []
    for i, (label, items) in enumerate(TOOLBOX):
        y = top + i * row_h
        parts.append(t(24, y + 22, label, 11, th["muted"], 600, MONO, spacing=1.2))
        cx, names = 120, []
        for item in items:
            icon = ICON_DATA.get(item)
            name = SHORT_NAMES.get(item, icon["title"] if icon else item)
            names.append(name)
            w = 14 + (24 if icon else 12) + len(name) * 7.1 + 14
            if cx + w > W - 16:
                raise ValueError(f"Toolbox row {label!r} is too long; move an item to another row.")
            parts.append(f'<rect x="{cx + .5}" y="{y + .5}" width="{w}" height="33" rx="16.5" '
                         f'fill="{th["card"]}" stroke="{th["border"]}"/>')
            if icon:
                color = icon["hex"] if contrast(icon["hex"], th["card"]) >= 2.4 else th["text"]
                parts.append(f'<g transform="translate({cx + 13} {y + 9}) scale({16 / 24})">'
                             f'<path fill="{color}" d="{icon["path"]}"/></g>')
                tx = cx + 37
            else:
                parts.append(f'<rect x="{cx + 14}" y="{y + 14}" width="6" height="6" fill="{th["accent"]}"/>')
                tx = cx + 26
            parts.append(t(tx, y + 21.5, name, 13, th["text"], 500))
            cx += w + 8
        alt.append(f"{label.title()}: {', '.join(names)}.")
    H = top + len(TOOLBOX) * row_h + 8
    return doc(W, H, "Toolbox", " ".join(alt), "".join(parts))


def heading(key: str, th: dict) -> str:
    icon, label = HEADINGS[key]
    W, H = 840, 52
    g = th["grad"]
    body = (
        f'<defs><linearGradient id="h" x1="0" x2="1"><stop offset="0" stop-color="{g[0]}"/>'
        f'<stop offset=".35" stop-color="{g[1]}" stop-opacity=".6"/><stop offset="1" stop-color="{th["border"]}" stop-opacity="0"/>'
        f'</linearGradient></defs>'
        f'<rect x=".5" y="6.5" width="30" height="30" rx="8" fill="{th["card"]}" stroke="{th["border"]}"/>'
        f'<path fill="{th["accent"]}" d="{pixel_icon(ICONS[icon], 8, 14, 2)}" shape-rendering="crispEdges"/>'
        + t(44, 28.5, label, 20, th["text"], 650)
        + f'<rect x="0" y="{H - 4}" width="{W}" height="2" fill="url(#h)"/>'
    )
    return doc(W, H, label, label, body)


def button(label: str, icon: str, th: dict, w: int = 200) -> str:
    # Drawn with a transparent margin so a row of buttons gets even gaps.
    H, m = 52, 5
    body = (
        f'<rect x="{m + .5}" y="{m + .5}" width="{w - 2 * m - 1}" height="{H - 2 * m - 1}" rx="{(H - 2 * m) / 2}" '
        f'fill="{th["card"]}" stroke="{th["border"]}"/>'
        f'<path fill="{th["accent"]}" d="{pixel_icon(ICONS[icon], 24, 18, 2)}" shape-rendering="crispEdges"/>'
        + t(48, 31, label, 14, th["text"], 600)
        + t(w - 24, 31, "\u2192", 15, th["muted"], 500, anchor="end")
    )
    return doc(w, H, label, label, body)


def about(th: dict) -> str:
    W, H, gap = 840, 148, 14
    tw_ = (W - 2 * gap) / 3
    parts = []
    for i, (icon, title, text) in enumerate(ABOUT):
        x = i * (tw_ + gap)
        lines = wrap(text, 34)
        if len(lines) > 3:
            raise ValueError(f"About tile {title!r} needs {len(lines)} lines, max 3. Shorten it.")
        parts.append(
            f'<rect x="{x + .5}" y=".5" width="{tw_ - 1}" height="{H - 1}" rx="12" fill="{th["card"]}" stroke="{th["border"]}"/>'
            f'<path fill="{th["accent"]}" d="{pixel_icon(ICONS[icon], x + 20, 22, 2.5)}" shape-rendering="crispEdges"/>'
            + t(x + 20, 66, title, 15.5, th["text"], 650)
            + "".join(t(x + 20, 90 + j * 19, ln, 13, th["muted"]) for j, ln in enumerate(lines))
        )
    return doc(W, H, "About", " ".join(f"{a}: {b}" for _, a, b in ABOUT), "".join(parts))


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for old in ASSETS.glob("*.svg"):
        old.unlink()
    files = {}
    for mode, th in THEMES.items():
        files[f"header-{mode}.svg"] = header(th)
        files[f"toolbox-{mode}.svg"] = toolbox(th)
        files[f"about-{mode}.svg"] = about(th)
        for key in HEADINGS:
            files[f"h-{key}-{mode}.svg"] = heading(key, th)
        for name, label, icon in LINK_BUTTONS + LIVE_BUTTONS:
            files[f"{name}-{mode}.svg"] = button(label, icon, th)
        for c in CARDS:
            files[f"{c['file']}-{mode}.svg"] = card(c, th)
    for name, content in files.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(files)} files ({sum(len(v.encode()) for v in files.values()):,} bytes)")


if __name__ == "__main__":
    main()
