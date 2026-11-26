"""Build the first two lecture decks; standalone HTML, no CDN or runtime dependencies."""
from pathlib import Path
from html import escape as e
import re
ROOT = Path(__file__).resolve().parents[3]
LESSONS = ROOT/'lessons'
CORE='https://github.com/bitcoin/bitcoin/blob/v29.0/src/'
def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def ul(*items): return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def code(s): return '<pre><code>'+e(s.strip())+'</code></pre>'
def formula(s): return '<div class="formula">'+s+'</div>'
def note(s): return '<p class="takeaway">'+s+'</p>'
def cols(a,b):return '<div class="columns"><div>'+a+'</div><div>'+b+'</div></div>'
def ref(path,label=None):return f'<a href="{CORE+path}" target="_blank" rel="noopener">{label or path} ↗</a>'
def local(n,name): return f'<a href="../../code/lesson-{n:02}/{name}">{name}</a>'
def snippet(n,file,start,end):
    text=(ROOT/f'code/lesson-{n:02}'/file).read_text(); a=text.index(start); b=text.index(end,a) if end else len(text)
    return code(re.sub(r'/\* 数学原理：.*?\*/\s*', '', text[a:b], flags=re.S).strip() + ('\n}' if end == '\n}\n}' else ''))
def flow(items):return '<div class="flow">'+''.join('<span>'+x+'</span>' for x in items)+'</div>'
def slide(title,q,body,source='',part='基础知识'):
    return dict(title=title,q=q,body=body,source=source,part=part)
def arch(n):
    names=['W1 用户接口','W2 密钥与脚本管理','W5 交易构造','W6 签名与见证装配','W7 节点接口','N5 共用交易与脚本检查']
    active=[0,2] if n==1 else [1,3,5]
    links=['btc-wallet.html']*5+['btc-full-node.html']
    out='<svg viewBox="0 0 1040 180" role="img" aria-label="本课在钱包和全节点中的模块位置；金色标出本课对应模块">'
    out+='<text x="18" y="26" class="svg-label">钱包</text><text x="868" y="26" class="svg-label">全节点</text>'
    for i,(name,link) in enumerate(zip(names,links)):
        x=18+i*170
        if i<5:out+=f'<path d="M{x+150} 85h20" class="edge"/>'
        out+=f'<a href="../00-overview/{link}"><rect x="{x}" y="48" width="150" height="74" rx="6" class="{"hot" if i in active else "module"}"/><text x="{x+75}" y="79" text-anchor="middle" class="svg-text">{name.split(" ")[0]}</text><text x="{x+75}" y="103" text-anchor="middle" class="svg-small">{name.split(" ")[1]}</text></a>'
    out+='<text x="18" y="159" class="svg-small">'+('本课：金额与草稿编码；共用序列化、哈希原语由后续节点模块复用。' if n==1 else '本课：密钥生成、签名与公开验签；N5 的完整交易检查在第4讲接入。')+'</text></svg>'
    return '<div class="architecture">'+out+'</div><p class="source">沿用 overview 模块名称；此处是本课学习路径。 <a href="../00-overview/btc-wallet.html">钱包完整架构</a> · <a href="../00-overview/btc-full-node.html">全节点完整架构</a></p>'

one=[]
def a(t,q,b,s='',p='基础知识'):one.append(slide(t,q,b,s,p))
a('让所有节点读懂同一笔付款','第01讲 · 字节、金额与确定性编码',cols('<h2>学习重点</h2>'+ul('<b>概念：</b>整数聪、字节序、确定性编码、哈希边界。','<b>算法：</b>十进制精确解析、小端编解码、有界读取、SHA-256。','<b>结构：</b>Amount、PaymentDraft、Bytes、Hash256、Reader。'),'<h2>本课要解决的问题</h2><p>Alice 输入 <code>0.00060000 BTC</code>，不同机器怎样得到相同金额、相同字节、相同摘要？</p>'+flow(['60000 聪','13 字节草稿','32 字节摘要']))+arch(1),p='本课总览')
a('整数金额 Amount','如何避免小数舍入进入付款计算？',formula('1 BTC = 100,000,000 聪')+cols(ul('金额存为 <code>int64_t</code>，小数只出现在输入和展示层。','整数适合比较、求和、费用与找零；仍然需要溢出保护。','<code>MAX_MONEY = 21,000,000 × COIN</code>，是范围上限，不是本课实现的发行规则。'),table(['表达','含义'],[['0.00060000 BTC','60000 聪'],['Amount','8 字节有符号整数'],['CAmount / MoneyRange','Bitcoin 类型 / 范围判定']]))+note('Bitcoin 交易保存整数金额；文本输入格式不是链上共识规则。'),ref('consensus/amount.h'))
a('十进制金额解析算法','怎样从文本精确得到整数聪？',formula('A = w × 10⁸ + f × 10<sup>8−d</sup>')+flow(['扫描字符','整数逐位累加','小数最多8位','补零到8位','检查金额范围'])+ul('w 为整数部分，f 为小数数字整数，d 为小数位数。','执行 <code>w = 10w + digit</code> 前，检查 <code>w ≤ (limit − digit) / 10</code>。','只接受数字和一个小数点；拒绝符号、空白、科学计数法、9位小数。')+note('O(L) 时间、O(1) 辅助空间；教学输入上限32字符。Core ParseMoney 会 TrimString，并返回 optional；教学接口失败抛异常。'),ref('util/moneystr.cpp','ParseMoney / FormatMoney'))
a('PaymentDraft、Bytes 与 Hash256','语义对象与传输字节为什么要分开？',code('using Amount = std::int64_t;\nusing Bytes = std::vector<unsigned char>;\nusing Hash256 = std::array<unsigned char, 32>;\nstruct PaymentDraft {\n    std::uint32_t recipient;\n    Amount amount;\n};')+table(['对象','存储与操作'],[['PaymentDraft','字段共12字节；本机 sizeof 为16，包含ABI填充'],['Bytes','连续动态数组；追加摊还 O(1)，扩容 O(n)'],['Hash256','32字节内联数组；类型固定长度']])+note('recipient 是教学占位标识，不是 Bitcoin 地址。不能把结构体内存直接当网络格式。'))
a('Bitcoin 交易数据结构','真实交易比付款草稿多了哪些信息？',table(['Bitcoin Core 类型','字段 / 职责','草稿当前缺少什么'],[['COutPoint','交易标识＋输出序号','旧输出引用'],['CTxIn','prevout、scriptSig、nSequence、scriptWitness','输入与授权材料'],['CTxOut','nValue、scriptPubKey','真实收款条件是脚本'],['CMutableTransaction','version、vin、vout、nLockTime','完整可修改交易'],['CTransaction','交易字段与缓存标识','交易生命周期与缓存']])+note('真实交易含动态数组和脚本：sizeof、总内存占用、网络字节长度是三个不同的量。uint256 是不透明哈希载荷；教学 Hash256 尚未区分 Txid / Wtxid。'),ref('primitives/transaction.h')+' · '+ref('uint256.h'))
a('小端整数编码','同一个整数怎样得到相同字节？',formula('bᵢ = (v ≫ 8i) &amp; 255　　v = Σ bᵢ · 2<sup>8i</sup>')+cols(code('60000 = 0xEA60\n\n小端：60 ea 00 00 00 00 00 00\n大端：00 00 00 00 00 00 ea 60'),ul('1字节 = 8位 = 2个十六进制字符。','编码和解码使用无符号移位。','解码先放入 uint64_t，检查范围后转换 Amount。'))+note('字节序由协议规定，不能依赖当前机器的内存顺序。'),ref('serialize.h','ser_writedata32/64、ser_readdata32/64'))
a('确定性序列化：13字节草稿','哪些规则共同保证编码没有歧义？',table(['偏移','字段','长度','示例'],[['0','version','1字节','01'],['1–4','recipient','4字节小端','02 00 00 00'],['5–12','amount','8字节小端','60 ea 00 00 00 00 00 00']])+code('01 | 02 00 00 00 | 60 ea 00 00 00 00 00 00')+ul('固定字段顺序、宽度、版本、字节序和有效范围。','合法规范输入满足 encode(decode(bytes)) == bytes。','JSON需要额外规范化；无边界字符串拼接可能产生歧义。')+note('教学 version 为1字节；Bitcoin 交易 version 为4字节，且有输入、输出、锁定时间及可选见证。'))
a('CompactSize 与交易序列化','Bitcoin 如何编码输入数量、脚本长度等变长信息？',table(['数值 x','CompactSize 编码','总长度'],[['0 ≤ x < 253','x','1字节'],['253 ≤ x ≤ 65535','fd + uint16 小端','3字节'],['65536 ≤ x ≤ 2³²−1','fe + uint32 小端','5字节'],['更大的 uint64','ff + uint64 小端','9字节']])+flow(['version','输入列表','输出列表','nLockTime'])+note('252 → fc；253 → fd fd 00。CompactSize 不等于 Core VARINT。见证交易按规则插入 marker/flag 和见证；本课13字节格式不兼容 Bitcoin。'),ref('serialize.h')+' · '+ref('primitives/transaction.h','SerializeTransaction'))
a('Reader 与有界反序列化','怎样拒绝截断、额外字节和越界金额？',flow(['总长 = 13','version = 1','读取 recipient','读取 amount','金额范围检查'])+cols(ul('<code>Reader = 字节引用 + pos</code>，保持 0 ≤ pos ≤ size。','先检查剩余长度，再读取并推进游标。','时间 O(n)，固定字段的只读解析辅助空间 O(1)。'),ul('Core SpanReader 用剩余 span 表示读取状态。','ReadCompactSize 拒绝非最短表示，例如用 fd 01 00 表示1。','Core 流可连续读取对象；是否禁止尾随数据由调用层决定。'))+note('解析成功只说明格式合规，不说明有钱、已授权、未双花。教学只接受版本1，不代表 Bitcoin 只能接受版本1。'),ref('streams.h','SpanReader')+' · '+ref('serialize.h','ReadCompactSize'))
a('SHA-256：分块、填充与压缩','固定长度摘要如何从消息字节产生？',flow(['追加1位与零填充','附加64位原始位长度','512位分块','64轮压缩','输出256位'])+ul('每块64字节；形成16个32位大端字，再扩展为64个字。','8个32位工作寄存器逐轮混合，结束后累加进状态。','SHA内部大端读字，与草稿字段的小端序属于不同层次。')+formula('块数 = ⌈(n + 9) / 64⌉')+note('O(n) 时间、流式常量工作空间。13字节草稿需要1块；双SHA-256的第二次32字节输入再需要1块。'),'<a href="https://csrc.nist.gov/pubs/fips/180-4/upd1/final">FIPS 180-4</a> · '+ref('crypto/sha256.h'))
a('SHA-256：消息扩展与一轮计算','一位输入变化怎样进入后续状态？',formula('Wₜ = σ₁(Wₜ₋₂) + Wₜ₋₇ + σ₀(Wₜ₋₁₅) + Wₜ₋₁₆<br>T₁ = h + Σ₁(e) + Ch(e,f,g) + Kₜ + Wₜ<br>T₂ = Σ₀(a) + Maj(a,b,c)')+table(['函数','位运算'],[['Ch / Maj','(x∧y)⊕(¬x∧z) / (x∧y)⊕(x∧z)⊕(y∧z)'],['Σ₀ / Σ₁','右旋 2、13、22 / 6、11、25 后异或'],['σ₀ / σ₁','右旋7、18与右移3 / 右旋17、19与右移10 后异或']])+note('所有加法模 2³²；每轮 a=T₁+T₂、e=d+T₁，其余寄存器顺移。理解流程并调用成熟库，不要求手写64轮。'))
a('Bitcoin 的哈希组合与输入边界','同样叫“哈希”，实际调用有什么不同？',table(['用途','算法与输入'],[['txid','不含见证的交易序列化 → 双SHA-256'],['wtxid','含见证的交易序列化 → 双SHA-256；无见证时等于txid'],['区块头 / PoW','80字节区块头 → 双SHA-256'],['HASH160','RIPEMD160(SHA256(data))'],['带标签哈希','SHA256(SHA256(tag) ∥ SHA256(tag) ∥ message)']])+note('教学 EVP_Digest 对应基础哈希；Core 用 CSHA256 / CHash256 等封装。草稿摘要不是 txid；Core 常见 uint256 十六进制显示顺序与本课原始字节 hex 不同。'),ref('hash.h')+' · '+ref('primitives/transaction.cpp'))
a('哈希摘要的保证边界','攻击者修改金额后，为什么仍能得到合法摘要？',cols(ul('<b>保证：</b>相同输入得到相同输出；依赖抗碰撞、抗原像性质。','<b>不保证：</b>没有碰撞、付款者身份、消息保密。','双哈希输出仍为32字节，安全强度不简单翻倍。'),code('原草稿 → SHA256 → 摘要 A\n改金额 → SHA256 → 摘要 B\n\n攻击者也能计算 B。'))+note('13字节草稿的摘要反而更长。摘要的价值是固定长度与索引，不是每次都压缩。'))
a('实验：输入金额，观察线格式','改变一个输入，检查整数与字节的对应。','<form id="amount-form"><label for="amount">金额 / BTC</label><input id="amount" value="0.00060000" inputmode="decimal"><label for="recipient">收款标识 / uint32</label><input id="recipient" value="2" inputmode="numeric"><button>计算编码</button></form><pre id="amount-output" aria-live="polite"></pre>'+note('试验：0.0006 与 0.00060000；60000聪与60001聪；9位小数；超过2100万BTC。此处演示编码，实际C++实验还验证哈希。'),p='实验尝试')
a('实验环境与代码入口','先确定输入、输出和文件职责。',code('bash ../../code/lesson-01/run.sh')+table(['文件','职责'],[[local(1,'foundations.hpp'),'金额、类型、编码、读取与哈希'],[local(1,'lab01.cpp'),'固定向量、失败输入、往返断言'],[local(1,'run.sh'),'C++17 编译与运行']])+ul('在本讲目录运行；依赖 pkg-config 与 OpenSSL 3开发文件。','输出进入 code/build/lesson-01；所有实现集中在 code/。','先独立实现或逐函数解释，再运行验证。'),p='实验尝试')
a('代码：金额解析与溢出检查','为什么必须先检查，再执行乘10？',snippet(1,'foundations.hpp','inline Amount parse_amount','inline void put_le')+note('关注三处约束：整数上界、小数8位、合并后的 MAX_MONEY。失败不返回“近似金额”。'),local(1,'foundations.hpp'),p='实验尝试')
a('代码：草稿编码与解码','怎样把类型契约变成可执行检查？',snippet(1,'foundations.hpp','inline Bytes encode','inline Bytes digest')+note('reserve(13) 控制扩容；读取金额先用无符号类型；通过范围检查才转 Amount。'),local(1,'foundations.hpp'),p='实验尝试')
a('代码：小端读写与哈希接口','哪些原语会被后续模块直接复用？',cols(snippet(1,'foundations.hpp','inline void put_le','// An intent'),snippet(1,'foundations.hpp','inline Hash256 sha256','template<class T>'))+note('put_le / Reader::le 固定宽度；sha256 / double_sha256 显式区分组合。不能把第2讲 message 接口误当 digest 接口。'),local(1,'foundations.hpp'),p='实验尝试')
a('验证：固定结果与失败场景','怎样判断是实现正确，而不只是程序成功运行？',code('amount_sat=60000\nwire_bytes=13\nwire_hex=010200000060ea000000000000\nsha256=54c84baf5560274cd84dcea2ba3d90eb9db9195f84961656adbe12affcdb2a7d\ndouble_sha256=cabe344ece1c989c86725f3799eebbd11746f15a7b6ea59ac5968df1fa98c873')+table(['输入 / 操作','预期'],[['1聪、21000000 BTC','接受；上界外1聪拒绝'],['负号、科学计数法、空串、9位小数','拒绝，不舍入'],['截断、加尾字节、改版本、金额全ff','拒绝'],['SHA256("abc") / 编解码往返','匹配标准向量 / 恢复原对象']]),local(1,'lab01.cpp'),p='实验尝试')
a('接入系统：表示层已经就绪','哪些成果保留，哪些结构后续演进？',table(['成果','后续调用','演进'],[['Amount / parse_amount','第3讲金额守恒、第8讲付款界面','增加安全求和'],['Bytes / Hash256 / 整数读写','交易、区块、网络、存储','为各消息定义布局'],['PaymentDraft','第2讲授权实验','第3/4讲建立UTXO交易'],['哈希接口','签名、标识、索引','固定各自输入和组合']])+ul('练习：实现 format_amount 往返；新增v2字段；测不同长度SHA吞吐量。','验收：画出13字节布局，说明草稿摘要为何不是txid，说明解析成功为何不等于交易有效。')+note('下一讲：攻击者也能重算哈希，如何证明这些字节经过 Alice 授权？'),p='实验尝试')

two=[]
def a(t,q,b,s='',p='基础知识'):two.append(slide(t,q,b,s,p))
a('证明这笔付款经过了谁的授权','第02讲 · 密钥、哈希与数字签名',cols('<h2>学习重点</h2>'+ul('<b>概念：</b>公私钥、数字签名、公开验签与授权边界。','<b>算法：</b>调用secp256k1上的ECDSA，完成消息签名与验签。','<b>结构：</b>Key / Context、消息字节、压缩公钥与DER签名。'),'<h2>本课要解决的问题</h2><p>任何人都能改草稿并重算哈希，怎样产生只有 Alice 能生成、其他人能公开核验的授权证据？</p>'+flow(['13字节草稿','私钥签名','公钥验签']))+arch(2),p='本课总览')
a('数字签名与公钥认证','谁能生成证据，谁能验证证据？',table(['机制','验证者需要什么','限制'],[['公开哈希','消息与算法','任何人都能重算'],['共享密码 / HMAC','同一秘密','持有验证秘密的人也能伪造'],['数字签名','公开密钥','私钥生成，公钥验证']])+note('签名不加密，也不证明余额、未双花或确认。公钥必须绑定应有的花费条件；不能信任提交者任意附带的公钥。'))
a('secp256k1、ECDSA 与 Schnorr','Bitcoin 到底使用哪条曲线、哪种算法？',table(['层次','Bitcoin 的实际选择','教学实现'],[['曲线','secp256k1：y²=x³+7 mod p','真实实验同样选 secp256k1'],['公钥生成','Q=dG，椭圆曲线标量乘法','小曲线用二进制倍加推演'],['传统 / SegWit v0','ECDSA','OpenSSL EVP ECDSA'],['Taproot','BIP340 Schnorr','本讲认识，E2扩展'],['库','libsecp256k1','OpenSSL 3']])+note('曲线是参数集合，标量乘法是底层运算，ECDSA / Schnorr 是签名算法；这三个层次不能混称。'),'<a href="https://bips.dev/340/">BIP340</a> · <a href="https://bips.dev/341/">BIP341</a>')
a('有限域与扩展欧几里得算法','模运算里的除法如何定义？',formula('a · a⁻¹ ≡ 1 (mod p)<br>ax + py = gcd(a,p) = 1')+ul('加、减、乘都取模；除以a改为乘a的逆元。','辗转相除递推余数，同时递推系数；gcd不变，线性组合关系不变。','只有 gcd(a,p)=1 才有逆元；不能求0的逆。')+code('例：3 × 13 = 39 ≡ 1 (mod 19)\n因此 3⁻¹ mod 19 = 13')+note('欧几里得除法步数 O(log p)；大整数除法本身也有成本。曲线坐标模p，签名标量模n。'))
a('椭圆曲线点群与 Point 结构','点加法为什么不是坐标分别相加？',formula('y² ≡ x³ + ax + b (mod p)')+cols(code('struct Point {\n    int x = 0, y = 0;\n    bool infinity = true;\n};'),ul('加入无穷远点 O，作为加法单位元。','P+O=P；P+(−P)=O。','负点为 (x,−y mod p)；输入必须在曲线上。'))+note('Point 是小参数教学结构；真实曲线坐标是256位，库对象还可能含投影坐标及内部状态。'))
a('椭圆曲线点加与倍点','怎样从两个曲线点计算另一个曲线点？',formula('P ≠ Q：λ = (y<sub>Q</sub>−y<sub>P</sub>)(x<sub>Q</sub>−x<sub>P</sub>)⁻¹ mod p<br>P = Q：λ = (3x<sub>P</sub>²+a)(2y<sub>P</sub>)⁻¹ mod p')+formula('x<sub>R</sub> = λ²−x<sub>P</sub>−x<sub>Q</sub><br>y<sub>R</sub> = λ(x<sub>P</sub>−x<sub>R</sub>)−y<sub>P</sub>　(mod p)')+note('先处理 O、互为负点与 y=0 的倍点；这些分支结果可能为 O，不能先尝试求逆。'),'<a href="https://www.secg.org/sec1-v2.pdf">SEC 1 v2.0</a>')
a('二进制倍加与公钥生成','如何用 O(log d) 次点运算计算 Q=dG？',cols(code('R = O, P = G\nwhile k > 0:\n    if k & 1: R = R + P\n    P = P + P\n    k >>= 1\nreturn R'),ul('d 在 [1,n−1]，G 是基点，n 是G的阶。','每轮处理一位；已累积部分与剩余倍点部分仍对应原来的 dG。','b位标量最多b次倍点、b次条件加法。','从Q反推d依赖椭圆曲线离散对数难题。'))+note('教学循环带秘密相关分支，不用于生产。Core 的窗口、预计算、坐标优化属于实现选择，不是共识指定的循环。'))
a('secp256k1 的固定参数','将通用曲线公式落到 Bitcoin。',formula('a=0，b=7，p=2²⁵⁶−2³²−977，h=1')+code('p  = FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F\nGx = 79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798\nGy = 483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8\nn  = FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141')+note('坐标运算模p，私钥/nonce/签名标量模n。公开测试 d=1 → Q=G → 压缩公钥 02∥Gx；不要把这个公开值用于保管资金。'),'<a href="https://www.secg.org/sec2-v2.pdf">SEC 2 v2.0 §2.4.1</a>')
a('ECDSA 签名算法','私钥如何把消息摘要变成 (r,s)？',flow(['消息m','摘要整数z','nonce k','R=kG','输出(r,s)'])+formula('r = x<sub>R</sub> mod n<br>s = k⁻¹(z + rd) mod n')+ul('私钥d和nonce k满足 1≤d,k<n。','r或s为0时重新生成nonce。','输出签名，不输出d或k；nonce由成熟库安全管理。')+note('本课 sign_message 内部做一次 SHA-256；Bitcoin P2WPKH 使用 BIP143 预映像的双SHA-256。'))
a('ECDSA 验签与正确性','只有公钥 Q，为什么也能验证？',formula('w=s⁻¹ mod n，u₁=zw mod n，u₂=rw mod n<br>X=u₁G+u₂Q')+ul('先检查 r,s 范围，公钥编码与曲线有效性。','若 X=O 拒绝；否则检查 x<sub>X</sub> mod n = r。')+formula('Q=dG ⇒ X=(z+rd)s⁻¹G=kG=R')+note('等式证明正确签名的一致性，不单独证明不可伪造；安全还依赖参数、随机数、公钥绑定和实现。'))
a('BIP143：Bitcoin P2WPKH 签名路径','真实交易签名覆盖的是什么？',flow(['输入 / 旧币金额 / scriptCode / 输出 / 模式','BIP143预映像','双SHA-256','ECDSA','DER + 模式字节'])+ul('签名与压缩公钥一起进入对应输入的见证。','验证者重建同一摘要，并核对公钥与旧输出条件。','不是对界面金额字符串签名，也不是直接签txid。')+note('教学只签13字节草稿，内部单SHA-256，没有完整交易输入、见证与签名模式；不能广播到 Bitcoin。第6讲逐字段展开。'),'<a href="https://bips.dev/143/">BIP143</a>')
a('BIP340 Schnorr：Taproot 的签名算法','同一条曲线，为什么不是同一种签名？',formula('s = k + ed mod n　　R = sG − eP')+ul('挑战 e 用规定的带标签哈希绑定R、公钥P和消息。','还必须遵循偶y规范化、nonce生成、范围检查，不能只实现核心等式。','x-only公钥32字节，签名本体64字节；显式非默认签名模式可再加1字节。','Taproot 输出公钥还涉及 BIP341 tweak。')+note('本讲完整推导ECDSA，Schnorr完整算法放E2。不能把“Bitcoin使用ECDSA”扩大成所有输出类型都只用ECDSA。'),'<a href="https://bips.dev/340/">BIP340</a> · <a href="https://bips.dev/341/">BIP341</a>')
a('ECDSA 小曲线手算','让每个公式落到可检查的数字。',code('p=17, a=2, b=2, G=(5,1), n=19\nd=7, z=13, k=3')+table(['步骤','结果'],[['2G / 3G / 7G','(6,3) / (10,6) / Q=(0,6)'],['r / k⁻¹','10 / 13'],['s=13×(13+10×7) mod19','15'],['w / u₁ / u₂','14 / 11 / 7'],['X=11G+7Q=3G','(10,6)，x mod19 = 10，通过']])+note('这条小曲线不是 secp256k1，只用于手算。改 z=14 保留签名 (10,15)，应验签失败。'))
a('nonce 复用与私钥恢复','两份公开签名为什么会暴露私钥？',formula('k=(z₁−z₂)(s₁−s₂)⁻¹ mod n<br>d=(s₁k−z₁)r⁻¹ mod n')+code('同一d、同一k：\nz₁=13, (r,s₁)=(10,15)\nz₂=14, (r,s₂)=(10, 9)\n公开信息 → k=3 → d=7')+note('Core CKey::Sign 使用 RFC6979 确定性nonce，并可为low-R额外输入重试。相同消息的确定性签名，不等于跨不同消息不安全复用k。教学OpenSSL不承诺相同nonce路径。'),ref('key.cpp','CKey::Sign'))
a('压缩公钥与 HASH160','曲线点怎样成为传输字节和归属标识？',table(['对象','编码','长度'],[['私钥标量','d','32字节'],['未压缩公钥','04 ∥ x ∥ y','65字节'],['压缩公钥','02/03 ∥ x；前缀指示y奇偶','33字节'],['HASH160','RIPEMD160(SHA256(pubkey_bytes))','20字节']])+note('压缩公钥需恢复y并验证点；长度正确不代表点有效。同一点的不同编码有不同HASH160；标识不是完整Bitcoin地址。'),ref('pubkey.h','CPubKey / GetID'))
a('DER、Key 与 Context','数学数对和库对象的内存边界是什么？',table(['结构','当前实现','注意'],[['签名(r,s)','DER字节串，通常70–72字节','不是固定64字节'],['Key','unique_ptr&lt;EVP_PKEY, deleter&gt;','库内存大于32字节载荷'],['Context','unique_ptr&lt;EVP_MD_CTX, deleter&gt;','管理每次签名/验签上下文'],['公钥副本','DER导出公开部分再导入','验证者不拿私钥']])+note('教学DER未加Bitcoin签名模式字节，未实现low-S策略及完整脚本规则。RAII自动释放库对象；传输载荷长度不等于对象内存大小。'))
a('ECDSA 的运算与存储开销','成本来自消息长度，还是曲线计算？',table(['操作','主要工作'],[['密钥生成','安全随机标量 + dG'],['签名','O(m)消息哈希 + kG + 标量模逆/乘法'],['验签','O(m)消息哈希 + u₁G + u₂Q + 点加'],['朴素倍加','O(b)点运算；每次含模乘与模逆'],['优化方向','投影坐标减少模逆；窗口/预计算；常数时间实现']])+note('固定256位曲线不等于没有成本。实际联合乘法和上下文管理使签名/验签耗时不能按点乘次数简单推算。'))
a('EVP 消息接口与 Bitcoin 摘要接口','怎样避免不经意多做一次哈希？',cols(code('教学：\n13字节消息\n → sign_message\n → EVP内部SHA256\n → ECDSA'),code('Bitcoin P2WPKH：\nBIP143预映像\n → 双SHA256\n → CKey::Sign(digest)\n → secp256k1_ecdsa_sign'))+note('传 sha256(bytes) 给教学 sign_message，会再哈希一次；若验签仍传原文，必然与签名输入不匹配。'),ref('key.cpp')+' · '+ref('pubkey.cpp'))
a('实验环境与文件','从小曲线推演走到真实 secp256k1。',code('bash ../../code/lesson-02/run.sh')+table(['文件','实践职责'],[[local(2,'toy_curve.cpp'),'实现 inverse / add / multiply / ECDSA'],[local(2,'toy_curve_test.cpp'),'小参数遍历、nonce复用及边界验证'],[local(2,'crypto.hpp'),'OpenSSL密钥、公钥、签名、验签'],[local(2,'lab02.cpp'),'复用第1讲编码；篡改与计时']])+note('仍用C++17和OpenSSL 3；临时密钥不保存、不输出。小曲线不进入系统授权模块。'),p='实验尝试')
a('代码：模逆与二进制倍加','保持什么不变量，才能得到正确点乘结果？',cols(snippet(2,'toy_curve.cpp','int inverse','bool on_curve'),snippet(2,'toy_curve.cpp','Point multiply','// 为了可手算'))+note('inverse 同时递推余数与系数；multiply 每轮取最低位、倍点、右移。先检查合法输入，再做群运算。'),local(2,'toy_curve.cpp'),p='实验尝试')
a('代码：小曲线 ECDSA','在哪里检查标量范围、曲线点与无穷远点？',snippet(2,'toy_curve.cpp','std::optional<Signature> sign_digest','} // namespace demo')+note('sign_digest 输入z已经是摘要整数，不再哈希；真实系统用成熟库完成大整数与常数时间实现。'),local(2,'toy_curve.cpp'),p='实验尝试')
a('代码：真实密钥与公开验证者','如何确保曲线选对，并且验证端不持有私钥？',snippet(2,'crypto.hpp','inline Key generate_key','inline Bytes compressed_public')+flow(['EC / secp256k1','导出公开DER','导入公钥对象','仅公钥验签'])+note('Core 对应 CKey::MakeNewKey → CKey::GetPubKey → secp256k1_ec_pubkey_create；库接口不同，曲线与公钥数学关系相同。'),local(2,'crypto.hpp')+' · '+ref('key.cpp'),p='实验尝试')
a('代码：ECDSA 消息签名','摘要、缓冲区与错误处理如何衔接？',snippet(2,'crypto.hpp','inline Bytes sign_message','inline bool verify_message')+ul('EVP_sha256 与 EC密钥共同确定消息摘要与ECDSA。','先查询签名缓冲区长度，再写入实际DER签名并resize。','初始化、分配或签名失败抛异常。'),local(2,'crypto.hpp'),p='实验尝试')
a('代码：ECDSA 公开验签','什么结果才能判定签名被接受？',snippet(2,'crypto.hpp','inline bool verify_message','\n}\n}')+note('只有返回1才接受；0或畸形签名错误都不是成功。Core 对应 CPubKey::Verify → secp256k1_ecdsa_verify。'),local(2,'crypto.hpp')+' · '+ref('pubkey.cpp'),p='实验尝试')
a('实验：正常路径与篡改矩阵','哪些输出固定，哪些输出可以变化？',code('public_bytes=33\nkey_id_bytes=20\nvalid=true\n小曲线：Q=(0,6)，(r,s)=(10,15)')+table(['操作','预期'],[['金额60000→60001 / 收款2→3','false'],['换公钥 / 改签名 / 非法DER','false'],['先哈希再sign_message，原文验签','false'],['同一私钥再次对原文签名','true，签名字节不要求固定']])+note('真实公钥、签名字节和DER长度可随运行变化。先预测失败原因，再运行 lab02.cpp 的断言。'),local(2,'lab02.cpp'),p='实验尝试')
a('实验：性能与载荷测量','200次验签究竟测到了什么？',formula('平均耗时 = 200次验签总耗时 / 200')+ul('包含上下文分配、初始化、消息哈希与曲线验签。','不包含密钥生成、签名生成、编译或打印；使用单调时钟。','改变消息长度、多轮记录中位值；可另做上下文复用实验。')+formula('13 + 33 + (70～72) ≈ 116～118 字节')+note('这是草稿＋公钥＋DER载荷估算，未含长度前缀/容器；不是交易vsize，也不是libsecp256k1基准或网络吞吐量。'),p='实验尝试')
a('接入系统：授权验证模块','从“签过这段字节”走向“有权花这笔钱”。',table(['成果','后续位置','接口约定'],[['generate_key','第7讲密钥管理','临时密钥演进为受控存储'],['compressed_public / hash160','第5讲脚本、第7讲归属','先固定编码'],['sign_message','第4讲授权、第8讲付款','明确定义签名预映像'],['verify_message','第4讲共用检查、第10/11讲','公钥匹配旧输出条件']])+note('当前草稿没有输入引用、链标识和旧币金额，尚无完整重放保护。第3讲建立UTXO，第4讲定义教学授权预映像，第6讲另做BIP143标准实验。')+ul('验收：推导ECDSA，区分模p/n，恢复复用nonce下的私钥，解释每种失败与单次哈希边界。'),p='实验尝试')

# Keep code pages within a presentation-sized viewport without shrinking the text.
one[17:18] = [
 slide('代码：小端读写', '哪些原语会被交易、区块与网络复用？', snippet(1,'foundations.hpp','inline void put_le','// An intent')+note('put_le 按低字节到高字节写入；Reader::le 先检查长度，再推进游标。'),local(1,'foundations.hpp'),'实验尝试'),
 slide('代码：哈希与十六进制接口', '如何明确区分原始字节、摘要与展示文本？', snippet(1,'foundations.hpp','inline Hash256 sha256','inline Bytes unhex')+note('hex 将一个字节拆成两个4位索引；double_sha256 明确做两次SHA-256。第2讲 message 接口内部自带单次哈希。'),local(1,'foundations.hpp'),'实验尝试')
]
two[20:21] = [
 slide('代码：小曲线 ECDSA 签名', 'nonce与签名范围在哪里约束？', snippet(2,'toy_curve.cpp','std::optional<Signature> sign_digest','bool verify_digest')+note('r或s为0返回空值，调用者重新选择nonce。这里z已是摘要整数，不再哈希。'),local(2,'toy_curve.cpp'),'实验尝试'),
 slide('代码：小曲线 ECDSA 验签', '哪些边界必须在接受签名前检查？', snippet(2,'toy_curve.cpp','bool verify_digest','} // namespace demo')+note('检查r/s范围、公钥在曲线上且nQ=O、计算结果不是O，最后比较x坐标模n。生产授权使用成熟密码学库。'),local(2,'toy_curve.cpp'),'实验尝试')
]


# Lesson 02: practical secp256k1 workflow; mathematical derivations live in resources.
old_two = {s['title']: s for s in two}
two = [
 slide('用 secp256k1 完成付款签名与验签','第02讲 · 从真实密钥到授权验证',cols('<h2>学习重点</h2>'+ul('<b>如何签名：</b>生成secp256k1密钥，将付款字节交给ECDSA签名接口。','<b>如何验签：</b>使用公钥、原始消息和签名，判断授权是否通过。','<b>如何检查失败：</b>修改金额、收款方、公钥或签名，验证拒绝结果；检查重复哈希误用。'),'<h2>本课要解决的问题</h2><p>用真实曲线签署第1讲的付款字节，让只持有公钥的验证者检查授权。</p>'+flow(['生成密钥','签名','仅公钥验签']))+arch(2),part='本课总览'),
 old_two['secp256k1、ECDSA 与 Schnorr'],
 slide('公私钥与签名：使用所需的原理','为什么私钥留在钱包，公钥可以交给验证者？',formula('Q = dG　　secp256k1：y² = x³ + 7 mod p')+flow(['消息字节m','哈希z','私钥d + 内部nonce k','签名(r,s)'])+ul('私钥d生成公钥Q；从Q反推d依赖离散对数难题。','ECDSA：R=kG，r=xR mod n，s=k⁻¹(z+rd) mod n。库完成底层运算与nonce处理。','验证端使用公钥、同一消息和签名，不需要私钥。')+note('本讲理解输入角色并正确调用库；模逆、点加与手算推导放课后补充。'),'<a href="resources/数学原理补充.md">数学原理补充</a>'),
 old_two['数字签名与公钥认证'],
 old_two['压缩公钥与 HASH160'],
 old_two['DER、Key 与 Context'],
 old_two['EVP 消息接口与 Bitcoin 摘要接口'],
 old_two['实验环境与文件'],
 slide('实践：先跑通一笔付款授权','从第1讲的编码结果走到 true。',code('auto alice = generate_key();\nauto verifier = public_only(alice.get());\nauto message = encode({2, parse_amount("0.00060000")});\nauto signature = sign_message(alice.get(), message);\nbool accepted = verify_message(\n    verifier.get(), message, signature);')+ul('先预测 accepted，再运行 lab02.cpp。','确认 verifier 只含公钥；message 就是第1讲的13字节。','保留signature，只把金额改成60001，重新验签。'),local(2,'lab02.cpp'),part='实验尝试'),
 old_two['代码：真实密钥与公开验证者'],
 slide('代码：压缩公钥与 HASH160','如何从公钥对象得到传输字节与标识？',snippet(2,'crypto.hpp','inline Bytes compressed_public','// Input is MESSAGE BYTES')+note('压缩编码33字节，HASH160为20字节。这里观察编码；verify_message接收公钥对象，不能直接传入这段字节数组。'),local(2,'crypto.hpp'),part='实验尝试'),
 old_two['代码：ECDSA 消息签名'],
 old_two['代码：ECDSA 公开验签'],
 slide('实践：保留签名，逐次只改一项','验签是否真的覆盖了这次付款？',code('verify_message(pub.get(), message, sig);              // true\nverify_message(pub.get(), encode({2,60001}), sig);     // false\nverify_message(pub.get(), encode({3,60000}), sig);     // false\nverify_message(other.get(), message, sig);            // false\nverify_message(pub.get(), message, Bytes{0});         // false')+note('分别改金额、收款方、公钥、DER。先解释再运行；不要把多种变化混在一个实验里。'),local(2,'lab02.cpp'),part='实验尝试'),
 slide('实践：排查多做一次哈希','为什么消息看起来相同，验签却失败？',code('auto h = sha256(message);\nauto wrong = sign_message(alice.get(), Bytes(h.begin(), h.end()));\nverify_message(pub.get(), message, wrong); // false')+flow(['签名端：SHA256(SHA256(message))','验签端：SHA256(message)'])+note('修复：把原始message交给sign_message。签名和验签必须约定相同输入与哈希层次，不能凭“都用了SHA-256”认为等价。'),local(2,'lab02.cpp'),part='实验尝试'),
 old_two['实验：正常路径与篡改矩阵'],
 old_two['实验：性能与载荷测量'],
 old_two['BIP143：Bitcoin P2WPKH 签名路径'],
 old_two['接入系统：授权验证模块'],
]
two[1]['body']=two[1]['body'].replace('小曲线用二进制倍加推演','由成熟库完成标量乘法')
two[7]['body']=code('bash ../../code/lesson-02/run.sh')+table(['文件','本次实践'],[[local(2,'crypto.hpp'),'真实secp256k1密钥、编码、签名、验签'],[local(2,'lab02.cpp'),'正常授权、篡改、哈希误用与计时'],[local(2,'run.sh'),'编译运行；另附的小曲线检查无需先学习']])+note('C++17、pkg-config、OpenSSL 3。先读lab02.cpp，再进入crypto.hpp；小曲线程序作为课后材料。')
two[-1]['body']=two[-1]['body'].replace('验收：推导ECDSA，区分模p/n，恢复复用nonce下的私钥，解释每种失败与单次哈希边界。','验收：独立生成secp256k1密钥、编码、签名、仅公钥验签；解释篡改拒绝和单次哈希边界，说明与Bitcoin交易签名的差异。')
two[-2]['part']='实验尝试'


# Explain the three names through their roles; keep background at the end.
two[1] = slide('secp256k1、ECDSA 与 Schnorr','分别是什么？在签名和验签中负责什么？',table(['名称','是什么','作用与Bitcoin用途'],[
 ['secp256k1','一套标准椭圆曲线参数','提供密钥和签名运算的底层基础；ECDSA和BIP340 Schnorr都使用它。'],
 ['ECDSA','椭圆曲线数字签名算法','用私钥产生签名，用公钥验证；Bitcoin传统与SegWit v0使用，本课实际操作它。'],
 ['Schnorr（BIP340）','另一种数字签名算法的Bitcoin规范','同样负责签名与验签；用于Taproot，本课只认识用途。']])+flow(['选择secp256k1','生成密钥','用ECDSA签名 / 验签'])+note('secp256k1不是签名算法；ECDSA和Schnorr是两种签名方案。libsecp256k1是实现库的名字；本课通过OpenSSL EVP调用secp256k1上的ECDSA。'),'<a href="https://bips.dev/340/">BIP340</a> · <a href="https://bips.dev/341/">BIP341</a>')
two[2] = slide('签名与验签的输入输出','私钥留在钱包，验证端究竟拿到什么？',cols('<h2>签名端</h2>'+flow(['私钥 + 消息字节','ECDSA签名接口','签名字节']),'<h2>验证端</h2>'+flow(['公钥 + 同一消息 + 签名','ECDSA验签接口','通过 / 拒绝']))+ul('私钥只用于生成签名，不发送给验证端。','验证端使用预期授权者的公钥，不能接受任意替换的公钥。','编码或哈希约定必须一致；任何一项输入不对应，都不能当作有效授权。')+note('接下来直接查看公钥、消息和签名在代码中的类型与调用方式。'))
two.extend([
 slide('附录 A · 有限域与模逆','库内部如何完成有范围约束的计算？',ul('有限域规定底层数值计算的范围和规则。','模逆是完成部分底层计算所需的工具。','这些运算由密码学库处理；应用代码调用密钥生成、签名和验签接口。')+note('本课不实现模逆，不展开数学推导。'),part='附录'),
 slide('附录 B · 椭圆曲线点与点群','公钥在库内部以什么形式参与运算？',ul('公钥在数学上对应曲线点；应用中使用库公钥对象或标准编码。','点群描述这些点参与运算时遵守的规则。','压缩公钥的解析与有效性检查交给库，不自行构造坐标。')+note('本课关注公钥导出、编码和正确传入验签接口。'),part='附录'),
 slide('附录 C · 点加与倍点','密钥和签名计算依赖哪些底层操作？',ul('点加、倍点是曲线运算的基本操作。','它们被组合用于公钥生成、签名和验签。','库处理特殊情况、有效性及实现细节；应用代码不直接操作曲线点。')+note('本课不展示坐标公式，不要求手算。'),part='附录'),
 slide('附录 D · 标量乘法与二进制倍加','库如何高效完成公钥与签名中的曲线计算？',ul('标量乘法是将私钥等数值与曲线点结合的底层运算。','二进制倍加是理解这种运算的一种方法；生产库可采用不同优化。','使用成熟库完成真实secp256k1运算，不把教学循环用于私钥处理。')+note('本课验收仍是：正确生成密钥、签名、验签，并验证失败场景。'),part='附录')
])


# Insert between the previous pages 8 and 9: operational pseudocode, not equations.
two.insert(8, slide('签名与验签：步骤伪代码','输入、算法调用、错误分支与返回值',cols('<h2>签名</h2>'+code('FUNCTION SignPayment(sk, draft) → Bytes\n    REQUIRE IsValidSecretKey(sk, secp256k1)\n\n    message ← Encode(draft)\n    digest  ← SHA256(message)\n    signature ← ECDSA.SignDigest(sk, digest)\n\n    IF signature = ERROR THEN\n        RAISE SigningError\n    END IF\n\n    RETURN DER.Encode(signature)\nEND FUNCTION'),'<h2>验签</h2>'+code('FUNCTION VerifyPayment(pk, draft, encodedSig) → Boolean\n    IF NOT IsValidPublicKey(pk, secp256k1) THEN\n        RETURN FALSE\n    END IF\n    signature ← DER.Decode(encodedSig)\n    IF signature = ERROR THEN\n        RETURN FALSE\n    END IF\n    message ← Encode(draft)\n    digest  ← SHA256(message)\n    RETURN ECDSA.VerifyDigest(pk, digest, signature)\nEND FUNCTION'))+note('ECDSA使用secp256k1；pk是预期授权者的公钥。SignDigest / VerifyDigest的内部步骤见下两页；实际EVP消息接口将SHA-256与ECDSA合并执行，调用者只传原文。'),local(2,'crypto.hpp'),part='实验尝试'))


# Expand the two digest-level primitives immediately after their caller.
ECDSA_SIGN_PSEUDO = 'FUNCTION ECDSA.SignDigest(d, digest) → (r, s)\n    REQUIRE 1 ≤ d < n AND Length(digest) = 32\n    z ← BytesToIntegerBE(digest)\n    LOOP\n        k ← SecureRandomInteger(1, n − 1)\n        R ← ScalarMultiply(k, G)\n        r ← XCoordinate(R) MOD n\n        IF r = 0 THEN\n            CONTINUE\n        END IF\n        s ← (ModInverse(k, n) × (z + r × d)) MOD n\n        IF s ≠ 0 THEN\n            RETURN (r, s)\n        END IF\n    END LOOP\nEND FUNCTION'
ECDSA_VERIFY_PSEUDO = 'FUNCTION ECDSA.VerifyDigest(Q, digest, (r, s)) → Boolean\n    IF Length(digest) ≠ 32 THEN RETURN FALSE END IF\n    IF Q = O THEN RETURN FALSE END IF\n    IF NOT IsOnSecp256k1(Q) THEN RETURN FALSE END IF\n    IF ScalarMultiply(n, Q) ≠ O THEN RETURN FALSE END IF\n    IF NOT (1 ≤ r < n AND 1 ≤ s < n) THEN\n        RETURN FALSE\n    END IF\n    z  ← BytesToIntegerBE(digest)\n    w  ← ModInverse(s, n)\n    u1 ← (z × w) MOD n\n    u2 ← (r × w) MOD n\n    X  ← PointAdd(ScalarMultiply(u1, G),\n                  ScalarMultiply(u2, Q))\n    IF X = O THEN RETURN FALSE END IF\n    RETURN (XCoordinate(X) MOD n) = r\nEND FUNCTION'
two[9:9] = [
 slide('ECDSA.SignDigest：签名内部步骤','输入私钥与32字节摘要，输出签名数对。',code(ECDSA_SIGN_PSEUDO)+note('d：私钥；G：标准基点；n：G的阶；k：内部nonce。点运算在secp256k1上执行；标量计算取模n。r或s为0时重新生成k。'),'<a href="https://www.secg.org/sec1-v2.pdf">SEC 1 v2.0 §4.1.3</a>',part='实验尝试'),
 slide('ECDSA.VerifyDigest：验签内部步骤','只使用预期公钥、同一摘要和签名，不需要私钥。',code(ECDSA_VERIFY_PSEUDO)+note('O：无穷远点；IsOnSecp256k1检查坐标范围与曲线关系。摘要按大端转整数；此处限定SHA-256与secp256k1，DER解析由外层完成。'),'<a href="https://www.secg.org/sec1-v2.pdf">SEC 1 v2.0 §4.1.4</a>',part='实验尝试')
]

CSS='''
:root{color-scheme:dark;--bg:#202328;--panel:#30343b;--line:#4b515c;--text:#edf0f5;--muted:#b2bbc8;--wire:#a9bcd3;--state:#88cec0;--gold:#e7be6d;--gold-bg:#4e4129}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:20px/1.65 "PingFang SC","Microsoft YaHei",sans-serif}a{color:#a5cbe9;text-underline-offset:.2em}button,input,select{font:inherit;color:inherit;background:var(--panel);border:1px solid #657180;border-radius:5px;padding:7px 12px}button{cursor:pointer}button:disabled{opacity:.4;cursor:default}:focus-visible{outline:2px solid white;outline-offset:4px}header{display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid var(--line);padding:12px 3vw;font-size:14px}header nav{display:flex;gap:20px;flex-wrap:wrap}.brand{color:var(--muted)}main{max-width:1440px;margin:auto;padding:22px 4vw 100px}.slide{min-height:calc(100dvh - 180px)}.slide[hidden]{display:none}.part{color:var(--state);font-size:16px;margin:0 0 12px}.slide h1,.slide h2.slide-title{font-size:clamp(30px,3.2vw,46px);letter-spacing:-.035em;line-height:1.25;margin:0 0 14px}.question{font-size:22px;color:var(--muted);margin:0 0 26px}.slide h2:not(.slide-title),h3{font-size:23px;margin:8px 0 12px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:start}.columns>div{min-width:0}p{margin:12px 0}ul{padding-left:1.2em;margin:14px 0}li{margin:10px 0}b,strong{font-weight:650;color:#fff}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:19px}th,td{border-bottom:1px solid var(--line);padding:12px 16px;text-align:left;vertical-align:top}th{background:var(--panel);color:var(--muted);font-weight:500}td:first-child{color:var(--state)}pre{background:#262a30;border:1px solid var(--line);border-left:3px solid var(--wire);padding:18px 22px;overflow:auto;tab-size:4;font:17px/1.55 "SFMono-Regular",Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}code{font-family:"SFMono-Regular",Consolas,monospace;color:#d7e5f4}p code,li code,td code{font-size:.88em}.formula{font-family:"Cambria Math","STIX Two Math","PingFang SC",serif;font-size:clamp(22px,2.3vw,31px);padding:20px 24px;background:var(--panel);border-left:3px solid var(--state);line-height:1.9;margin:16px 0;overflow-wrap:anywhere}.takeaway{border-top:1px solid var(--line);padding-top:17px;margin-top:24px;color:var(--state);font-size:19px}.source{font-size:14px;color:var(--muted);margin-top:20px}.flow{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:24px 0}.flow span{border:1px solid var(--line);background:var(--panel);padding:12px 16px;border-radius:5px}.flow span+span:before{content:'→';color:var(--wire);margin-right:12px}.architecture{margin-top:24px;border:1px solid var(--line);background:radial-gradient(#424852 1px,transparent 1px) 0 0/22px 22px;border-radius:8px;overflow:auto}.architecture svg{display:block;width:100%;min-width:780px}.module{fill:var(--panel);stroke:#636d7a}.hot{fill:var(--gold-bg);stroke:var(--gold);stroke-width:2}.svg-label,.svg-text{fill:var(--text);font-size:17px}.svg-small{fill:#c5ced9;font-size:14px}.edge{stroke:var(--wire);stroke-width:2}footer{position:fixed;bottom:0;inset-inline:0;background:var(--bg);border-top:1px solid var(--line);padding:12px 3vw;display:flex;align-items:center;gap:12px;font-size:15px;z-index:2}.progress{height:3px;position:absolute;top:-2px;left:0;background:var(--state);width:0}footer .spacer{flex:1}.hint{color:var(--muted)}dialog{background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:8px;width:min(850px,92vw);max-height:85dvh;padding:24px}dialog::backdrop{background:#000a}dialog nav{display:grid;grid-template-columns:1fr 1fr;gap:6px}dialog a{display:block;padding:9px;border-bottom:1px solid var(--line);font-size:16px;text-decoration:none}dialog a[aria-current=page]{background:var(--panel);color:var(--state)}.dialog-head{display:flex;align-items:center;justify-content:space-between}form{display:grid;grid-template-columns:auto 1fr;gap:16px;align-items:center}form button{grid-column:2}.skip{position:fixed;top:-100px;background:var(--panel);z-index:10;padding:12px}.skip:focus{top:0}.reading .slide{display:block!important;min-height:0;border-bottom:1px solid var(--line);padding-bottom:60px;margin-bottom:60px}.reading main{max-width:1200px}.reading footer .paging{display:none}.reading .slide-title{scroll-margin-top:20px}
@media(min-width:1500px){body{font-size:23px}table{font-size:21px}pre{font-size:19px}}
@media(max-width:800px){body{font-size:18px}.columns{grid-template-columns:1fr;gap:12px}main{padding:22px 18px 120px}.question{font-size:19px}table{font-size:16px}th,td{padding:10px}pre{font-size:14px}.hint,.brand{display:none}header{font-size:13px}header nav{gap:12px}footer{gap:7px;flex-wrap:wrap}footer button{font-size:14px;padding:7px}dialog nav{grid-template-columns:1fr}.source{overflow-wrap:anywhere}}
@media print{@page{size:landscape;margin:12mm}body{font-size:13pt;background:#fff;color:#111}header,footer,.skip,dialog{display:none!important}main{padding:0;max-width:none}.slide,.slide[hidden],.reading .slide{display:block!important;break-after:page;min-height:0;padding:0;margin:0;border:0}.slide:last-child{break-after:auto}.slide h1,.slide h2.slide-title{font-size:25pt}.question{font-size:15pt}.part,.takeaway,td:first-child{color:#24594e}b,strong,code{color:inherit}pre,.formula,th{background:#f3f4f6;color:#111}pre{font-size:10pt}table{font-size:12pt}a{color:#234e75}.source{font-size:9pt}.architecture{background:#262a30;print-color-adjust:exact}form{display:none}}
'''
JS='''
const slides=[...document.querySelectorAll('.slide')], dialog=document.querySelector('dialog');
let current=0,reading=false;
const prev=document.querySelector('#prev'),next=document.querySelector('#next'),count=document.querySelector('#count');
function show(i,focus=false){current=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,j)=>s.hidden=!reading&&j!==current);prev.disabled=current===0;next.disabled=current===slides.length-1;count.textContent=`${current+1} / ${slides.length}`;document.querySelector('.progress').style.width=`${100*(current+1)/slides.length}%`;document.querySelectorAll('[data-goto]').forEach((a,j)=>{if(j===current)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});history.replaceState(null,'',`#page-${current+1}`);if(!reading)window.scrollTo(0,0);if(focus){const h=slides[current].querySelector('.slide-title');h.focus({preventScroll:true});if(reading)h.scrollIntoView()}}
prev.onclick=()=>show(current-1,true);next.onclick=()=>show(current+1,true);
document.querySelector('#toc').onclick=()=>dialog.showModal();document.querySelector('#close').onclick=()=>dialog.close();
document.querySelectorAll('[data-goto]').forEach(a=>a.onclick=ev=>{ev.preventDefault();dialog.close();show(Number(a.dataset.goto),true)});
document.querySelector('#reading').onclick=()=>{reading=!reading;document.body.classList.toggle('reading',reading);document.querySelector('#reading').textContent=reading?'分页展示':'连续阅读';document.querySelector('#reading').setAttribute('aria-pressed',reading);show(current,true)};
const full=document.querySelector('#fullscreen');if(!document.fullscreenEnabled)full.hidden=true;full.onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{full.textContent='全屏不可用'}};document.addEventListener('fullscreenchange',()=>full.textContent=document.fullscreenElement?'退出全屏':'全屏');
document.addEventListener('keydown',ev=>{if(reading||dialog.open||ev.altKey||ev.metaKey||ev.ctrlKey||ev.target.closest('input,textarea,select,button,a,[contenteditable]'))return;let target;if(['ArrowRight','PageDown'].includes(ev.key))target=current+1;if(['ArrowLeft','PageUp'].includes(ev.key))target=current-1;if(ev.key==='Home')target=0;if(ev.key==='End')target=slides.length-1;if(target!==undefined){ev.preventDefault();show(target,true)}});
window.addEventListener('hashchange',()=>{const m=location.hash.match(/^#page-(\\d+)$/);if(m)show(Number(m[1])-1,true)});
const initial=location.hash.match(/^#page-(\\d+)$/);show(initial?Number(initial[1])-1:0);
const form=document.querySelector('#amount-form');if(form){function calculate(ev){ev?.preventDefault();const output=document.querySelector('#amount-output');try{const s=document.querySelector('#amount').value,rs=document.querySelector('#recipient').value;if(s.length>32||!/^\\d+(\\.\\d{1,8})?$/.test(s))throw Error('金额格式无效：数字＋最多8位小数，不接受空白或符号');const [w,f='']=s.split('.');const amount=BigInt(w)*100000000n+BigInt(f.padEnd(8,'0'));if(amount>2100000000000000n)throw Error('金额超过 MAX_MONEY');if(!/^\\d{1,10}$/.test(rs)||BigInt(rs)>4294967295n)throw Error('收款标识超出 uint32');const le=(v,n)=>Array.from({length:n},(_,i)=>Number((v>>BigInt(8*i))&255n).toString(16).padStart(2,'0')).join(' ');output.textContent=`amount_sat=${amount}\\nversion   | recipient   | amount\\n01        | ${le(BigInt(rs),4)} | ${le(amount,8)}\\nwire_bytes=13`}catch(err){output.textContent=`拒绝：${err.message}`}}form.addEventListener('submit',calculate);calculate()}
'''

def build(n,slides, *, adjacent=None, lesson_title=None, extra_css="", extra_js=""):
    directory=next(LESSONS.glob(f'{n:02}-*'))
    adjacent = 3-n if adjacent is None else adjacent
    other=next(LESSONS.glob(f'{adjacent:02}-*'))
    title=f'第{n:02}讲 · '+(lesson_title or ('字节、金额与确定性编码' if n==1 else '密钥、哈希与数字签名'))
    sections=[]
    for i,s in enumerate(slides):
        tag='h1' if i==0 else 'h2'
        sections.append(f'<section class="slide" id="page-{i+1}"><p class="part">{s["part"]} / {i+1:02}</p><{tag} class="slide-title" tabindex="-1">{s["title"]}</{tag}><p class="question">{s["q"]}</p>{s["body"]}'+(f'<p class="source">{s["source"]}</p>' if s['source'] else '')+'</section>')
    toc=''.join(f'<a href="#page-{i+1}" data-goto="{i}">{i+1:02}　{s["title"]}</a>' for i,s in enumerate(slides))
    html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{CSS}{extra_css}</style></head><body>
<a class="skip" href="#main">跳至课程内容</a><header><span class="brand">{title}</span><nav aria-label="课程资源"><a href="../课程展示/课程展示.html">课程大纲</a><a href="../00-overview/btc-wallet.html">系统架构</a><a href="讲义.md">完整讲义</a><a href="../{other.name}/课堂展示.html">第{adjacent:02}讲</a></nav></header><main id="main">{''.join(sections)}</main>
<footer><div class="progress"></div><button id="toc">目录</button><button id="reading" aria-pressed="false">连续阅读</button><button id="fullscreen">全屏</button><span class="spacer"></span><span class="hint">← → 翻页</span><button id="prev" class="paging">上一页</button><span id="count" aria-live="polite"></span><button id="next" class="paging">下一页</button></footer>
<dialog aria-labelledby="toc-title"><div class="dialog-head"><h2 id="toc-title">{title}</h2><button id="close">关闭</button></div><nav aria-label="课内目录">{toc}</nav></dialog><script>{JS}{extra_js}</script></body></html>'''
    (directory/'课堂展示.html').write_text(html)
    print(f'{directory.name}: {len(slides)} pages')
if __name__=='__main__':
    build(1,one);build(2,two)
