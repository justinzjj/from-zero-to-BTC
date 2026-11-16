"""Build both offline HTML pages and the single syllabus from shared resources."""
from pathlib import Path
import argparse,runpy,re
from urllib.parse import unquote,urlsplit
B=Path(__file__).resolve().parent
R=B/'resources'

def build(check=False):
    audit=runpy.run_path(str(R/'build_audit.py'))['make']()
    if check:
        assert all(p.exists() and p.read_text()==s for p,s in audit.items()), 'Audit/data/syllabus outputs are stale'
    else:
        for p,s in audit.items():p.write_text(s)
    display=runpy.run_path(str(R/'build_display.py'))['outputs']
    if check:
        assert all(p.exists() and p.read_text()==s for p,s in display.items()), 'Display/SVG outputs are stale'
    else:
        for p,s in display.items():p.write_text(s)
    assert {p.name for p in B.rglob('*.md')}=={'课程大纲.md','知识点梳理.md'}, 'Keep the unified syllabus and knowledge checklist'
    for p in [B/'课程展示.html',B/'课程覆盖审计.html',B/'课程大纲.md']:
        content=p.read_text()
        links=re.findall(r'href="([^"]+)"',content) if p.suffix=='.html' else re.findall(r'\]\(([^)]+)\)',content)
        for link in links:
            if '${' in link or '{{' in link:continue
            u=urlsplit(link)
            if u.scheme or u.netloc or not u.path:continue
            assert (p.parent/unquote(u.path)).exists(), f'Broken link: {p.name}: {link}'
    print('PASS: shared course data, both HTML pages, unified syllabus, SVGs and local links verified.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    build(parser.parse_args().check)
