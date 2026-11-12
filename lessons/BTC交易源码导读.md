# Alice 给 Bob 付款：七步读懂真实源码

配合[交易生命周期讲义](0-BTC%20overview.md)阅读。我们始终跟踪同一个旧输出 U：Alice 用它的 100,000 聪支付书款。交易 B 产生 Bob 的 60,000 聪和 Alice 的 39,000 聪，余下 1,000 聪是手续费。竞争交易 C 也花 U。本例假设 U 已确认、可立即花费，输入和两个输出均采用原生 P2WPKH。

C++ 看 Bitcoin Core v29.0。Go 看 btcd v0.24.2；选币和构造付款另读独立的钱包项目 btcwallet v0.16.10。链接固定到具体提交和行号。这些版本用于对照协议行为，各钱包的输出顺序、选币结果和各节点的入池策略可以不同。下面的代码块摘自对应源码，是阅读片段，需要所在函数的上下文。

## 1. 从 Bob 的地址得到收款脚本

**读 Core。** Bob 的钱包已有一个公钥，其 20 字节公钥哈希可表示为 `WitnessV0KeyHash`。地址编码分支把版本 0 和哈希编成 Bech32 字符串。Alice 构造输出时，地址解码得到相同类型的目的地，`GetScriptForDestination` 分派到这个分支。下面是构造脚本的一行。[Core · 地址编码](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/key_io.cpp#L44) · [Core · 输出脚本](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/addresstype.cpp#L131)

```cpp
return CScript() << OP_0 << ToByteVector(id);
```

**读 Go。** `NewAddressWitnessPubKeyHash` 接受的是已经算好的见证程序；到 `PayToAddrScript`，按地址类型进入 `payToWitnessPubKeyHashScript`。两个实现都应产出 `00 14 <Bob 的 20 字节哈希>`：版本 0，压入 20 字节，随后是哈希。密钥乘法发生在产生公钥时，收款脚本组装只处理公开数据。[Go · 地址构造](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/btcutil/address.go#L599) · [Go · 按地址类型生成脚本](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/txscript/standard.go#L861)

**课堂保留。** 让学生拿地址解出的哈希与 B 的第 0 个输出逐字节对照。Bob 此时无需签名，也无需在线；以后花 B:0 时才需要满足这个条件。

## 2. 从钱包的可用输出构造 B

**读 Core。** `CreateTransactionInternal` 为付款和费用准备目标值，请 `SelectCoins` 从可用输出中选择输入，再构造收款与找零。分支限界搜索 `SelectCoinsBnB` 是可选策略之一：在候选组合里搜索落入目标范围的解，提前剪掉凑不够或超过范围的分支。观察输入数量很重要，因为额外输入本身也会增加费用。[Core · 构造付款并调用选币](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/wallet/spend.cpp#L1160) · [Core · 分支限界搜索](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/wallet/coinselection.cpp#L93)

**读 Go。** btcwallet 的 `NewUnsignedTransaction` 把“如何挑 UTXO”交给 `fetchInputs`；先按暂估手续费取输入，再根据实际输入脚本类型重估虚拟大小。若输入不足以覆盖重估的费用，就提高目标并重试。有经济意义的找零才加入输出。最值得圈出的是这行减法。[Go · 选输入、重估费用、添加找零](https://github.com/btcsuite/btcwallet/blob/7be2dd11052231828844bca0333591e3f7182c69/wallet/txauthor/author.go#L93)

```go
changeAmount := inputAmount - targetAmount - maxRequiredFee
```

**课堂保留。** 固定 U 与 1,000 聪手续费后，直接算出找零 39,000 聪。真实钱包可能调整输出顺序；本例明确约定 B:0 给 Bob、B:1 找零。验证者按输出编号定位资金，交易字段里没有“找零”标签。

## 3. 把 U 的花费授权写入见证

**读 Core。** 在 `MutableTransactionSignatureCreator::CreateSig` 里找 `SignatureHash` 调用。它拿到待签交易、输入编号、签名模式、前序输出的脚本编码及金额。对本例，跟进 `SignatureHash` 的 `WITNESS_V0` 分支：普通 `SIGHASH_ALL` 会绑定两个新输出。之后才用 Alice 对应的密钥签摘要并附上模式字节。[Core · 产生签名](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/script/sign.cpp#L37) · [Core · 计算签名摘要](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/script/interpreter.cpp#L1568)

**读 Go。** `RawTxInWitnessSignature` 算见证签名摘要、调用 ECDSA，再把模式字节附在序列化签名后。上一层 `WitnessSignature` 把签名和公钥组成输入见证。读下面的返回值时问一句：为什么放的是 Alice 的公钥？因为当前要解锁的是 U。[Go · 摘要、签名及见证](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/txscript/sign.go#L23)

```go
return wire.TxWitness{sig, pkData}, nil
```

**课堂保留。** 摘要和验签使用现成库。安排两次改动：旁人把 B:0 改成 61,000 聪，原签名失效；Alice 自己给 C 签名，两笔签名都可能有效。第二个结果必须留给后面的状态验证解决。

## 4. 从收到网络消息到本地入池

**读 Core。** 在网络层收到交易后可以找到 `m_chainman.ProcessTransaction(ptx)`。单笔入池路径进入 `MemPoolAccept::AcceptSingleTransaction`：先做较便宜的预检查，需要时检查冲突替换，再做策略脚本检查和共识脚本检查。成功路径通过 `FinalizeSubpackage` 应用池内变更，并处理池容量限制。仅测试是否可接受的调用会提前返回。[Core · 从网络消息提交 B](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/net_processing.cpp#L4263) · [Core · 单笔交易入池](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/validation.cpp#L1415)

**读 Go。** btcd 的同步管理器把收到的交易交给 `TxPool.ProcessTransaction`。沿 `maybeAcceptTransaction` 查看金额、前序输出、池内冲突和脚本检查；缺少父交易时还有单独的处理路径。两个节点的本地策略和已收到的交易可能不同。[Go · 网络消息进入交易池](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/netsync/manager.go#L630) · [Go · ProcessTransaction](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/mempool/mempool.go#L1107) · [Go · 入池检查](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/mempool/mempool.go#L935)

**课堂保留。** 在纸上分别画“内存池”和“已确认 UTXO”。B 入池时只把 B 写到前者；在后者仍应查到 U。若节点只因本地费率门槛拒收 B，矿工仍可能在符合共识规则的块里收录它。

## 5. 从候选交易到满足目标的区块头

**读 Core。** `BlockAssembler::CreateNewBlock` 构造供挖矿使用的候选块模板，处理可共同打包的交易、coinbase 奖励交易及相关承诺。`BlockMerkleRoot` 对有序 txid 建树。`CheckProofOfWorkImpl` 则从压缩目标解出合法范围并检查给定哈希是否命中。模板构造、矿机搜索和节点复核是三个独立动作。[Core · 候选模板](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/node/miner.cpp#L118) · [Core · Merkle 根](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/consensus/merkle.cpp#L66) · [Core · 复核工作量](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/pow.cpp#L161)

**读 Go。** btcd 的 `NewBlockTemplate` 给出组块路径；CPU 矿工的 `solveBlock` 特别适合看懂暴力搜索：更新头里的 nonce，计算头哈希，把它作为整数与目标比较。主网上矿机执行这项搜索，这段 CPU 代码用来阅读同一个命中条件。[Go · 构造区块模板](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/mining/mining.go#L443) · [Go · nonce 搜索与目标比较](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/mining/cpuminer/cpuminer.go#L276)

```go
header.Nonce = i
hash := header.BlockHash()
```

**课堂保留。** 把 B 放在候选块中；改 nonce 时只重算区块头。若改 B 的某个输出，要更新 txid、Merkle 根和区块头，而且旧签名也会失效。教学搜索可调低难度；真实节点必须按该父块和高度规定的目标验证。

## 6. 从一个有效块得到新的 UTXO 状态

**读 Core。** `ConnectBlock` 以父块对应的 UTXO 视图为起点，按块内顺序检查并应用交易。跟进 `UpdateCoins`：花掉旧输出时把旧币内容记进撤销记录，然后调用 `AddCoins` 添加新输出。这也解释了一个设计问题：将来若撤销 B，仅凭 B 的输入引用，读不回 U 的旧金额和脚本。[Core · 整块连接](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/validation.cpp#L2440) · [Core · SpendCoin、撤销记录与 AddCoins](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/validation.cpp#L2101)

**读 Go。** `checkConnectBlock` 在给定的 UTXO 视图上检查区块；`UtxoViewpoint.connectTransaction` 对普通输入查 `PreviousOutPoint`，按需保存旧金额、脚本、高度和 coinbase 标记，调用 `entry.Spend()`，最后 `view.AddTxOuts(...)`。后一个函数只负责状态更新，上层负责验证。[Go · 连接检查](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/blockchain/validate.go#L1037) · [Go · 更新 UTXO 并生成撤销数据](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/blockchain/utxoviewpoint.go#L275)

**课堂保留。** 在临时视图上做三次操作：删除 U，写入 B:0，写入 B:1。若同块下一笔是 C，它再查 U 就会失败；整块不能提交。只有有效块成为活动链的一部分，Bob 的账本中才出现这笔已确认书款。

## 7. 从竞争分支恢复一致的账本

**读 Core。** `GetBlockProof` 按目标计算单块的工作贡献。选出候选链之后，`ActivateBestChainStep` 找共同祖先，向后 `DisconnectTip`，再向前 `ConnectTip`；`DisconnectBlock` 利用撤销数据恢复旧输出。连接时若发现无效块，这条候选历史不能仅凭工作量获胜。[Core · 单块工作量](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/chain.cpp#L131) · [Core · 寻找分叉点并切链](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/validation.cpp#L3350) · [Core · 撤销区块](https://github.com/bitcoin/bitcoin/blob/f490f5562d4b20857ef8d042c050763795fd43da/src/validation.cpp#L2298)

**读 Go。** 在 `connectBestChain` 的侧链路径，可以看到 `node.workSum.Cmp(b.bestChain.Tip().workSum)`。更重的候选分支需要进一步验证。`reorganizeChain` 接收待断开和待接入的区块列表，先检查切换能否成立，再执行断开与接入。两个实现共同维护的条件是：活动链尖与当前 UTXO 视图必须描述同一段历史。[Go · 比较累计工作量](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/blockchain/chain.go#L1252) · [Go · 验证并执行重组](https://github.com/btcsuite/btcd/blob/cc26860b40265e1332cca8748c5dbaf3c81cc094/blockchain/chain.go#L872)

**课堂保留。** 设两边共享父块 P，一边收录 B，另一边收录 C 后再接一块，难度相同。从 B 分支切过去时，先移除 B:0 和 B:1、恢复 U，再由 C 消耗 U。B 的签名依然正确，但已失去可用输入；Bob 若已签了一笔花 B:0 的后续交易，也失去了输入。

## 第一遍读源码，先跟哪三个函数？

沿着 **见证里写了什么 → U 什么时候消失 → U 怎样被恢复** 这条线读。先看第 3 步 Go 的 `WitnessSignature`，再看第 6 步 Core 的 `UpdateCoins`，最后看第 7 步的 `DisconnectBlock`。分别回答“谁授权”“哪份状态接受了付款”“什么变化能撤销付款”，其余四步就有了清楚的位置。
