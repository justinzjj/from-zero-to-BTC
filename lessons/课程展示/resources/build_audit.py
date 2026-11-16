"""Render the syllabus and offline coverage page from one reviewed mapping."""
import argparse, hashlib, json, re
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
DATA = BASE / 'coverage-data.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def make():
    d = json.loads(DATA.read_text())
    courses = d['lessons'] + d['electives']; ids = {c['id'] for c in courses}
    assert len(ids) == len(courses), 'duplicate lesson ID'
    assert d['integrationLesson'] in ids
    assert len({m['id'] for m in d['modules']}) == len(d['modules'])
    visited = set()
    for c in courses:
        assert set(c['prerequisites']) <= visited, ('out-of-order dependency', c['id'])
        visited.add(c['id'])
    topics = [t for m in d['modules'] for t in m['topics']]
    assert len({t['id'] for t in topics}) == len(topics)
    for m in d['modules']:
        for t in m['topics']:
            assert t['tier'] in ['必做','必讲','选修']
            assert set(t['lessons'] + t['electives']) <= ids
            assert t['outcome'] and (t['lessons'] if t['tier'] != '选修' else t['electives']), t['id']
        assert set(m['primary']) == {n for t in m['topics'] for n in t['lessons']}
    # Recompute elective links and depth classification so the view cannot drift.
    for m in d['modules']:
        m['electives'] = sorted({e for t in m['topics'] for e in t['electives']})
        m['depth'] = 'mixed' if m['electives'] else 'theory' if any(t['tier']=='必讲' for t in m['topics']) else 'practice'
    table = '\n'.join(f"| {c['id']} | {c['title']} | {', '.join(c['prerequisites']) or '第0讲'} | {c['practice']} |" for c in d['lessons'])
    table = '| 课次 | 主题 | 先修 | 累积实践 / 对照实验 |\n|---|---|---|---|\n' + table
    sections = []
    for c in d['lessons']:
        sections.append(f"<a id=\"lesson-{c['id']}\"></a>\n\n### 第{c['id']}讲 · {c['title']}\n\n- **先修与模块：** {', '.join(c['prerequisites']) or '第0讲'}；{'、'.join(c['modules'])}。\n- **基本概念与技术细节：** {c['concept']}。\n- **算法原理：** {c['algorithm']}。\n- **简单实践：** {c['practice']}。\n- **验收与失败例：** {c['accept']}。")
    elective = '| 编号与专题 | 先修 | 选修内容 | 实践与验收 |\n|---|---|---|---|\n' + '\n'.join(f"| {c['id']} · {c['title']} | {', '.join(c['prerequisites'])} | {c['concept']} | {c['practice']}；{c['accept']} |" for c in d['electives'])
    topic_table = '| 模块 | 技术点 | 必修深度 / 课次 | 选修深化 | 可观察结果 |\n|---|---|---|---|---|\n'
    topic_table += '\n'.join(f"| {m['id']} {m['name']} | {t['name']} | {t['tier']} {' / '.join(t['lessons'])} | {' / '.join(t['electives']) or '—'} | {t['outcome']} |" for m in d['modules'] for t in m['topics'])
    md = (BASE/'课程大纲模板.txt').read_text()
    for key,value in {'LESSONS_TABLE':table,'LESSONS':'\n\n'.join(sections),'ELECTIVES':elective,'TOPIC_TABLE':topic_table,'MIGRATION':'\n'.join(f'| {a} | {b} |' for a,b in d['oldToNew'])}.items():
        md = md.replace('{{'+key+'}}',value)
    summary=json.loads((BASE/'展示摘要.json').read_text())
    assert [(c['id'],c['title']) for c in summary['rows']]==[(c['id'],c['title']) for c in d['lessons']]
    overview='| 课程 | 基本概念／算法与数据结构 | 对应代码实践 | 学到什么／积累什么能力 |\n|---|---|---|---|\n'
    overview+='\n'.join(f"| {c['id']}. {c['title']} | {c['concept']} | {c['practice']} | {c['ability']} |" for c in summary['rows'])
    ext='| 专题 | 基本概念／算法与数据结构 | 对应代码实践 |\n|---|---|---|\n'+'\n'.join(f"| {c['id']}. {c['title']} | {c['concept']} | {c['practice']} |" for c in d['electives'])
    md=md.replace('{{OVERVIEW}}',overview).replace('{{EXT_OVERVIEW}}',ext)
    for a,b in [('必做','基础实践'),('必讲','基础概念'),('选修','专题扩展')]: md=md.replace(a,b)
    source_dir = ROOT/'from-zero-to-BTC/lessons/00-overview'
    d['sources']=[dict(file=p.name,path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [source_dir/'btc-deployment.html',source_dir/'btc-wallet.html',source_dir/'btc-full-node.html']]
    d['sources'].append(dict(file='课程大纲.md',path=str((BASE.parent/'课程大纲.md').relative_to(ROOT)),sha256=hashlib.sha256(md.encode()).hexdigest()))
    html=(BASE/'coverage.template.html').read_text().replace('{{DATA}}',json.dumps(d,ensure_ascii=False).replace('</','<\\/'))
    return {DATA:json.dumps(d,ensure_ascii=False,indent=2)+'\n',BASE.parent/'课程大纲.md':md,BASE.parent/'课程覆盖审计.html':html}

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    outputs=make()
    if args.check:
        stale=[str(p) for p,s in outputs.items() if not p.exists() or p.read_text()!=s]
        if stale: raise SystemExit('Stale generated files:\n'+'\n'.join(stale))
        print('PASS: lesson dependencies, topic assignments, source hashes and all 4 generated files match.')
    else:
        for p,s in outputs.items():p.write_text(s)
        print('Rendered syllabus, portable syllabus, mapping and offline HTML.')
