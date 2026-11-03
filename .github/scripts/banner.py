"""Render the profile header banner as light and dark SVGs (standard library only)."""

from pathlib import Path

OUT = Path("assets")

THEMES = {
    "light": {
        "bg": "#f6faf8", "border": "#d3e2db", "grid": "#dfeae5", "title": "#13201b",
        "text": "#3d4f48", "muted": "#6b7f77", "accent": "#1f8a66",
        "term": "#ffffff", "term_border": "#d3e2db", "prompt": "#1f8a66", "out": "#3d4f48",
    },
    "dark": {
        "bg": "#0f1714", "border": "#24352e", "grid": "#18241f", "title": "#e7f1ed",
        "text": "#b9cbc3", "muted": "#7f978d", "accent": "#4fc08d",
        "term": "#0a100e", "term_border": "#24352e", "prompt": "#4fc08d", "out": "#b9cbc3",
    },
}

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

TERMINAL = [
    ("$", "whoami"),
    ("", "full-stack developer, France"),
    ("$", "stack --top"),
    ("", "TypeScript · Vue · Symfony · Swift"),
    ("$", "claude \"what are we building today?\""),
]


def banner(theme):
    t = THEMES[theme]
    lines = []
    for index, (prompt, text) in enumerate(TERMINAL):
        y = 124 + index * 30
        color = t["out"] if not prompt else t["title"]
        prefix = f'<tspan fill="{t["prompt"]}">{prompt} </tspan>' if prompt else ""
        lines.append(
            f'<text x="678" y="{y}" font-family="{MONO}" font-size="17" fill="{color}">'
            f'{prefix}{text.replace(chr(34), "&quot;")}</text>'
        )
    cursor_y = 124 + (len(TERMINAL) - 1) * 30 - 15
    last_prompt, last_text = TERMINAL[-1]
    cursor_x = 678 + 0.6 * 17 * (len(last_prompt) + 1 + len(last_text)) + 4
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" role="img" aria-label="Alexis, full-stack developer based in France">
<title>Alexis, full-stack developer based in France</title>
<style>
.cursor {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .cursor {{ animation: none; }} }}
</style>
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.3" fill="{t['grid']}"/>
  </pattern>
</defs>
<rect x="1" y="1" width="1198" height="298" rx="20" fill="{t['bg']}" stroke="{t['border']}" stroke-width="2"/>
<rect x="1" y="1" width="1198" height="298" rx="20" fill="url(#dots)"/>

<text x="64" y="96" font-family="{MONO}" font-size="20" fill="{t['accent']}">@Alexvolkihar</text>
<text x="61" y="160" font-family="{SANS}" font-size="54" font-weight="700" letter-spacing="-1.5" fill="{t['title']}">Hi, I'm Alexis</text>
<text x="64" y="206" font-family="{SANS}" font-size="23" fill="{t['text']}">Full-stack developer in France. Web apps,</text>
<text x="64" y="238" font-family="{SANS}" font-size="23" fill="{t['text']}">dev tools and AI agents with Claude Code.</text>

<rect x="650" y="40" width="510" height="220" rx="14" fill="{t['term']}" stroke="{t['term_border']}" stroke-width="1.5"/>
<circle cx="674" cy="64" r="5.5" fill="#ff5f57"/>
<circle cx="693" cy="64" r="5.5" fill="#febc2e"/>
<circle cx="712" cy="64" r="5.5" fill="#28c840"/>
<text x="1136" y="69" text-anchor="end" font-family="{MONO}" font-size="14" fill="{t['muted']}">~/alexvolkihar</text>
{chr(10).join(lines)}
<rect class="cursor" x="{cursor_x:.0f}" y="{cursor_y}" width="10" height="19" fill="{t['accent']}"/>
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"banner-{theme}.svg").write_text(banner(theme), encoding="utf-8")


if __name__ == "__main__":
    main()
