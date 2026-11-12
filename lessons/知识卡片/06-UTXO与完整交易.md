# 06 · UTXO 记账模型：输出、输入与未花费集合

**UTXO（Unspent Transaction Output，未花费交易输出）**是一笔已有交易创建、截至所观察的链尖仍未被消费的输出。它有一个可被下一笔交易引用的位置、一笔整数金额，以及一段规定花费条件的脚本。Bitcoin Core v29.0 用下面两个对象表达这项记录：用 **COutPoint** 查哪一项，用 **Coin** 保存查到的内容。

| 所属对象 | Core 字段与类型 | 含义 |
|---|---|---|
| 查找键 COutPoint | `hash: Txid` | 创建该输出的交易标识（transaction identifier，txid），32 字节 |
| 查找键 COutPoint | `n: uint32_t` | 该交易输出数组中从 0 开始的下标 |
| 记录 Coin → out: CTxOut | `out.nValue: CAmount` | 有符号 64 位整数，以聪为单位；有效输出的金额须在共识允许范围内 |
| 记录 Coin → out: CTxOut | `out.scriptPubKey: CScript` | 可变长脚本字节，规定花费这项钱要满足的条件 |
| 记录 Coin | `fCoinBase: unsigned int（1 位）` | 创建它的交易是否为 coinbase，花费时用于检查成熟期 |
| 记录 Coin | `nHeight: uint32_t（31 位）` | 创建输出的区块高度，也用于成熟期和相对时间锁检查 |

前两个字段来自引用位置。中间两个字段来自原交易输出。最后两个字段由节点处理所在区块时补上。后来花费它的交易只需在输入的 `prevout` 写出同一对键，节点即可取得金额和脚本进行验证。[交易类型定义](https://github.com/bitcoin/bitcoin/blob/v29.0/src/primitives/transaction.h) · [Coin 定义](https://github.com/bitcoin/bitcoin/blob/v29.0/src/coins.h)

### 读一条真实记录：主网高度 170 的第 0 号付款输出

下面按 Core 的字段重建**刚接入高度 170 时**的历史状态。它来自一笔 10 BTC 的主网付款，与 Alice 的 60,000 聪书款是两个样例。交易标识按区块浏览器的显示顺序书写。

```text
COutPoint
  hash = f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16
  n    = 0
Coin
  out.nValue       = 1000000000
  out.scriptPubKey = 4104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac
  fCoinBase        = 0
  nHeight          = 170
```

在原交易中，这个输出依次写作金额 `00 ca 9a 3b 00 00 00 00`、脚本长度 `43`、上面的 67 字节脚本。金额按小端读为十亿聪。脚本开头的 `41` 指示压入 65 字节公钥，末尾 `ac` 是 OP_CHECKSIG（检查签名）。这种条件称为 **P2PK（Pay to Public Key，支付到公钥）**。换到书款案例，B:0 的金额是 60,000 聪，脚本是 22 字节的 P2WPKH（Pay to Witness Public Key Hash），Core 用同样的字段保存它。[高度 170 付款的原始交易](https://learnmeabitcoin.com/explorer/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16)

### 节点怎样保存和更新这条记录？

内存里可以按上述对象理解。写入 chainstate 的 LevelDB 时，Core 将键编码为前缀 `0x43`、序列化交易标识、按 Core VARINT 编码的输出编号。值先编码 `2 × nHeight + fCoinBase`（此例为 340），再写压缩的金额与脚本。原交易的输出长度使用 CompactSize；数据库键值采用自己的编码。它们表达相同的输出，字节布局不同。[CoinEntry 数据库键](https://github.com/bitcoin/bitcoin/blob/v29.0/src/txdb.cpp) · [输出压缩格式](https://github.com/bitcoin/bitcoin/blob/v29.0/src/compressor.h)

普通交易接块时，节点在父链状态中按每个输入的 prevout 查找 Coin，核对金额、脚本及花费资格，在工作视图中消费旧 Coin，再按新交易的 txid 和各输出下标加入可进入 UTXO 集的新 Coin。消费会让旧键从可用集合中消失；历史交易本身仍然存在。

**余额怎样表示。** 钱包找出脚本属于自己跟踪范围的输出，再按花费状态和确认类别汇总金额。余额是查询结果。假设 Alice 只有一项 100,000 聪的输出，要付 60,000 聪，她可以消费整项，创建 60,000 聪书款与 39,000 聪找零，差额 1,000 聪为手续费。

**英文术语**　BIP（Bitcoin Improvement Proposal，比特币改进提案）。

[读取一笔完整交易并复算字节](推演-06.md) · [BIP143 Native P2WPKH](https://bips.dev/143/#native-p2wpkh)

## 图解与实作

- [Block Zero · UTXO Visualizer](https://blockzerobtc.com/tools/utxo-visualizer)　按 txid 载入交易，点输入追到旧输出，点已花费的输出查看后续花费。
- [mempool.space · 高度 170 的付款](https://mempool.space/zh/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16)　对照真实输入 50 BTC 与两个输出 10 BTC、40 BTC。
- [廖雪峰 · UTXO 模型](https://liaoxuefeng.com/books/blockchain/bitcoin/utxo/index.html)　用中文例子对照旧输出、找零和可用余额。
- [Building Blockchain in Go · Transactions 2](https://jeiwan.net/posts/building-blockchain-in-go-part-6/)　对照教学链 UTXO 集的查找和更新，实现细节以 Core 版卡片为准。
