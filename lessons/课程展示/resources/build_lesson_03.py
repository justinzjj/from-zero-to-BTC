"""从实际 C++ 文件、实测输出与共用课件模板生成第 03 讲。"""
from build_lesson_html import LESSONS, build, code, cols, flow, formula, local, note, ref, slide, snippet, table, ul

slides = []
def add(title, question, body, source='', practice=False):
    slides.append(slide(title, question, body, source, '实验尝试' if practice else '基础知识'))

def src(file, start, end):
    return snippet(3, file, start, end)

diagram = '<img class="ledger-diagram" src="resources/付款状态.svg" alt="花费 U:0 的十万聪，检查后创建 B:0 六万聪和 B:1 三万九千聪，费用一千聪。">'
diagram += '<div class="mobile-ledger"><b>花费前</b>　U:0　100000 聪<hr><b>检查</b>　旧键唯一且可用<br>100000 − 99000 = 1000 聪费用<hr><b>花费后</b>　B:0 收款 60000 聪<br>　　　　 B:1 找零 39000 聪</div>'
overview = """
<div class="overview-grid">
<section><h2>学习重点</h2>
<dl class="focus-list">
<dt>概念</dt><dd>UTXO、outpoint、交易输入与输出、找零、手续费。</dd>
<dt>算法</dt><dd>输入查找、重复输入检查、金额检查、UTXO 状态更新。</dd>
<dt>数据结构</dt><dd>OutPoint、交易输入与输出、Coin、UTXO 集合。</dd>
<dt>掌握目标</dt><dd>用简单数组和循环实现最小账本，完成付款并拒绝重复花费。</dd>
</dl></section>
<section><h2>本课要解决的问题</h2>
<p>前两讲已能编码付款信息、签名和验签。签名仍不能说明这笔钱是否存在、是否已经花过。</p>
<ol><li>付款引用哪一笔已有资金？</li><li>怎样判断这笔资金仍然可花？</li><li>付款后，哪些旧记录删除、哪些新记录产生？</li></ol>
<p class="payment-path"><span>引用旧输出</span><span>→ 检查输入和金额</span><span>→ 消耗旧输出</span><span>→ 创建收款与找零输出</span></p>
</section></div>
<section class="system-position"><h2>系统位置</h2>
<div class="system-links"><a href="../00-overview/btc-wallet.html"><b>W5 交易构造</b> · 钱包完整架构 ↗</a>
<a href="../00-overview/btc-full-node.html"><b>N8 UTXO 视图</b> · 全节点完整架构 ↗</a></div>
<p><b>本课产出</b>　可执行付款、维护可花资金、拒绝重复花费的最小账本。授权检查在第 04 讲接入。</p></section>
"""
slides.append(slide('第 03 讲 · UTXO 与最小账本', '', overview,
                    part='课程总览'))
# 同一组课堂记录同时用于讲义、投影和验收截图。
handout = (next(LESSONS.glob('03-*')) / '讲义.md').read_text()

def lesson_table(heading, *, layout='', highlights=None):
    """读取指定小节的第一张 Markdown 表；高亮仅修饰投影，不改变字段值。"""
    section = handout.split('#### ' + heading + '\n', 1)[1]
    lines = section[section.index('| '):].split('\n\n', 1)[0].splitlines()
    rows = [[cell.strip() for cell in line.strip('|').split('|')] for line in lines]
    rendered = table(rows[0], rows[2:])
    for label, status in (highlights or {}).items():
        rendered = rendered.replace('<tr><td>'+label+'</td>', f'<tr class="{status}"><td>{label}</td>')
    return f'<div class="lesson-table {layout}">{rendered}</div>'

old_rows = lesson_table('付款前 · 三条记录',layout='coins-grid',highlights={'U':'spent-row'})
new_rows = lesson_table('付款后 · 四条记录',layout='coins-grid',highlights={'B':'new-row'})
core_objects = ref('primitives/transaction.h','Core v29.0 · COutPoint、CTxOut')+' · '+ref('coins.h','Coin')
add('UTXO 与当前可花资金表','Alice 想付给 Bob 60000 聪。账本中哪几条记录与她有关？',
    '<p>一行是一条未花费的交易输出。U、V、W 是构造的交易 ID 简称，高度也是示意值。Alice、Bob 标记谁能满足条件；链上输出保存脚本。</p>'+
    old_rows+note('钱包认出两条 Alice 的输出，得到 100000 + 20000 = 120000 聪。节点无需归并人名。花费还要满足授权、coinbase 成熟期等适用条件。'),
    '用表格表达当前状态，无须 SQL。 · '+ref('coins.h','Core v29.0 · Coin'))
add('OutPoint 与联合主键','三条记录的序号都是 0。只给节点一个 0，它该查哪条？',
    table(['创建交易 txid','输出序号 vout','合起来读','命中的旧输出'],[
        ['U','0','U:0','100000 聪 · Alice'],['V','0','V:0','20000 聪 · Alice'],['W','0','W:0','8000 聪 · Bob']])+
    note('txid + vout 整体唯一。vout 从 0 开始，表示输出在创建交易中的位置。移动数组中的记录不会改变它。付款 B 稍后会产生 B:0、B:1，单靠 B 也分不清。'),core_objects)
add('交易 B 的输入表与输出表','Alice 拥有 120000 聪，这笔交易实际引用了多少？',
    '<h3>输入 · 只选一条旧输出</h3>'+lesson_table('B 的输入',layout='input-grid')+
    '<h3>输出 · 钱包填写两笔金额和条件</h3>'+lesson_table('B 的输出',layout='output-grid')+
    note('“收款”和“找零”是钱包的用途说明。输出本身只有金额和脚本，输入金额要回到 U:0 查。'),core_objects)
add('交易检查与整笔更新','钱包构造 B 后，节点在哪一步才可以动账？',
    lesson_table('付款过程',layout='compact-grid')+
    note('广播或进入交易池只表示待确认。真实节点连接区块时按顺序应用交易。任一检查失败，保留执行前的状态。'),ref('validation.cpp','Core v29.0 · UpdateCoins'))
add('付款前后变化表','假设区块 900003 包含 B。对照两张表，哪一行消耗、哪两行新增？',
    '<h3>执行前 · 3 条　<span class="spent-ink">− 消耗 U:0</span></h3>'+old_rows+
    '<h3>执行后 · 4 条　<span class="new-ink">+ 新增 B:0、B:1</span></h3>'+new_rows+
    note('V:0、W:0 原样保留。U:0 再查失败，历史交易 U 仍在区块里。Bob 下次花新收的 60000 聪，应引用 B:0。'),
    'B 是普通交易，两个新输出继承所在区块高度，coinbase 标记均为 false。')
add('COutPoint、CTxOut 与 Coin 的真实字段','读 U:0 这一行：哪些字段用于定位，哪些来自交易，哪些由节点补上？',
    '<p><b>COutPoint（键） → Coin（值）</b>　Coin.out 保存 CTxOut。Coin 自身没有 OutPoint，输出自身也不写 txid 和序号。</p>'+
    lesson_table('真实字段表',layout='field-grid',highlights={'COutPoint':'key-field'})+
    note('节点保存检查旧输出所需的信息。签名、公钥等授权材料由花费交易按输出类型提供。'),core_objects)
add('P2WPKH 输出的网络序列化','把 U:0 的 100000 聪写成一条真实格式的输出，需要传哪些字节？',
    lesson_table('P2WPKH 输出的网络序列化',layout='wire-grid')+
    formula('8 + 1 + 22 = 31 字节')+
    '<p>顺序拼接表中三行就是完整构造样本。外层 <b>0x16</b> 数整段脚本的 22 字节；脚本里的 <b>0x14</b> 数接下来的 20 字节公钥哈希。00 是见证版本 0。</p>'+
    note('钱包从地址生成脚本，公钥哈希是脚本中的数据。这个样本没有对应的链上交易。')+
    '<details><summary>网络字节、内存对象与 chainstate 存储</summary><p>31 字节只计一条网络输出。Core 内存对象另含容器或元数据。chainstate 用另一套键编码和金额、脚本压缩；数据库键中的序号用 VARINT，交易输入中的 OutPoint 用 32 字节标识加固定 4 字节小端序号。</p></details>',
    '<a href="https://developer.bitcoin.org/reference/transactions.html">Bitcoin 交易格式</a> · <a href="https://bips.dev/141/">BIP 141</a> · '+ref('txdb.cpp','CoinEntry'))
add('教学结构与 Bitcoin 字段对照','现在要写最小账本，哪些字段要保留，哪些规则留到下一讲？',
    lesson_table('教学代码对照表',layout='compact-grid')+
    note('三条示意记录中，付款只引用 U:0。C++ 用一条旧记录起步，所以程序显示 1 → 2；课堂完整表显示 3 → 4。'),
    local(3,'ledger.hpp'))
add('交易结构与付款构造','怎样把付款意图组织成一笔交易？',
    '<p>已经确定教学账本保留哪些字段。现在把“花费 U:0，给 Bob 60000 聪，给 Alice 找零 39000 聪”写成一笔交易。</p>'+
    cols(lesson_table('交易结构与付款构造'),
         '<h3>payment 的参数 old 就是 U:0</h3>'+src('lab03.cpp','static Transaction payment','static void print_book'))+
    '<p>返回的交易描述想花哪条旧记录、想创建哪些新输出。<b>此时还没有修改账本。</b>交易 ID B 给新输出命名：B:0 和 B:1。</p>'+
    '<details><summary>查看交易结构体定义</summary>'+src('ledger.hpp','struct OutPoint','// error')+'</details>'+
    note('交易构造好了，但输入只写了 U:0。节点还不知道它是否存在、里面有多少钱，下一步要查账。'),local(3,'lab03.cpp'))
add('OutPoint 查询与旧输出读取','节点收到交易后，怎样根据输入找到要花费的旧资金？',
    '<p class="lookup-path">输入 U:0 → 按 txid 和输出序号查询 → 找到旧输出 → 读取金额与花费条件</p>'+
    lesson_table('OutPoint 查询与旧输出读取')+
    cols('<h3>这段循环实现表中的查找步骤</h3>'+src('ledger.cpp','int Ledger::find','// 先比较'),
         '<p>最坏比较 n 行。slot 是当前数组位置，输出序号是创建交易中的位置。先排除 −1 再访问数组。查询只读；缺失可能意味着从未存在，也可能已经花费。</p>'
         '<p><b>输入给引用，节点从自己的账本读金额。</b>Bitcoin 还读旧 scriptPubKey；教学用 recipient 代替，第 04 讲接入授权检查。</p>')+
    note('找到 U:0，说明旧输出存在。但同一笔交易若写两次 U:0，两次单独查询都会成功，下一步要排除重复引用。'),local(3,'ledger.cpp'))
add('重复输入检查','如果两行输入都指向 U:0，两次查询都会命中。为何仍须拒绝？',
    '<p><b>正常输入 [U:0]</b>：累计 100000。若误写成 <b>[U:0, U:0]</b>，读第二项时会再次命中同一条旧输出。与第一项比对发现重复，立即拒绝，账本仍是原来的三条记录。</p>'+
    src('ledger.cpp','    for (int i = 0; i < tx.input_count; ++i) {\n        const OutPoint& key = tx.vin[i].previous;\n        for (int j','    for (int i = 0; i < tx.output_count;')+
    note('每个输入只与此前的输入比较。前缀保持唯一，才可以把旧币金额加进 incoming。比较 O(i²)，查找 O(in)，额外空间 O(1)。'),ref('consensus/tx_check.cpp','CheckTransaction'))
add('找零、金额范围与手续费','节点看到两条同类输出。它如何算费用，又如何避免累计溢出？',
    formula('100000 − (60000 + 39000) = 1000 聪')+
    '<p>把给 Bob 的金额改为 62000，找零仍为 39000，输出合计 101000。Alice 虽有 120000，但这笔交易只引用 100000，仍差 1000，必须拒绝。</p>'+
    src('ledger.cpp','static bool add_amount','// 只接收')+
    note('两侧分别从零累加，余量够才加。输入须覆盖输出；差额就是费用，本交易没有第三个矿工输出。累计 O(i+o)，额外空间 O(1)。'),ref('consensus/amount.h','MoneyRange')+' · '+ref('consensus/tx_verify.cpp','CheckTxInputs'))
add('UTXO 状态更新','通过哪些检查之后，才可以删除第一条旧记录？',
    '<p>下图只画本次付款涉及的输出。Alice 的 V:0（20000 聪）和 Bob 的 W:0（8000 聪）从头到尾保留，因此完整集合由 3 条变为 4 条。</p>'+diagram+flow(['计数合法','输入唯一且存在','单项、总额合法','容量足够、新键无冲突'])+
    note('在单线程内先完整检查，再删除、追加。失败沿用原账本。总耗时 O(i² + (i+o)n + L)，临时编码 O(L)。'),ref('validation.cpp','UpdateCoins')+' · '+ref('coins.cpp','SpendCoin / AddCoins'))

demo = """<div class="demo"><label for="pay">收款金额（聪）</label> <input id="pay" type="text" inputmode="numeric" value="60000" size="10">
<button id="spend">提交 U:0</button> <button id="reset-book">恢复付款前的账本</button>
<p>找零固定为 39000 聪。试填 62000，再改回 60000 连续提交两次。</p>
<output id="verdict" aria-live="polite"></output><pre id="view" aria-live="polite"></pre></div>"""
add('UTXO 状态转移演示','连续两次提交同一笔付款，第二次会留下哪些记录？',demo + note('恢复后可从三条原始记录再试一次。C++ 实验只放入本次用到的 U:0，便于逐行核对检查结果。'))
# 拓展只改变阅读路径。课堂程序仍从同一个 U:0 夹具启动。
def extension(title, question, body, sources):
    slides.append(slide(title, question, body, sources, part='拓展理解'))

def sources(*items):
    return ' · '.join(f'<a href="{url}">{label}</a>' for label, url in items)

btc_docs = 'https://developer.bitcoin.org/devguide/'
eth_docs = 'https://ethereum.org/en/developers/docs/'

extension('Bitcoin 的 UTXO 模型与 Ethereum 的账户模型',
    '单独取出本次使用的 100000，暂忽略两条未参与输出和费用。Alice 有 100000 单位，付给 Bob 60000。剩余的 40000 记在哪里？',
    """<div class="state-pair">
    <section><h3>Bitcoin · 输出</h3><p>付款前</p><div>U:0　Alice　100000</div>
    <p>↓　整笔消耗 U:0</p><div>B:0　Bob　60000<br>B:1　Alice　40000</div></section>
    <section><h3>Ethereum · 账户</h3><p>付款前</p><div>Alice　100000　nonce 7<br>Bob　0</div>
    <p>↓　从 Alice 账户发送，携带 nonce 7</p><div>Alice　40000　nonce 8<br>Bob　60000</div></section></div>""" +
    note('左边新增找零键 B:1。右边保留原账户，只收款的 Bob 不增加发送序号。两边使用同一教学单位。'),
    sources(('Bitcoin 开发指南 · 交易', btc_docs+'transactions.html'), ('Ethereum · 账户', eth_docs+'accounts/')))

extension('钱包、交易池与活动链 UTXO 集合',
    '恢复主课的 1000 聪费用。钱包已经显示“待确认”，节点何时才会从活动链视图移除 U:0？',
    table(['观察位置','看到的记录','这时能下什么结论？'],[
        ['Alice 的钱包','U:0　100000 聪','同步时匹配自己跟踪的输出脚本，并跟踪后续花费；可用余额还取决于确认等条件。'],
        ['构造交易 B','输入 U:0 → Bob 60000 + 找零 39000','输入点名 txid + vout。每个输出保存金额和花费条件，地址帮助钱包生成条件。'],
        ['节点的交易池','B 待确认；活动链仍有 U:0','查旧币、验授权、验金额及时间等规则，再检查本地接纳策略。广播本身不改变链状态。'],
        ['活动链连接区块','删除 U:0 → 加入 B:0、B:1','按块内顺序更新；历史保留 U 与 B。重组时撤销旧分支，再执行新分支。']])+
    note('查表解决给定分支上的重复花费。不同有效分支各花一次 U:0 时，节点还要依据累计工作量选择活动链。'),
    ref('validation.cpp','Core v29.0 · UpdateCoins / DisconnectBlock')+' · '+sources(('Bitcoin 开发指南 · 区块链',btc_docs+'block_chain.html')))

extension('显式输入、选币与找零',
    '同样显示 100000 聪，一笔大收入和十笔小收入付起款来有什么区别？',
    cols('<h3>验证者看到的依赖</h3>'+ul(
        '键唯一 → 可查明是哪笔旧币。两笔候选交易点名同一键，冲突立即可见。',
        '输入取旧值、输出写新值 → 核对去重与金额范围后，可直接算差额。',
        '无共同输入 → 部分检查可并行；若子交易引用父输出，状态更新仍有先后。'),
         '<h3>钱包与节点承担的成本</h3>'+ul(
        '选哪几笔、找零多少？同费率下，同类小币合并通常增加虚拟大小与费用。',
        '分开收款可分别管理资金；合并输入或识别找零，也可能暴露关联。',
        '未花小币积累会占用存储与缓存。Core 的 dust 门槛属于转发策略，钱包还须按实际费率判断值不值得花。'))+
    note('若两人都要改同一个状态输出，两次更新会争用同一键。合约可以围绕输出设计，但必须处理后继状态与更新顺序。'),
    ref('wallet/spend.cpp','Core v29.0 · AvailableCoins')+' · '+ref('policy/policy.cpp','GetDustThreshold / IsDust'))

# 投影时按需展开同一张对照表，字段和讲义保持一致。
comparison = handout[handout.index('| 对照项 |'):].split('\n\n', 1)[0]
comparison_rows = [line.strip('|').split('|') for line in comparison.splitlines()]
comparison_table = table(comparison_rows[0], comparison_rows[2:])

extension('账户 nonce 与合约持久状态',
    'Alice 的旧签名还能验证。账户怎样拒绝第二次扣款？同一份合约被两人调用，又会怎样？',
    cols('<h3>付款与重放</h3>'+formula('Alice：nonce 7 → 8')+
         '<p>下一笔须匹配 8。普通 ETH 转账另按已用 gas × 有效单价付费，基础费销毁，优先费归区块提议者。Bitcoin 的费用取输入与输出差额。</p>',
         '<h3>同一地址的售票合约</h3>'+formula('已售票数：17 → 18 → 19')+
         '<p>账户记录余额、nonce、代码哈希和存储根。两次调用共享持久存储，须处理读写依赖；持续新增记录也会扩大状态。</p>')+
    '<p>账户模型规定怎样更新记录，PoS 负责就链的历史达成共识。</p>'+
    '<details><summary>展开八项模型对照</summary>'+comparison_table+'</details>'+
    '<details><summary>课堂讨论 · 用上述付款解释五个问题</summary><ol>'+
    ''.join('<li>'+q+'</li>' for q in [
        '签名正确，为什么交易仍可能无效？','钱包显示余额足够，为什么付款费用可能很高？',
        '两笔交易分别花不同 UTXO，是否就一定可以完全并行？','为什么账户模型也要防止同一笔付款重复执行？',
        '哪种模型更适合本课的简单系统？你愿意承担哪项代价？'])+'</ol></details>',
    sources(('Ethereum · 交易与 nonce',eth_docs+'transactions/'),('gas 与费用',eth_docs+'gas/'),('完整八项对照表见讲义','讲义.md')))

add('初始测试账本与付款构造','如何从 BEFORE 中的 U:0 构造一入两出的交易？从本讲目录运行下列命令。',
    code('bash ../../code/lesson-03/run.sh')+
    cols(src('lab03.cpp','    Ledger book = Ledger::fixture();','    Ledger initial = book;'),ul('C++17、Bash、pkg-config、OpenSSL 3。脚本编译并运行。','初始记录由 fixture 建立，非创世输出。read 拷贝一行，find 核对旧键。','先预测两条新记录的序号，再读 AFTER。'))+
    '<details><summary>查看教学代码怎样算出 B（v3 编码）</summary>'+flow(['03 · 版本','输入数','U:0 · 36 字节','输出数','两条输出 · 24 字节'])+
    formula('L = 3 + 36i + 12o = 63 字节')+
    '<p>整数小端，输出先写 8 字节金额，再写 4 字节收款标识。这是教学交易格式；Bitcoin 使用自己的交易序列化。对完整字节做双 SHA-256，时间和缓冲均为 O(L)。不能直接哈希含空槽和填充的结构体。v1 草稿和 02A 签名示例都缺旧输出引用。</p></details>',
    local(3,'run.sh')+' · '+local(3,'lab03.cpp'), True)
add('Ledger::apply 与状态更新','为什么不能把一次预检回执当作以后修改账本的凭证？',
    src('ledger.cpp','Result Ledger::apply','\n}\n}')+
    note('apply 重查当前交易与账本。删除时按键重新定位，避免末行搬移后使用旧槽位。写入阶段没有分配或哈希调用。'),local(3,'ledger.cpp'),True)
output = (next(LESSONS.glob('03-*'))/'resources/正常与失败输出.txt').read_text().splitlines()
add('输出键与交易重放','两条新记录如何区分？再次提交同一笔交易时，还能找到旧键吗？',
    code('\n'.join(output[:7]))+note('第二次提交给出 missing or spent。两条新输出逐字段保持原值。'),'<a href="resources/正常与失败输出.txt">完整运行输出</a>',True)
add('失败实验与授权边界','哪一种修改可以通过全部金额规则？',
    code('\n'.join([*output[7:14],output[20],output[21]]))+
    note('数量 −1、0、5 在访问数组前被拒绝。每次拒绝都核对行数、顺序、完整键、金额和收款标识。改收款人仍满足金额规则，必须在后续检查授权。'),local(3,'lab03.cpp'),True)
add('线性查找的代价与系统接入','查首行、末行和缺失键各要比较几次？下一讲在哪里接入授权检查？',
    cols(ul('余额求和要扫描全部 n 行，时间 O(n)，游标与累计值占 O(1) 额外空间。','平衡树查找 O(log n)，哈希表平均 O(1)、最坏 O(n)，需要额外索引。固定数组占 O(C)，本课容量 C=4。','查 n 行最多比较 n 次。调整数组容量后重新对照 sizeof 与 63 字节线格式。',output[-2],'time ../../code/build/lesson-03/lab03 会计入启动与输出时间。'),
         ul('W5 提供 vin/vout；N8 维护 OutPoint → Coin。','第 04 讲在提交前核对旧输出花费条件与授权。','脚本、交易池、区块与网络在后续课程接入。')),
    '<a href="../01-字节、金额与确定性编码/课堂展示.html">第 01 讲 · 金额与编码</a> · <a href="resources/验证记录.txt">C++ 验证记录</a> · <a href="resources/参考来源.md">Core v29.0 源码索引</a>',True)

demo_js = """
const pay = document.querySelector('#pay'), view = document.querySelector('#view'), verdict = document.querySelector('#verdict');
let spent = false;
function resetBook(){
    spent = false; pay.value = '60000'; verdict.textContent = '等待提交';
    view.textContent = '付款前（3 条）\\nU:0　Alice　100000 聪\\nV:0　Alice　20000 聪\\nW:0　Bob　8000 聪';
}
document.querySelector('#reset-book').onclick = resetBook;
document.querySelector('#spend').onclick = () => {
    if (spent) { verdict.textContent = '拒绝：U:0 已花费'; return; }
    const raw = pay.value;
    if (!/^[0-9]+$/.test(raw) || raw.length > 16 || BigInt(raw) > 2100000000000000n) {
        verdict.textContent = '拒绝：请输入范围内的非负整数聪'; return;
    }
    const amount = BigInt(raw), fee = 100000n - amount - 39000n;
    if (fee < 0n) { verdict.textContent = '拒绝：输出总额超过 100000 聪'; return; }
    spent = true;
    verdict.textContent = '接受：手续费 ' + fee + ' 聪';
    view.textContent = '付款后（4 条，B 表示本次交易）\\nV:0　Alice　20000 聪\\nW:0　Bob　8000 聪\\nB:0　Bob　' + amount + ' 聪\\nB:1　Alice　39000 聪';
};
resetBook();
"""
overview_css = """
.lookup-path{color:var(--state);border-left:3px solid var(--state);padding-left:12px}

.lesson-table table{width:100%;font-variant-numeric:tabular-nums}
.lesson-table th,.lesson-table td{padding:7px 12px;line-height:1.4}
.coins-grid table,.field-grid table{min-width:780px}
.coins-grid th,.coins-grid td{padding-block:5px}
.compact-grid table,.wire-grid table{min-width:640px}
.coins-grid :is(th,td):is(:nth-child(1),:nth-child(2)),.input-grid :is(th,td):is(:nth-child(2),:nth-child(3)),.field-grid .key-field td:nth-child(2){color:var(--wire)}
.coins-grid :is(th,td):nth-child(3),.output-grid :is(th,td):nth-child(2),.field-grid tr:nth-child(3) td:nth-child(2){color:var(--gold)}
.coins-grid :is(th,td):nth-child(4),.output-grid :is(th,td):nth-child(3),.field-grid tr:nth-child(4) td:nth-child(2){color:var(--state)}
.coins-grid .spent-row{background:#3b3033}.coins-grid .new-row{background:#283c39}
.spent-ink{color:#efb2ad}.new-ink{color:var(--state)}
.field-grid td:first-child,.wire-grid td:last-child{font-family:monospace}

.state-pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:24px}
.state-pair section{display:grid;grid-template-rows:auto auto 1fr auto 1fr;align-content:start}
.state-pair section div{background:var(--panel);border:1px solid var(--line);padding:12px 18px;font-variant-numeric:tabular-nums}
.state-pair section p{color:var(--state);margin:8px 0}
.slide details summary{cursor:pointer;color:var(--state)}

#page-1 .question:empty{display:none}
.overview-grid,.system-links{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.overview-grid>section{border-top:2px solid var(--state);padding-top:10px}
#page-1 h2{font-size:24px;margin:0 0 8px}
.focus-list{display:grid;grid-template-columns:max-content 1fr;gap:10px 16px;margin:0}
.focus-list dt{color:var(--state);font-weight:600}
.focus-list dd{margin:0;text-wrap:pretty}
.overview-grid p,.system-position p{margin:0}
.overview-grid ol{padding-left:1.45em;margin:8px 0}
.overview-grid li{margin:0}
.payment-path span{white-space:nowrap}.payment-path{display:flex;flex-wrap:wrap;gap:0 .35em;color:var(--state);border-left:3px solid var(--state);padding-left:12px}
.system-position{border-top:1px solid var(--line);padding-top:12px;margin-top:18px}
.system-links{gap:10px;margin:0 0 10px}
.system-links a{border:1px solid var(--line);background:var(--panel);padding:8px 14px;text-decoration:none}
.system-links a:hover{text-decoration:underline}
.system-links b{color:var(--gold)}
@media(max-width:800px){.overview-grid,.system-links{grid-template-columns:1fr;gap:14px}.focus-list{gap:12px}.system-links{gap:6px}}
"""

if __name__ == '__main__':
    build(3, slides, adjacent=2, lesson_title='UTXO 与最小账本',
          extra_css=overview_css + '.mobile-ledger{display:none}.ledger-diagram{display:block;width:100%;max-width:1000px;margin:20px 0}.demo{background:var(--panel);border:1px solid var(--line);padding:20px}.demo button,.demo input{margin:4px}.demo output{color:var(--gold)}@media(max-width:600px){.ledger-diagram{display:none}.mobile-ledger{display:block;padding:16px;border:1px solid var(--line);background:var(--panel)}.mobile-ledger hr{border:0;border-top:1px solid var(--line)}.demo{padding:12px}}',
          extra_js=demo_js)
