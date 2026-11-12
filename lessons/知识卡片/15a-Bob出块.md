# 15a · Bob 出块与书款确认

Bob 同时经营挖矿设施和书店。B 是支付书款的交易，K 是包含 B 的候选块。挖矿设施找到合格区块头后组装并提交 K，收款侧节点独立验证并采用 K。

| 完整流程 | 数据与接收方 |
|---|---|
| 选父块、填块体、算根 | Bob 在出块方的角色选定父块 P 和交易 B，把 coinbase 放在首位；控制器根据作业材料构造候选头。此时已有候选块，Bob 的收款还未确认。 |
| 搜索、命中 | ASIC 试 nonce；本次头哈希不大于目标，控制器上报参数，池方重建并复算。命中说明头的工作量证明达标。 |
| 组装并提交 K | 作业协调取回完整交易，配上命中头提交给出块侧节点。该节点验证并接入有效的 K。 |
| 收款侧验块、钱包确认 | Bob 以书商身份使用的全节点独立验 K、接入自己的活动链并通知钱包，书款在链尖获得 1 次确认。 |

无论哪个矿工找到区块，Bob 的书款都在他的节点采用含 B 的块时获得确认。出块奖励按该块的 coinbase 支付。

**英文术语**　ASIC（Application-Specific Integrated Circuit，专用集成电路）。

## 图解与实作

- [Visualize Bitcoin · 3D 网络场景](https://visualizebitcoin.org/world)　在模拟环境中跟踪矿工、交易和区块的关系。
- [Bitcoin Designed · 交易生命周期图](https://www.bitcoindesigned.com/infographics/the-bitcoin-transaction-life-cycle/)　沿付款流程图区分出块与收款确认。
