"""Bring elitze-site/index.html to clean HTML: escape bare '&', add thead/tbody,
replace inline styles with classes so html-validate passes with zero errors."""
from __future__ import annotations

import re
from pathlib import Path

P = Path(__file__).resolve().parent / "index.html"

CSS_ADDITIONS = """
  .brand-sub{font-weight:500;font-size:12.5px;letter-spacing:.10em;text-transform:uppercase;color:#a79fc4;margin-left:8px}
  .card.featured{border-color:#4c2f8a}
  .tag.small{font-size:11px}
  .lead.lede-sm{font-size:16px}
"""


def main() -> int:
    html = P.read_text(encoding="utf-8")

    # 1. escape bare ampersands (keep existing entities intact)
    html = re.sub(r"&(?!(?:[a-zA-Z][a-zA-Z0-9]{1,10}|#\d{1,6}|#x[0-9a-fA-F]{1,6});)", "&amp;", html)

    # 2. inline styles -> classes
    html = html.replace(
        '<span style="font-weight:500;font-size:12.5px;letter-spacing:.10em;text-transform:uppercase;color:#a79fc4;margin-left:8px">',
        '<span class="brand-sub">',
    )
    html = html.replace('<div class="card" style="border-color:#4c2f8a">', '<div class="card featured">')
    html = html.replace('<span class="tag" style="font-size:11px">', '<span class="tag small">')
    html = html.replace('<p class="lead" style="font-size:16px">', '<p class="lead lede-sm">')

    # 3. thead/tbody
    def wrap(match: re.Match) -> str:
        rows = re.findall(r"<tr>.*?</tr>", match.group(1), flags=re.S)
        if len(rows) < 2:
            return match.group(0)
        body = "\n      ".join(rows[1:])
        return ("<table>\n    <thead>\n      " + rows[0] +
                "\n    </thead>\n    <tbody>\n      " + body + "\n    </tbody>\n  </table>")

    html = re.sub(r"<table>(.*?)</table>", wrap, html, flags=re.S)

    # 4. inject the new classes once, before the closing </style>
    if ".brand-sub{" not in html:
        html = html.replace("</style>", CSS_ADDITIONS + "</style>", 1)

    P.write_text(html, encoding="utf-8")
    print("inline styles left:", html.count("style=\""))
    print("thead:", "<thead>" in html, "| tbody:", "<tbody>" in html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
