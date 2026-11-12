# 05 · P2WPKH 与脚本执行

Bitcoin Script 用操作码和数据表达并检验花费条件。P2WPKH（Pay to Witness Public Key Hash）是一种见证版本 0 的输出类型，它在输出脚本中给出一个 20 字节公钥哈希。花费原生 P2WPKH 时，输入的 scriptSig 为空，见证携带签名和公钥。

这里缓存的是输出脚本（scriptPubKey），即交易输出中规定将来怎样花这笔钱的字节。Bob 的钱包用 B:0 的完整脚本查索引，命中就能识别书款；将来花费时，再从对应派生位置查找密钥或签名器。以后花费时，节点核对公钥哈希并验证签名，由此判断这次花费是否得到授权。识别脚本和实际签署花费可以由不同设备负责。

**从栈到判定。** 节点从旧输出读出 `00 14 <20字节哈希>`，要求输入的见证恰有签名和公钥两项。执行相当于 `OP_DUP OP_HASH160 <20字节哈希> OP_EQUALVERIFY OP_CHECKSIG` 的检查：复制栈顶公钥、求其哈希、与旧输出承诺比较，最后用公钥检查针对本次花费的签名。任何必需检查失败都无法花费该输出。

**英文术语**　BIP（Bitcoin Improvement Proposal，比特币改进提案）。

[逐步执行脚本并检查归属](推演-05.md) · [BIP141 见证程序](https://bips.dev/141/#witness-program)

**规范与实现**　[BIP143 官方向量](https://bips.dev/143/#native-p2wpkh)

## 图解与实作

- [Block Zero · Script Playground](https://blockzerobtc.com/tools/script-playground)　逐条执行 P2PKH 模板，观察公钥哈希比较和验签时的栈；原生 P2WPKH 的初始数据来自见证。
- [Mastering Bitcoin · 授权脚本](https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch07_authorization-authentication.adoc)　对照输出条件和花费时提供的授权数据。
