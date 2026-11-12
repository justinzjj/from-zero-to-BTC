# Bitcoin 家教知识卡 · 从部署图进入

配合[部署页](../btc-deployment.html)、[钱包页](../btc-wallet.html)、[全节点页](../btc-full-node.html)、[矿机页](../btc-miner.html)使用。部署页有两个视角：「完整流程 · Bob 竞争出块」共 12 步，「展开矿池与矿机」共 10 步。查位置时先看视角，再找步骤名称。

概念卡先说明术语指什么、它解决什么问题。需要带学生演算时，点卡末的配套推演。关于选币、冲突替换、同时出块和重组的讨论可从对应问题直接进入。

## 本次预讲的 11 条标注

各项都已整理成卡，课堂讨论待点名。第 10 条的原词仍待确认。

| 预讲标注 | 对应卡片 | HTML 位置 | 适合做成 |
|---|---|---|---|
| 1. 聪和 BTC | [19 一聪是一亿分之一 BTC](19-聪与BTC.md) | 报价 | 金额换算题 |
| 2. 钱包、全节点的职责 | [20 谁能签名，谁独立验证](20-钱包与全节点.md) | 构造、签名并提交 B → 首次确认 | 角色对照 |
| 3. 激励政策 | [21 补贴、手续费与池内记工](21-挖矿激励.md) | 填块体与奖励 | 奖励上限算例 |
| 4. P2P 算法 | [10 邻居怎样通告、请求和转发](10-P2P邻居与请求调度.md) | 中继 B | 分角色传消息 |
| 5. 私钥到公钥、地址 | [02 私钥乘基点](02-私钥与压缩公钥.md) · [03 HD 派生](03-HD钱包与扩展密钥.md) · [04 收款地址](04-从地址到收款脚本.md) | 报价 | 公钥与地址复算 |
| 6. UTXO「账户结构」 | [06 按 outpoint 查旧输出](06-UTXO与完整交易.md) · [20 钱包怎样显示余额](20-钱包与全节点.md) | 选 U → 接入 K | UTXO 前后表 |
| 7. P2WPKH、BIP134、SIGNAL ALL | [05 花费条件](05-P2WPKH与见证栈.md) · [08 BIP143 与 SIGHASH_ALL](08-BIP143签名摘要.md) · [09 ECDSA](09-ECDSA签名与见证装配.md) | 签名并装入见证 | 脚本执行与摘要复算 |
| 8. witness 是数据结构吗 | [05a 逐输入的字节串列表](05a-见证的数据结构.md) | 交易 B（含见证） | 拆见证的两项 |
| 9. 一笔交易的完整结构 | [06 字段、长度和完整官方样例](推演-06.md) | 构造 B → 交易 B（含见证） | 逐字段解码 |
| 10. 「b 竖块」→ 可能是「B 出块」 | [15a Bob 竞争出块，交易 B 被打进 K](15a-Bob出块.md) | 完整流程 ⑤–⑫ | 指图复述 |
| 11. 多人同时命中、传播先后 | [16 累计工作量与重组](16-同时出块与分支选择.md) · [17 节点和钱包状态](17-链状态与本地记录.md) | 传播并验证 K → 全节点页验块与重组 | 双节点分叉推演 |

## 钱包页预讲标注

| 讲到哪里 | 单独展开的知识点 | 建议归课 |
|---|---|---|
| Bob 收款 · 生成地址 | [助记词、密钥树和收款地址一起走一遍](03-HD钱包与扩展密钥.md) | 第一讲 |
| Alice 付款 · 同步旧输出，Bob 收款 · B 入池 | [输出脚本与钱包的归属识别](05-P2WPKH与见证栈.md) | 第二讲 |
| Alice 付款 · 组装未签名 B | [B:1 的找零脚本](04-从地址到收款脚本.md) | 第一讲 |
| Alice 付款 · 计算摘要与见证 | [BIP143 签哪些字段](08-BIP143签名摘要.md) · [私钥签名与公钥验签](09-ECDSA签名与见证装配.md) · [输入携带的两项见证](05a-见证的数据结构.md) | 第二讲 |
| Bob 收款 · 入池和采用含 B 的块 | [UTXO 的记录字段与余额求和](06-UTXO与完整交易.md) | 第二讲 |
| Bob 收款 · 断开旧块，采用含 C 的分支 | [撤下确认与重新判定冲突](17-链状态与本地记录.md) | 第四讲 |

## 全节点页预讲标注

| 课件位置 | 已补充的知识点 | 建议归课 |
|---|---|---|
| Bob 如何确认收款 · ①邻居通告、②用旧币验证 | 已知通告、缺父暂存、拒绝、接纳与直接验块；逐项核对格式、金额、时间、脚本、签名和重复花费 | 第二讲 |
| 同一流程 · ③按 outpoint 查冲突 | 标准性、粉尘、重量、最低费率、动态门槛；C 与 B 如何争用 U，何时登记占用 | 第二讲 |
| [独立 UTXO 页](../btc-utxo.html) | 查键和值、认归属、算余额、判双花；切换入池、接块、断块与新链五个状态 | 第二讲 |
| 矿池或 CPU 流程 · 从本地池挑选 | sat/vB 与祖先包、父先子后、剩余容量、更新候选与落选去向 | 第三讲 |
| 命中并提交、验块与重组 | 难度目标、累计工作量与有效分支选择 | 第三、四讲 |
| Bob 收块 · 收到 K → 执行 → 采用 | 检查头和块体、逐笔执行、提交 UTXO 和索引、清池、通知钱包与重组回滚 | 第三、四讲 |

## 原有 18 个专题与新增的 3 个专题

建议归课沿用工作区八讲大纲。第一讲跟着书款走，第二讲执行交易，第三讲从交易到区块与工作量，第四讲改选历史，第五讲理解规则升级。这里标的是建议重点展开的课节；首页即可先作简答。

| 编号与知识点 | 建议归课 | 跨页对应位置 |
|---|---|---|
| [01 哈希、原始字节、字节序、txid 与 wtxid](01-哈希与交易标识.md) | 第2讲 | 钱包⑦、全节点接收 |
| [02 secp256k1、私钥与压缩公钥](02-私钥与压缩公钥.md) | 第1讲 | 钱包②、部署报价 |
| [03 HD 钱包、链码与普通／硬化派生](03-HD钱包与扩展密钥.md) | 第1讲 | 钱包②、Bob 收款 |
| [04 Bech32 地址、见证程序与收款脚本](04-从地址到收款脚本.md) | 第1讲 | 钱包③⑤、部署报价 |
| [05 P2WPKH 的花费与脚本执行](05-P2WPKH与见证栈.md) | 第2讲 | 钱包⑥、全节点脚本检查 |
| [06 UTXO、outpoint、CompactSize 与交易序列化](06-UTXO与完整交易.md) | 第2讲 | 钱包⑤、全节点 UTXO |
| [07 选币、找零、重量、费率与 BnB](07-选币找零与费率.md) | 第1讲 | 钱包④⑤ |
| [08 BIP143 签名摘要与 SIGHASH_ALL](08-BIP143签名摘要.md) | 第2讲 | 钱包⑥、部署签名 |
| [09 ECDSA、DER 与签名装配](09-ECDSA签名与见证装配.md) | 第2讲 | 钱包⑥、全节点验签 |
| [10 P2P 通告、请求调度与交易传播](10-P2P邻居与请求调度.md) | 第1讲 | 部署中继、全节点 P2P |
| [11 内存池接纳、冲突替换与清理](11-内存池冲突与替换.md) | 第2讲 | 全节点入池、接块与重组 |
| [12 Merkle 树、包含证明、SPV 与见证承诺](12-Merkle包含证明与见证承诺.md) | 第3讲 | 矿机模板、全节点验块 |
| [13 候选块、补贴、成熟期与区块资源限制](13-候选块与区块奖励.md) | 第3讲 | 矿机模板、全节点验块 |
| [14 PoW、80 字节头、nBits 与难度调整](14-PoW与主网难度调整.md) | 第3讲 | 矿机控制器与 ASIC、全节点验头 |
| [15 矿池模板、Stratum、ASIC、份额与提交](15-矿池作业与份额.md) | 第3讲 | 矿机两种结果、部署回报 |
| [16 分支选择、累计工作量与重组](16-同时出块与分支选择.md) | 第4讲 | 全节点验块与重组、部署首次确认 |
| [17 初始同步、链状态、撤销记录与裁剪](17-链状态与本地记录.md) | 第4讲 | 全节点活动链、钱包通知 |
| [18 时间、锁定条件、软分叉与激活](18-时间锁与规则激活.md) | 第5讲 | 全节点共识检查、钱包交易字段 |
| [19 聪与 BTC](19-聪与BTC.md) | 第1讲 | 部署报价、钱包金额 |
| [20 钱包与全节点的核心职责](20-钱包与全节点.md) | 第1讲 | 部署设备、钱包与全节点页 |
| [21 挖矿的经济激励](21-挖矿激励.md) | 第1讲 | 部署奖励、矿机复核 |

见证结构另有 [05a 独立追问卡](05a-见证的数据结构.md)；Bob 出块的角色切换见 [15a 口述核对卡](15a-Bob出块.md)。两张都属于已有专题。原有编号 01–18 保留，19–21 为此次新增。

## 样例与取材

- 课堂 B 花 U 的 100,000 聪，B:0 给 Bob 60,000，B:1 找零 39,000，差额 1,000。C 与 B 竞争同一个 U，K 是拟纳入 B 的候选块。有关收款条件和输出字节可查[本地交易总览](../0-BTC%20overview.md)。
- 规范样例有各自的私钥、公钥、输入、金额和预期值。卡内写明切换数据的地方。把 BIP143 的签名拿来验算时，须使用该向量自己的交易及前序金额。
- 原有[资源目录](../../resources/BTC学习资源.md)和[源码导读](../BTC交易源码导读.md)适合继续查阅。各卡注明参考资料的课堂动作和已核实的许可条件；仅标注投影或链接的外部材料不计入已获许可的离线素材。

## 教师备课参考与许可记录

### 07-选币找零与费率

先投影[本地钱包清单](../钱包模块算法与数据结构清单.md)的④⑤两行。用纸笔对照深度优先搜索的剪枝条件；源码按 MIT 许可，收入离线包时附原版权和许可文本。[Core v29.0 选币实现](https://github.com/bitcoin/bitcoin/blob/v29.0/src/wallet/coinselection.cpp#L47-L79) · [Core 许可](https://github.com/bitcoin/bitcoin/blob/v29.0/COPYING)

重量公式可以投影并复算，BIP 正文标为公有领域（PD）。[BIP141 · Block size](https://bips.dev/141/#block-size)

### 11-内存池冲突与替换

先投影[本地源码导读](../BTC交易源码导读.md)中两张表的课堂动作，分别写「本地池」和「已确认 UTXO」。再打开下列两份 Core v29.0 原始材料；均可按项目 MIT 许可随离线课件附原版权和许可文本。

- 复算增量费用，并指出仅增加绝对费用还缺哪些条件。[v29.0 替换策略](https://github.com/bitcoin/bitcoin/blob/v29.0/doc/policy/mempool-replacements.md)
- 投影 removeForBlock 和 removeConflicts，追踪确认和冲突引起的两次不同删除。[v29.0 内存池实现](https://github.com/bitcoin/bitcoin/blob/v29.0/src/txmempool.cpp#L600-L636)

### 13-候选块与区块奖励

- 投影现有讲义第 5 节，让学生圈出 B 在奖励上限中贡献的那一项。[一笔 BTC 付款的一生](../0-BTC%20overview.md)
- 查找并投影 `GetBlockSubsidy` 及 `bad-cb-amount`，对照补贴计算和超领拒绝两处实现。[Bitcoin Core v29.0 验证代码](https://github.com/bitcoin/bitcoin/blob/v29.0/src/validation.cpp)
- 打开头文件并核对三个上限或门槛。以上 Core 文件为 MIT，离线转载源码须保留版权及许可声明。[Core v29.0 共识常量](https://github.com/bitcoin/bitcoin/blob/v29.0/src/consensus/consensus.h)

### 15-矿池作业与份额

- 投影本地两条动画，在同一个第 8 步对照池的记工记录、池方链尖和 Bob 钱包。[矿机页](../btc-miner.html)
- 投影模板响应，找出交易列表、父块哈希和可领取金额，说明矿池怎样从节点取材料。已核实 BSD-2-Clause，可按条款保留版权、许可条件及免责条款收入离线包。[BIP 22 模板接口](https://bips.dev/22/)
- 对读 V1 的三条消息 `mining.subscribe`、`mining.notify`、`mining.submit`，让学生在五个提交参数里找作业号。此处仅链接在线投影，未核实离线转载条件。[Bitcoin Wiki 的 V1 消息说明](https://en.bitcoin.it/wiki/Stratum_mining_protocol)

### 15a-Bob出块

投影[本地部署页](../btc-deployment.html)，先选「完整流程 · Bob 竞争出块」，让学生用三个不同的词读出「Bob 把 B 打入 K」；再切「展开矿池与矿机」辨认实际职责。下一次只需核对预讲原句里 B 指 Bob 还是交易 B，确认后可将此条移出待问。

### 16-同时出块与分支选择

- 投影真实主网分叉树，找同高且同父的两个块，再查哪一个有主链后继。数据反映收集者能观察到的记录。外站图表未核实离线转载许可。[Bitcoin Stale Block Dataset](https://bitcoin-data.github.io/stale-blocks/tree/)
- 复算单块工作量，再找 `LastCommonAncestor` 里高度对齐与回退的步骤。[Core v29.0 工作量和共同祖先](https://github.com/bitcoin/bitcoin/blob/v29.0/src/chain.cpp#L119)
- 投影 `CBlockIndexWorkComparator` 与分配本地序号的说明。上述 Core 源码采用 MIT，可附版权及许可声明离线摘录。[Core v29.0 候选排序](https://github.com/bitcoin/bitcoin/blob/v29.0/src/node/blockstorage.cpp#L145)

### 17-链状态与本地记录

- 投影本地「验块与重组」，让学生在断 K 时口述「旧块体贡献哪些字段，撤销数据补齐哪些字段」。[全节点页](../btc-full-node.html)
- 按文件名对照磁盘目录，标出哪一种记录能恢复旧 Coin。[Core v29.0 数据文件表](https://github.com/bitcoin/bitcoin/blob/v29.0/doc/files.md)
- 投影 `DisconnectBlock` 的逆向循环及撤销读取。Core 代码及上述文档为 MIT，可随版权及许可声明收入离线包。[Core v29.0 断块实现](https://github.com/bitcoin/bitcoin/blob/v29.0/src/validation.cpp#L2108)

### 21-挖矿激励

投影[白皮书第 6 节 Incentive](https://bitcoin.org/bitcoin.pdf#page=4)，让学生圈出补贴和手续费两个来源（原文仅作链接，未核实离线转载许可）。再投影 [Bitcoin Core v29.0 的奖励上限检查](https://github.com/bitcoin/bitcoin/blob/v29.0/src/validation.cpp#L2495-L2499)，代入上述数字，观察大于号的方向。源码按 [MIT 许可](https://github.com/bitcoin/bitcoin/blob/v29.0/COPYING)保留声明可离线引用。

### 推演-01

投影钱包模块⑦，先指出广播的数据，再用卡 06 的完整向量复算两种标识。[钱包页](../btc-wallet.html) · [卡 06 的逐字段字节](推演-06.md)  
投影规范中的 Transaction ID 两条公式，尤其留意不带见证时的情况。BIP141 标注公有领域，可收入离线课件。[BIP141](https://bips.dev/141/#transaction-id)

### 推演-02

先投影课件中从私钥到脚本的一段，再运行本卡的倍点算式。[仓库总览，第 1 步](../0-BTC%20overview.md)  
翻到 §2.4.1 对照 secp256k1 的 p、G、n。原 PDF 扉页允许复制，要求所有提及或引用该文档的材料以 “Standards for Efficient Cryptography 2 (SEC 2)” 标明文档。[Standards for Efficient Cryptography 2 (SEC 2)](https://www.secg.org/sec2-v2.pdf)

### 推演-03

投影模块②的描述符与派生下标，操作时区分树位置和地址字符串。[本地钱包模块清单](../钱包模块算法与数据结构清单.md)  
用 Test vector 1 对照路径和扩展密钥。规范标明 BSD-2-Clause，离线收录时保留版权、许可条件与免责声明。[BIP32](https://bips.dev/32/#test-vector-1)

### 推演-04

投影现成的 B:0，遮住公钥哈希，请学生从地址复原。[本地案例](../0-BTC%20overview.md)  
用规范的 Segwit address format 和参考实现复算地址；再对照版本分流。两份 BIP 均标注 BSD-2-Clause，离线收录须保留版权、条款与免责声明。[BIP173](https://bips.dev/173/#segwit-address-format) · [BIP350](https://bips.dev/350/#addresses-for-segregated-witness-outputs)

### 推演-05

投影模块⑥与全节点的交易检查，再用两张纸代表两项见证，逐行执行上表。[钱包页](../btc-wallet.html)  
讲清 P2WPKH 两项栈要求，随后看官方 Native P2WPKH 已签交易里的空列表、两项列表。两份 BIP 均标注公有领域，可离线收录向量。[BIP141 见证程序](https://bips.dev/141/#witness-program) · [BIP143 官方向量](https://bips.dev/143/#native-p2wpkh)

### 推演-05a

投影[钱包模块⑥](../btc-wallet.html)，让学生分别指给你看谁组装、谁验证；对照 [BIP141 的 Transaction ID 与 Witness program 两节](https://bips.dev/141/#transaction-id)读数量与长度，正文标为公有领域，可存入离线课件。投影 [Bitcoin Core v29.0 的 CScriptWitness 定义](https://github.com/bitcoin/bitcoin/blob/v29.0/src/script/script.h#L541-L545)，让学生解释外层与内层两个 vector。源码离线摘录按项目 MIT 许可保留声明。

### 推演-06

对着钱包模块⑤投影输入和输出，再观察 Bob 钱包如何用脚本索引认出 B:0。[本地钱包页](../btc-wallet.html)  
逐字段复算上面的向量，规范标注公有领域，可收入离线课件。[BIP143 Native P2WPKH](https://bips.dev/143/#native-p2wpkh)  
在 Bitcoin Core v29.0 的 `SerializeTransaction` 中依次找 vin、vout、scriptWitness、nLockTime，对照条件分支读标准布局。[固定版本交易结构](https://github.com/bitcoin/bitcoin/blob/v29.0/src/primitives/transaction.h)

### 推演-08

先在[本地钱包清单](../钱包模块算法与数据结构清单.md)找到⑥。投影及复算官方向量，正文标为公有领域，可纳入离线课件。[BIP143 · Native P2WPKH](https://bips.dev/143/#native-p2wpkh)

核对口误时只需投影 BIP134 标题和状态页。此卡仅保留链接，未核实其离线转载许可。[BIP134 · Flexible Transactions](https://bips.dev/134/)

### 推演-09

先投影[本地钱包清单](../钱包模块算法与数据结构清单.md)第⑥行。规范里的完整字节可投影、拆分或离线复算，BIP143 正文标为 PD。[BIP143 · Native P2WPKH](https://bips.dev/143/#native-p2wpkh)

投影严格 DER 编码的字段图，给学生圈出 DER 之外的最后一个字节。BIP66 正文标为 BSD-2-Clause，离线引用保留原版权、条款与免责声明。[BIP66 · DER encoding reference](https://bips.dev/66/#der-encoding-reference)

### 推演-10

投影全节点页的「TxRequestTracker · 交易索取调度」卡，让两名学生当邻居，同时报同一标识，第三名学生只向其中一人索取交易。[本地全节点课件](../btc-full-node.html)

把投影切到 AddTxAnnouncement 与 GetRequestsToSend，学生在源码中找出“已拥有”和“尚在途”的判断。源码标 MIT，离线收入需附原版权和许可文本。[Core v29.0 下载调度](https://github.com/bitcoin/bitcoin/blob/v29.0/src/node/txdownloadman_impl.cpp#L164-L215)

投影规范的协商步骤，圈出 wtxidrelay 与 MSG_WTX。BIP339 标为 BSD-2-Clause，离线引用需保留原版权、条款和免责声明。[BIP339](https://bips.dev/339/)

### 推演-12

先查[仓库资源表中的 Merkle 树互动与历史交易](../../resources/BTC学习资源.md)。在线投影高度 170 的交易顺序，对照上面的离线算式；区块浏览器只作外链，未核实网页离线转载许可。[高度 170 的节点数据](https://www.thebitcointm.com/block/170)

对照计算过程找出两棵树的叶子，Core 源码按 MIT 许可，离线附原版权和许可文本。规范正文标为 PD，可离线使用。[Core v29.0 Merkle 实现](https://github.com/bitcoin/bitcoin/blob/v29.0/src/consensus/merkle.cpp) · [BIP141 · Commitment structure](https://bips.dev/141/#commitment-structure)

### 推演-14

- 投影「普通份额」和「命中网络目标」两个分支，指出同一作业的 nonce 在何处进入区块头。[矿机课件](../btc-miner.html)
- 复算前，找到主网 `CreateGenesisBlock(1231006505, ...)` 附近的根和期望哈希。[Core v29.0 主网参数](https://github.com/bitcoin/bitcoin/blob/v29.0/src/kernel/chainparams.cpp)
- 投影 `GetNextWorkRequired`、`CalculateNextWorkRequired` 的周期与边界。两份 Core 源码采用 MIT，离线摘录请附版权和许可声明。[Core v29.0 PoW](https://github.com/bitcoin/bitcoin/blob/v29.0/src/pow.cpp)

### 推演-18

- 投影序号字段图并复算 3 个块或 3 × 512 秒的编码。本卡仅链接 BIP 68 在线版本，未核实离线转载许可。[BIP 68 相对锁](https://bips.dev/68/)
- 投影中位数的计算，给出 11 个数让学生排出第六个。文末关联 CLTV、CSV 和 BIP 68。此 BIP 正文声明为公有领域，可收入离线课件。[BIP 113 的 MTP](https://bips.dev/113/)
- 投影 States 一节，辨认 LOCKED_IN 与 ACTIVE。正文声明为公有领域，可收入离线课件。[BIP 9 版本位激活](https://bips.dev/9/)

### 推演-19

投影[本地部署页](../btc-deployment.html)的报价，再用上表心算。对照 [Bitcoin Core v29.0 的金额常量](https://github.com/bitcoin/bitcoin/blob/v29.0/src/consensus/amount.h#L9-L13)找出 COIN 和 CAmount；该源码适用 [MIT 许可](https://github.com/bitcoin/bitcoin/blob/v29.0/COPYING)，收入离线课件时保留版权及许可声明。

### 推演-20

投影[本地总览中的两幅组件图](../0-BTC%20overview.md)，在两图各找一次「谁保存 U、谁记下书款」。打开 [Bitcoin 开发指南的 Wallet Programs](https://developer.bitcoin.org/devguide/wallets.html#wallet-programs)，让学生指出收款、签名和联网可以分别由谁负责。外部指南供投影、链接，未核实插图的离线转载许可。
