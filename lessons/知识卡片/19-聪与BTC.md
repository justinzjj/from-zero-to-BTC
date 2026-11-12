# 19 · 聪与 BTC 的计量关系

聪（sat）是 Bitcoin 链上金额的最小单位。BTC 是 bitcoin（比特币）的单位符号。1 BTC 等于 100,000,000 聪，所以 1 聪等于 0.00000001 BTC。交易输出的金额以整数聪编码，钱包可把同一笔金额显示成 BTC。

用一个共同的整数单位，钱包和节点就能精确加减金额。60,000 聪写作 0.00060000 BTC，两种写法指同一笔书款。

**字段与字节。** Core 用 CAmount（int64_t）在内存中表示金额。CTxOut 的 nValue 在普通交易输出中按 8 字节小端编码。60,000 聪等于十六进制 EA60，写入为 `60 ea 00 00 00 00 00 00`；解码时最低两字节贡献 96 + 234 × 256 = 60,000。

**英文术语**　sat（satoshi，聪）。

[换算并解码金额字节](推演-19.md) · [Bitcoin Core v29.0 的金额常量](https://github.com/bitcoin/bitcoin/blob/v29.0/src/consensus/amount.h#L9-L13)

## 图解与实作

- [高度 170 · 真实交易金额](https://mempool.space/zh/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16)　把首个输出的 10 BTC 对应到 1,000,000,000 聪。
- [同一交易的 JSON](https://mempool.space/api/tx/f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16)　查看 vout[0].value 的整数聪金额。
