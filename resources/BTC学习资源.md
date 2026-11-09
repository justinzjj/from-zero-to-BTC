# BTC 学习资源

## 系统教程与教材

- **Learn Me A Bitcoin** 从零基础图解延伸到协议字段、真实交易和区块数据。想弄清某个部件怎样工作，可以按主题进入技术指南，再用原始数据对照图解。[全站](https://learnmeabitcoin.com/) · [技术指南索引](https://learnmeabitcoin.com/technical/)
- **BTCVisual** 中文互动入门站，用一笔付款串起双花、节点验证、出块和确认，再用短实验解释哈希、挖矿和网络传播。[学习路线与六步演示](https://btcvisual.com/) · [传播实验：断开连接后哪些节点还能收到消息](https://btcvisual.com/experiments/network)
- **廖雪峰《区块链教程》** 中文技术教程，从比特币的区块、挖矿、交易和钱包讲到以太坊账户与智能合约。比特币篇从日常转账切入，适合第一次接触电子现金的读者。[比特币篇与全书目录](https://liaoxuefeng.com/books/blockchain/bitcoin/index.html)
- **肖臻《区块链技术与应用》** 中文板书公开课。前半系统讲 Bitcoin 的密码学基础、数据结构、协议、挖矿、脚本和分叉；后半转向以太坊的账户、状态树与智能合约。[全课合集](https://www.bilibili.com/video/BV1Vt411X7JF/)
- **Mastering Bitcoin 第三版** 面向技术读者的开放教材，从一笔支付逐步深入密钥、地址、钱包、交易、脚本、点对点网络、挖矿和共识，适合沿着一个协议问题查到实现细节。[全书与代码](https://github.com/bitcoinbook/bitcoinbook)
- **Stanford CS251** 大学课程，从密码学、Bitcoin 和钱包延伸到分布式共识、以太坊与去中心化应用。[全课程与配套阅读](https://cs251.stanford.edu/syllabus.html)
- **Mastering the Lightning Network** 系统讲解比特币的链下支付：从钱包收款和运行节点，到通道开关、多跳路由与支付转发。[在线全书](https://lnbook.256k1.dev/),[github仓库](https://github.com/lnbook/lnbook)

## 开发文档与参考资料

- **Bitcoin Developer Documentation** 指南解释区块链、交易、钱包、挖矿和 P2P 网络怎样工作；参考手册用来核对字段、消息和接口，示例展示如何实际调用。[指南、参考手册与示例](https://developer.bitcoin.org/index.html)
- **Bitcoin Core Onboarding** 面向想读懂或参与 Bitcoin Core 开发的人，串起编译测试、代码组织、共识验证、钱包、网络和内存池。组件图适合先看一笔交易在节点内部经过哪些模块。[开发者手册](https://bitcoincore.academy/) · [节点、命令行与钱包组件图](https://bitcoincore.academy/components-overview.html)
- **Bitcoin.org 中文资源目录** 社区维护的资料导航，汇集学习材料、技术文档和工具入口，适合继续寻找专题来源。[中文资源目录](https://bitcoin.org/zh_CN/resources)

## 代码实操

- **Jeiwan · Building Blockchain in Go** 分篇从一个最小区块搭出教学链，逐步加入工作量证明、持久化、命令行、交易、钱包、未花费输出和节点通信。适合已经会基础 Go、想看每个功能怎样接入前一版代码的读者。[英文系列第一篇](https://jeiwan.net/posts/building-blockchain-in-go-part-1/) · [中文逐章目录](https://github.com/liuchengxu/blockchain-tutorial)
- **Karpathy · A from-scratch tour of Bitcoin in Python** 一篇完整的交易编程实录：从私钥推导公钥和地址，用一个已有输出构造付款与找零，再签名、序列化并广播传统 P2PKH 交易。最值得跟着写的是从交易字段到可广播字节的过程。[Python 长文与代码](https://karpathy.github.io/2021/06/21/blockchain/)

## 专题讲解与交互演示

- **3Blue1Brown · 比特币究竟怎样工作** 从朋友间的共享账本开始，逐次引入冒签、重复花费和账本分歧，让读者理解为什么需要数字签名与工作量证明。[动画与配套图文](https://www.3blue1brown.com/lessons/bitcoin/)
- **Bitcoin Access · How Bitcoin Works** 学院把区块链、钱包、节点、挖矿和共识分题讲解；这一页的模拟器适合追踪一笔付款，逐步看节点何时验证交易、矿工何时组块、收款何时获得确认。[Alice → Bob 交易模拟器](https://www.bitcoinaccess.org/academy/bitcoin/how-bitcoin-works)
- **The Bitcoin Transaction Life Cycle** 一张可投影的流程图，用两条线索串起用户操作与后台处理，从扫码付款、签名、广播一直画到首次确认及后续确认。[作者的高清信息图](https://www.bitcoindesigned.com/infographics/the-bitcoin-transaction-life-cycle/)
- **Blockchain Demo** Anders Brownworth 的浏览器实验从哈希、区块和工作量证明推进到多份账本、代币与区块奖励。最直观的操作是改写旧区块，再逐块重新挖矿，观察哪些后继块仍受影响。[MIT 分步演示](https://blockchain.mit.edu/how-blockchain-works/) · [直接修改一条区块链](https://andersbrownworth.com/blockchain/blockchain)
- **本仓库《一笔 BTC 付款的一生》** 跟着 Alice 的书款对照三次账本状态：入池时旧输出仍在，首次确认后 Bob 得到新输出，竞争分支胜出后这项收款可能消失。[中文讲义与账本快照](../lessons/0-BTC%20overview.md)

## 区块浏览器与真实数据

- **mempool.space** 查看一个观察点上的未确认交易、费率、预计打包情况和已挖区块。高度 170 的历史交易提供了可复查的例子：一个 50 BTC 输入生成 10 BTC 和 40 BTC 两个输出，手续费为零。[中文浏览器](https://mempool.space/zh/) · [历史交易图](https://mempool.space/zh/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16) · [同笔交易的 JSON 数据](https://mempool.space/api/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16) · [开源项目与部署说明](https://github.com/mempool/mempool)
- **Bitfeed** 把节点看到的未确认交易和新挖区块画成动态图。切换显示模式，可以观察同一笔交易的金额和区块空间占用如何分别体现在图形大小上。[实时动画](https://bitfeed.live/) · [作者图例与显示模式说明](https://github.com/bitfeed-project/bitfeed/wiki/FAQ)
