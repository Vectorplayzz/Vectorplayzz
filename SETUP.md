# Putting the new profile live

About 10 minutes. Everything here goes in a new public repo named exactly **`Vectorplayzz`** (same as your username). GitHub shows that repo's README at the top of your profile.

## 1. Create the profile repo and push

```bash
gh repo create Vectorplayzz/Vectorplayzz --public --description "Profile README"
cd github-profile            # this folder, unzipped
git init -b main
git add .
git commit -m "Profile README"
git remote add origin https://github.com/Vectorplayzz/Vectorplayzz.git
git push -u origin main
```

(Or create the repo on github.com and upload the files. Keep the folder layout: `assets/`, `scripts/`, `.github/workflows/`.)

## 2. Start the snake

The snake image comes from a GitHub Action that redraws it daily.

1. Repo **Settings → Actions → General → Workflow permissions**: leave it on **Read repository contents** (the workflow asks for write access for its own job only).
2. **Actions** tab → **snake** → **Run workflow**. It takes under a minute and creates an `output` branch with the light and dark snake images.

Until that first run finishes, the snake at the bottom shows as a broken image. After that it updates itself every morning.

## 3. Fill in your profile and repo descriptions

Every one of your repos currently says "No description, website, or topics provided", which is the first thing a recruiter sees on a pinned card. The script fixes all of them and your profile fields in one go.

```bash
gh auth refresh -h github.com -s user        # once, lets gh edit your profile
python3 scripts/polish_repos.py              # preview, changes nothing
python3 scripts/polish_repos.py --apply      # apply
```

It only edits descriptions, websites, topics and profile text. It never deletes, archives or changes visibility. Edit the text at the top of the script if you want different wording.

If you'd rather do the profile by hand (**github.com → your avatar → Settings → Public profile**):

| Field | Value |
| :-- | :-- |
| Name | Vector |
| Bio | I build AI agents, ship full-stack apps and run the servers they live on. |
| Location | (leave empty) |
| URL | https://nagarjuna.ourspaces.net |
| Social | LinkedIn: https://www.linkedin.com/in/goddindla-nagarjuna/ |
| Available for hire | On |

## 4. Pin your best six (manual, GitHub has no API for this)

Profile page → **Customize your pins**, in this order:

1. sitrep-incident-commander
2. devops-failure-recovery-agent
3. cognify
4. clutchr
5. minimart
6. worst-captcha

## 5. Small cleanups worth doing

- **TrueForge-Hackathon** is empty (0 files). An empty public repo looks abandoned. Make it private or delete it; SITREP is the real entry.
- **jokerbot** (2019) and **vectorplayzz.github.io** (2021) are fine to keep, just don't pin them.

## Changing the page

Most of the README is plain text: edit README.md directly.

The header, link buttons, section headings, About tiles, project cards, live-demo buttons and toolbox are generated in light and dark versions. Their content lives at the top of `scripts/build_assets.py` (`HEADER`, `ABOUT`, `HEADINGS`, `LINK_BUTTONS`, `LIVE_BUTTONS`, `CARDS`, `TOOLBOX`). Edit it, then run:

```bash
python3 scripts/build_assets.py
```

Commit the updated `assets/` folder, and update the matching `alt` text in README.md, since that is what screen readers and search engines read.

- The header's "now:" line rotates through `HEADER["rotating"]`; keep each phrase short.
- Toolbox items are either a logo slug from `scripts/icons.json` (Simple Icons, CC0) or plain text for a chip without a logo. To add a logo, copy its path and colour from simpleicons.org into `icons.json`.
- The script stops with a clear message if a card description runs past 3 lines or a toolbox row gets too long.
- It needs only Python and makes no network requests. Animations (cursor, rotating line, mosaic shimmer) stop for visitors who prefer reduced motion.

Keep each pair of cards on a single line in README.md with nothing between `</a>` and `<a`, otherwise GitHub inserts a space and the second card drops to the next row.
