"""Render the profile stats and top-languages cards as light and dark SVGs.

Standard library only. Reads a token from STATS_TOKEN or GITHUB_TOKEN and
counts public, non-fork repositories owned by the user.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

LOGIN = os.environ.get("STATS_LOGIN", "Alexvolkihar")
OUT = Path(os.environ.get("STATS_OUT", "assets"))
TOP_LANGUAGES = 6
EXCLUDED_LANGUAGES = {"Jupyter Notebook"}

THEMES = {
    "light": {
        "bg": "#f6faf8", "border": "#d3e2db", "title": "#13201b",
        "text": "#3d4f48", "muted": "#6b7f77", "accent": "#1f8a66",
    },
    "dark": {
        "bg": "#0f1714", "border": "#24352e", "title": "#e7f1ed",
        "text": "#b9cbc3", "muted": "#7f978d", "accent": "#4fc08d",
    },
}

FONT = ("ui-sans-serif, -apple-system, 'Segoe UI', 'Noto Sans', Helvetica, "
        "Arial, sans-serif")

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    pullRequests { totalCount }
    contributionsCollection { totalCommitContributions }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER,
                 isFork: false, privacy: PUBLIC) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def graphql(token, variables):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "User-Agent": "profile-stats-card"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def collect(token):
    after = None
    stars = 0
    languages = {}
    while True:
        user = graphql(token, {"login": LOGIN, "after": after})
        repos = user["repositories"]
        for repo in repos["nodes"]:
            stars += repo["stargazerCount"]
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                if name in EXCLUDED_LANGUAGES:
                    continue
                size, color = languages.get(name, (0, edge["node"]["color"]))
                languages[name] = (size + edge["size"], color or "#8b949e")
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]
    return {
        "stars": stars,
        "repos": user["repositories"]["totalCount"],
        "commits": user["contributionsCollection"]["totalCommitContributions"],
        "prs": user["pullRequests"]["totalCount"],
        "languages": languages,
    }


def card(theme, title, body, height, label):
    t = THEMES[theme]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" viewBox="0 0 400 {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<rect x="0.5" y="0.5" width="399" height="{height - 1}" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>
<text x="24" y="38" font-family="{FONT}" font-size="15" font-weight="600" fill="{t['title']}">{escape(title)}</text>
<rect x="24" y="48" width="28" height="3" rx="1.5" fill="{t['accent']}"/>
{body}
</svg>
"""


def stats_card(theme, data):
    t = THEMES[theme]
    year = datetime.now(timezone.utc).year
    rows = [
        ("Stars earned", data["stars"]),
        (f"Commits in {year}", data["commits"]),
        ("Pull requests", data["prs"]),
        ("Public repositories", data["repos"]),
    ]
    body = []
    for index, (label, value) in enumerate(rows):
        y = 86 + index * 28
        body.append(
            f'<text x="24" y="{y}" font-family="{FONT}" font-size="13" '
            f'fill="{t["text"]}">{escape(label)}</text>'
            f'<text x="376" y="{y}" text-anchor="end" font-family="{FONT}" '
            f'font-size="13" font-weight="600" fill="{t["title"]}">{value:,}</text>'
        )
    label = ", ".join(f"{name}: {value}" for name, value in rows)
    return card(theme, "GitHub activity", "\n".join(body), 190, label)


def languages_card(theme, data):
    t = THEMES[theme]
    ranked = sorted(data["languages"].items(), key=lambda kv: -kv[1][0])
    top = ranked[:TOP_LANGUAGES]
    total = sum(size for _, (size, _) in top) or 1
    body = ['<clipPath id="bar"><rect x="24" y="68" width="352" height="8" rx="4"/></clipPath>',
            '<g clip-path="url(#bar)">']
    x = 24.0
    for name, (size, color) in top:
        width = 352 * size / total
        body.append(f'<rect x="{x:.2f}" y="68" width="{width:.2f}" height="8" fill="{color}"/>')
        x += width
    body.append("</g>")
    for index, (name, (size, color)) in enumerate(top):
        column, row = index % 2, index // 2
        cx = 24 + column * 180
        cy = 104 + row * 28
        percent = 100 * size / total
        body.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}"/>'
            f'<text x="{cx + 18}" y="{cy}" font-family="{FONT}" font-size="13" '
            f'fill="{t["text"]}">{escape(name)} '
            f'<tspan fill="{t["muted"]}">{percent:.1f}%</tspan></text>'
        )
    label = "Top languages: " + ", ".join(
        f"{name} {100 * size / total:.1f}%" for name, (size, _) in top)
    return card(theme, "Most used languages", "\n".join(body), 190, label)


def main():
    token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("STATS_TOKEN or GITHUB_TOKEN is required")
    data = collect(token)
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"stats-{theme}.svg").write_text(stats_card(theme, data), encoding="utf-8")
        (OUT / f"languages-{theme}.svg").write_text(languages_card(theme, data), encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k != "languages"}))


if __name__ == "__main__":
    main()
