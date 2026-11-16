from pathlib import Path
import json,io,re
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table,TableStyle,Paragraph
from reportlab.lib.styles import ParagraphStyle
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from html import escape
B=Path(__file__).resolve().parent; ROOT=B.parents[3]
D=json.loads((B/'展示摘要.json').read_text()); E=json.loads((B/'coverage-data.json').read_text())['electives']
pdfmetrics.registerFont(TTFont('CJK','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
pdfmetrics.registerFontFamily('CJK',normal='CJK',bold='CJK',italic='CJK',boldItalic='CJK')
W,H=landscape(A3); out=B/'从零构建区块链-课程大纲与知识覆盖图.pdf';c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('从零构建区块链 · 课程大纲与知识覆盖图');c.setAuthor('')
bg=colors.HexColor('#202328');text=colors.HexColor('#edf0f5');line=colors.HexColor('#4b515c')
style=ParagraphStyle('cell',fontName='CJK',fontSize=14,leading=22,textColor=text,wordWrap='CJK')
head=ParagraphStyle('head',parent=style,fontSize=13,leading=20)
def page(title,sub=''):
 c.setFillColor(bg);c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(text);c.setFont('CJK',25);c.drawString(36,H-55,title)
 if sub:c.setFillColor(colors.HexColor('#b2bac6'));c.setFont('CJK',12);c.drawString(36,H-80,sub)
def finish():
 c.setFont('CJK',10);c.setFillColor(colors.HexColor('#b2bac6'));c.drawRightString(W-36,20,str(c.getPageNumber()));c.showPage()
def table(rows):
 headers=['课程','基本概念／算法与数据结构','对应代码实践','学到什么／积累什么能力']
 data=[[Paragraph(h,head) for h in headers]]+[[Paragraph(escape(str(x)),style) for x in row] for row in rows]
 t=Table(data,colWidths=[(W-72)*x for x in [.22,.25,.28,.25]])
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#3a4049')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#30343b'),colors.HexColor('#292d34')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15),('LINEBELOW',(0,0),(-1,-1),.5,line)]))
 tw,th=t.wrap(W-72,H-140);assert th<H-140,(th,H);t.drawOn(c,36,H-110-th)
for a,z in [(0,8),(8,16),(16,22)]:
 page('从零构建区块链 · 课程大纲',f'第 {a+1}–{z} 讲')
 table([[r['id']+'. '+r['title'],r['concept'],r['practice'],r['ability']] for r in D['rows'][a:z]]);finish()
page('从零构建区块链 · 专题扩展','6 个扩展专题')
abilities=['扩展标准钱包与密钥恢复能力','增加可验证的交易与脚本类型','在不改变共识的前提下优化交易选择','提高传播、同步与资源控制能力','在保持正确性的前提下提升状态恢复性能','理解矿池协议到矿机执行的工程边界']
table([[r['id']+'. '+r['title'],r['concept'],r['practice'],a] for r,a in zip(E,abilities)]);finish()
for name in ['01-课程能力进阶.svg','02-系统模块覆盖.svg','03-知识深度分层.svg']:
 page('')
 s=(B/name).read_text().replace('font-weight:650','font-weight:normal');s=re.sub(r'font-family:[^;}]+','font-family:CJK',s)
 drawing=svg2rlg(io.BytesIO(s.encode()));scale=min((W-40)/drawing.width,(H-50)/drawing.height);drawing.scale(scale,scale)
 renderPDF.draw(drawing,c,(W-drawing.width*scale)/2,(H-drawing.height*scale)/2+8);finish()
c.save();print(out)
