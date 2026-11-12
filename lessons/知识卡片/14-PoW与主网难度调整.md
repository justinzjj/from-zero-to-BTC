# 14 · 工作量证明、网络目标与 nBits

工作量证明（Proof of Work，PoW）在 Bitcoin 中要求一个 80 字节区块头的双 SHA-256 哈希按整数解释后小于等于目标 T。nBits 是区块头里对目标的紧凑编码；nonce 是矿工可以改变的一个 4 字节字段。T 越小，随机一次尝试达标的概率越低。

所有节点都能用很少的计算核对一个达标结果；产生结果通常需要大量尝试。每个有效块按其目标贡献可计算的工作量，节点据此比较有效分支。主网按既定周期调整目标，使长期平均出块间隔趋近十分钟。

**目标与累计工作量。** 给定 T，一次均匀哈希命中的概率是 (T + 1) / 2²⁵⁶。节点按目标为每个有效块计入工作量，再沿父块相加。同一目标下，偶然找到更小的哈希不会多得工作量。

**80 字节头的布局。** 按字节偏移依次是版本 [0,4)、父块哈希 [4,36)、Merkle 根 [36,68)、时间 [68,72)、nBits [72,76)、nonce [76,80)。对合法例值 0x1d00ffff，指数为 0x1d，系数为 0xffff，解得 T = 65535 × 256²⁶。节点对序列化头做双 SHA-256，以小端读出结果整数 h，核对 h ≤ T，并核对 nBits 符合父链规定。

**英文术语**　SHA-256（Secure Hash Algorithm 256-bit）。

[复算创世块并推导难度调整](推演-14.md) · [Core v29.0 主网参数](https://github.com/bitcoin/bitcoin/blob/v29.0/src/kernel/chainparams.cpp)

**规范与实现**　[Core v29.0 PoW](https://github.com/bitcoin/bitcoin/blob/v29.0/src/pow.cpp)

## 图解与实作

- [SatoshiBench · 区块头 PoW](https://satoshibench.com/learn/proof-of-work/)　在浏览器中对区块头进行哈希试算。
- [Block Zero · 难度周期](https://blockzerobtc.com/tools/difficulty)　把头中的目标与历史难度曲线对照。
- [BTCVisual · 挖矿实验](https://btcvisual.com/experiments/mining)　用简化目标观察 nonce 搜索。
