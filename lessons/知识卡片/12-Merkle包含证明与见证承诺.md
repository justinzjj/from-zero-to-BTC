# 12 · Merkle 树、树根与包含证明

Merkle 树将一组有序数据的哈希逐层配对，拼接并哈希，最终得到一个根。Bitcoin 的普通交易树以块内交易的 txid 为叶，根写入区块头。包含证明由目标叶的位置和沿途各层的兄弟哈希组成。

一个区块头需要承诺整块的交易次序和内容。持有区块头的人可以用一条短路径核对某笔交易是否被包含。证明的范围限于包含关系；脚本和输入有效性仍需交易与链状态。含见证的区块还通过 coinbase 承诺另一棵见证树。

**简化支付验证（SPV）。** 轻客户端可以保存和核验区块头，用包含证明确认某笔交易被某个头承诺，再观察这条头链的累计工作量。这个判断依赖客户端获得的链和相应的算力假设。

**三片叶子的计算。** 令 D 表示双 SHA-256，a、b、c 表示按块内次序排列的 32 字节交易哈希。末层为奇数时复制 c，先算 p = D(a || b)、q = D(c || c)，再算根 D(p || q)。证明 b 的包含关系只需提供左兄弟 a、右兄弟 q 及方向。哈希函数的输入是字节拼接。

**英文术语**　SHA-256（Secure Hash Algorithm 256-bit）、SPV（Simplified Payment Verification，简化支付验证）、txid（transaction identifier，交易标识）。

[用主网高度 170 的数据重建树根](推演-12.md) · [高度 170 的节点数据](https://www.thebitcointm.com/block/170)

**规范与实现**　[Core v29.0 Merkle 实现](https://github.com/bitcoin/bitcoin/blob/v29.0/src/consensus/merkle.cpp) · [BIP141 · Commitment structure](https://bips.dev/141/#commitment-structure)

## 图解与实作

- [SatoshiBench · 交互 Merkle 树](https://satoshibench.com/learn/merkle-tree/)　载入区块，选一笔交易，沿兄弟哈希路径追到区块头的根。
- [Decentralized Thoughts · Merkle 包含证明](https://decentralizedthoughts.github.io/2020-12-22-what-is-a-merkle-tree/)　从成员证明图解读懂路径需要哪些哈希。
