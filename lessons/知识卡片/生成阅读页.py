"""在更新 Markdown 知识卡后运行：python3 生成阅读页.py（需要 pandoc）。"""
import html
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

folder = Path(__file__).resolve().parent
cards = sorted(folder.glob("[0-9][0-9]*-*.md"))
targets = {card.name: card.name.split("-")[0] for card in cards}
examples = sorted(folder.glob("推演-*.md"))
targets.update({p.name: "example-" + p.stem.split("-")[1] for p in examples})
articles = []
for card in cards + examples:
    number = targets[card.name]
    content = subprocess.check_output(
        ["pandoc", "--from=gfm", "--to=html5", "--wrap=none", "--syntax-highlighting=none", str(card)], text=True
    )
    def link_card(match):
        target = targets.get(unquote(html.unescape(match[1])))
        return f'href="#card-{target}"' if target else match[0]
    content = re.sub(r'href="([^"]+)"', link_card, content)
    # Markdown headings in separate cards may have identical slugs.
    content = re.sub(r'(<h[1-6]) id="[^"]+"', r'\1', content)
    articles.append(f'<article id="card-{number}">\n{content}</article>')

page = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bitcoin 课程知识卡</title><style>
:root{color-scheme:dark;font:17px/1.8 system-ui,sans-serif;background:#202328;color:#edf0f5}
body{max-width:52rem;margin:auto;padding:clamp(1rem,4vw,3rem)}
article{display:none;overflow-wrap:anywhere}article:target{display:block}
main:has(article:target) nav{display:none}a{color:#99d9ed;text-underline-offset:3px}
h1,h2,h3{line-height:1.35}h1{font-size:clamp(1.6rem,4vw,2.25rem)}
h2{margin-top:2rem;font-size:1.35rem}p,ul,ol{margin-block:.9rem}
pre,table{background:#30343b}pre{overflow:auto;padding:1rem;border:1px solid #4b515c;border-radius:6px}
code{font: .93em ui-monospace,monospace}table{display:block;overflow:auto;border-collapse:collapse}
th,td{padding:.5em .65em;border:1px solid #4b515c;text-align:left;vertical-align:top}
</style></head><body><main>
"""
index = ''.join(f'<li><a href="#card-{targets[c.name]}">{html.escape(c.stem)}</a></li>' for c in cards)
(folder / "阅读.html").write_text(page + '<nav><h1>Bitcoin 课程知识卡</h1><ul>' + index +
                              '</ul></nav>\n' + '\n'.join(articles) + '</main></body></html>\n')
