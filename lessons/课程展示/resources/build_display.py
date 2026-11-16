from pathlib import Path
from html import escape as e
import json,hashlib,argparse
B=Path(__file__).resolve().parent
S=B/'coverage-data.json'
D=json.loads(S.read_text());C=json.loads((B/'展示摘要.json').read_text())
assert [(x['id'],x['title']) for x in C['rows']]==[(x['id'],x['title']) for x in D['lessons']], '展示摘要需随核准课次更新'
def svg(title,desc,body,height):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="{height}" viewBox="0 0 1440 {height}" role="img" aria-labelledby="title desc"><title id="title">{e(title)}</title><desc id="desc">{e(desc)}</desc><style>text{{font-family:"PingFang SC","Microsoft YaHei",sans-serif;fill:#edf0f5}}.small{{font-size:17px;fill:#b2bac6}}.label{{font-size:20px}}.title{{font-size:32px;font-weight:650}}.module{{cursor:pointer}}.module.dim{{opacity:.2}}.module.selected rect{{stroke:#efc478;stroke-width:4}}.module:focus rect{{stroke:#a9ceff;stroke-width:4}}a:focus rect{{stroke:#a9ceff;stroke-width:4}}</style><rect width="1440" height="{height}" fill="#202328"/><text x="40" y="55" class="title">{e(title)}</text><text x="40" y="89" class="small">{e(desc)}</text>{body}</svg>'''
def rect(x,y,w,h,stroke='#4b515c',fill='#30343b'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>'
body=''
for i,s in enumerate(C['stages']):
 x=40+(i%3)*465;y=90+(i//3)*265
 body+=f'<g class="stage" data-stage="{i}" role="button" tabindex="0" aria-label="第{s["start"]}至{s["end"]}讲 {s["name"]}">{rect(x,y,430,220)}<text x="{x+22}" y="{y+36}" class="small">第 {s["start"]}—{s["end"]} 讲</text><text x="{x+22}" y="{y+78}" font-size="27">{s["name"]}</text><text x="{x+22}" y="{y+117}" class="small">{s["path"]}</text><path d="M{x+22} {y+145}H{x+408}" stroke="#4b515c"/><text x="{x+22}" y="{y+184}" font-size="23" style="fill:#88d5bc">{s["result"]}</text></g>'
 body+=f'<text x="{x+388}" y="{y+38}" class="small">{i+1:02}</text>'
body+='<text x="40" y="680" class="label">运行 3 个节点、2 个钱包，完成付款、分叉、重组与恢复。</text>'
progress=svg('知识覆盖图 1 · 从一笔付款到一个系统','',body,730)
body=''
groups=[('钱包 · 10 个模块',[m for m in D['modules'] if m['id'].startswith('W')]),('全节点 · 10 个独立模块',[m for m in D['modules'] if m['id'].startswith('N') and m['id']!='N11']),('挖矿 · 3 项职责',[m for m in D['modules'] if m['id'].startswith('D')])]
for col,(title,mods) in enumerate(groups):
 x=40+col*465;body+=f'<text x="{x}" y="138" font-size="24">{title}</text>'
 for row,m in enumerate(mods):
  y=160+row*79;nums=' / '.join(m['primary']);opts=' · '+','.join(m['electives']) if m['electives'] else ''
  body+=f'<g class="module" data-module="{m["id"]}" role="button" tabindex="0" aria-label="{e(m["name"])}">{rect(x,y,430,67)}<text x="{x+15}" y="{y+27}" class="label">{e(m["id"]+" "+m["name"])}</text><text x="{x+15}" y="{y+52}" font-size="15" fill="#b2bac6">必修 {nums}{opts}</text></g>'
 if col==2:
  lines=['接口闭环','15 讲：节点发布有序事件','16 讲：钱包提交、查询与订阅','19 讲：崩溃后重扫或重放恢复','','部署边界','钱包负责授权与归属跟踪','全节点独立验证交易与历史','矿池协调作业，矿机搜索PoW','','N11是钱包在节点中的部署实例，','不重复计入20个独立模块。']
  for i,t in enumerate(lines):body+=f'<text x="{x+15}" y="{445+i*34}" class="{ "label" if i in [0,5] else "small"}">{e(t)}</text>'
body+='<text x="40" y="1005" class="small">图中课次为教学安排；第22讲统一集成验收。交叉复用与逐项深度可在HTML中点击查看。</text>'
modules=svg('知识覆盖图 2 · 课程落在系统的什么位置','20个独立钱包／节点模块均有必修安排；矿池与虚拟矿机机制在第21讲对照。',body,1040)
body='';tiers=[('必讲','#9fc9ed'),('必做','#88d5bc'),('选修','#b8a4df')];tier_names={'必讲':'基础概念','必做':'基础实践','选修':'专题扩展'}
for i,(label,color) in enumerate(tiers):
 x=40+i*465;body+=rect(x,125,430,124,color)+f'<text x="{x+20}" y="165" font-size="25" style="fill:{color}">{tier_names[label]}</text>'
 lines={'必做':['构建钱包、账本与节点','实现正常流程和失败用例'],'必讲':['核心概念、算法与数据结构','标准机制与协议原理'],'选修':['协议兼容与性能优化','存储、网络与矿机工程']}[label]
 for j,t in enumerate(lines):body+=f'<text x="{x+20}" y="{198+j*27}" class="small">{t}</text>'
for i,(prefix,label) in enumerate([('W','钱包'),('N','全节点（含钱包实例）'),('D','挖矿职责')]):
 topics=[t for m in D['modules'] if m['id'].startswith(prefix) for t in m['topics']];y=300+i*85;body+=f'<text x="40" y="{y+28}" class="label">{label}</text>';x=340
 for tier,color in tiers:
  count=sum(t['tier']==tier for t in topics);w=count*20
  if w:body+=rect(x,y,w,42,color,color)+f'<text x="{x+w/2}" y="{y+28}" font-size="19" text-anchor="middle" style="fill:#202328">{count}</text>'
  x+=w
body+='<text x="40" y="590" font-size="26">6 个扩展专题</text>'
for i,c in enumerate(D['electives']):
 x=40+(i%3)*465;y=625+(i//3)*105;body+=rect(x,y,430,88,'#76658e')+f'<text x="{x+15}" y="{y+31}" font-size="18">{e(c["id"]+" · "+c["title"])}</text><text x="{x+15}" y="{y+62}" class="small">先修：第 {" / ".join(c["prerequisites"])} 讲</text>'
depth=svg('知识覆盖图 3 · 基础概念、基础实践与专题扩展','',body,860)
svgs=[progress,modules,depth];names=['01-课程能力进阶.svg','02-系统模块覆盖.svg','03-知识深度分层.svg']
payload=dict(**C,modules=D['modules'],electives=D['electives'],sourceSha256=hashlib.sha256(S.read_bytes()).hexdigest())
html=(B/'展示模板.html').read_text().replace('{{DATA}}',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
for i,s in enumerate(svgs):html=html.replace('{{SVG'+str(i+1)+'}}',s.replace('id="title"',f'id="figure-{i+1}-title"').replace('id="desc"',f'id="figure-{i+1}-desc"').replace('aria-labelledby="title desc"',f'aria-labelledby="figure-{i+1}-title figure-{i+1}-desc"'))
outputs={B.parent/'课程展示.html':html,**{B/n:s for n,s in zip(names,svgs)}}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
 if a.check:
  assert all(f.exists() and f.read_text()==s for f,s in outputs.items()),'展示输出与源数据不同步'
  print('PASS: 22 approved lessons and all 5 presentation artifacts match source.')
 else:
  for f,s in outputs.items():f.write_text(s)
  print('Generated Markdown, standalone HTML and 3 standalone SVG figures.')
