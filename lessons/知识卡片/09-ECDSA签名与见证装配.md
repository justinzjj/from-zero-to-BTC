# 09 · ECDSA 签名、验证与 DER 编码

ECDSA 是一种公钥数字签名算法。签名端用私钥、消息摘要和一次性标量 k 得到两个整数 r 和 s。验证端用公钥、同一摘要以及 r、s 检查签名。DER 规定这对整数如何编码成字节。

付款人需要授权一笔指定的花费，同时让任意节点独立核验。P2WPKH 将 DER 签名附上签名模式字节，并把它与公钥装入见证；私钥只在签名端使用。

**签名与验签的计算。** 设基点为 G、阶为 n，私钥 d 的公钥为 Q = dG，摘要解释为整数 z。签名端计算 R = kG，取 r = x(R) mod n，再求 s = k⁻¹(z + rd) mod n，r 或 s 为零须重选 k。验签端先检查 r、s 的范围，再算 w = s⁻¹ mod n 和点 X = (zw mod n)G + (rw mod n)Q。X 不是无穷远点且 x(X) mod n = r 时通过。

**英文术语**　P2WPKH（Pay to Witness Public Key Hash，支付到见证公钥哈希）、ECDSA（Elliptic Curve Digital Signature Algorithm，椭圆曲线数字签名算法）、DER（Distinguished Encoding Rules，可辨别编码规则）、BIP（Bitcoin Improvement Proposal，比特币改进提案）。

[验签并拆读官方见证样例](推演-09.md) · [BIP143 · Native P2WPKH](https://bips.dev/143/#native-p2wpkh)

**规范与实现**　[BIP66 · DER encoding reference](https://bips.dev/66/#der-encoding-reference)

## 图解与实作

- [Block Zero · Signatures](https://blockzerobtc.com/tools/sha256)　用演示密钥签署消息并核验；消息签名演示和 BIP143 交易摘要使用不同的消息构造方式。
- [廖雪峰 · 数字签名](https://liaoxuefeng.com/books/blockchain/bitcoin/p2p/signature/index.html)　从签名者和验证者两端看私钥、公钥与消息。
- [Karpathy · Python 签名实现](https://karpathy.github.io/2021/06/21/blockchain/)　阅读签名数对与 DER 编码代码。
- [Learn Me A Bitcoin · ECDSA](https://learnmeabitcoin.com/technical/cryptography/elliptic-curve/ecdsa/)　对照椭圆曲线点运算、签名和验证公式。
