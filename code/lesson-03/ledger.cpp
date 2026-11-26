#include "ledger.hpp"
namespace lesson03 {
bool same_key(const OutPoint& a, const OutPoint& b) {
    return a.index == b.index && a.txid == b.txid;
}

Ledger Ledger::fixture() {
    Ledger book;
    // 人工键：32 字节中只有首字节为 1，输出序号为 0。
    book.coins[0].key.txid[0] = 1;
    book.coins[0].output = {teaching::parse_amount("0.00100000"), 1};
    book.count = 1;
    return book;
}

bool Ledger::read(int index, Coin& copy) const {
    if (index < 0 || index >= count) return false;
    copy = coins[index];
    return true;
}

int Ledger::find(const OutPoint& key) const {
    for (int i = 0; i < count; ++i) {
        if (same_key(coins[i].key, key)) return i;
    }
    return -1;
}

// 先比较剩余额度，再加；失败时 total 保持原值。
static bool add_amount(Amount& total, Amount value) {
    if (value < 0 || value > teaching::MAX_MONEY - total) return false;
    total += value;
    return true;
}

// 只接收已检查长度与金额的交易。put_le 向 bytes 追加指定宽度的小端整数。
// double_sha256 接收完整字节串，返回 32 字节；前课库失败时抛出的异常由程序入口报告。
static Hash256 transaction_id(const Transaction& tx) {
    teaching::Bytes bytes;
    teaching::put_le(bytes, 3, 1);
    teaching::put_le(bytes, tx.input_count, 1);
    for (int i = 0; i < tx.input_count; ++i) {
        const OutPoint& key = tx.vin[i].previous;
        for (unsigned char byte : key.txid) bytes.push_back(byte);
        teaching::put_le(bytes, key.index, 4);
    }
    teaching::put_le(bytes, tx.output_count, 1);
    for (int i = 0; i < tx.output_count; ++i) {
        teaching::put_le(bytes, tx.vout[i].amount, 8);
        teaching::put_le(bytes, tx.vout[i].recipient, 4);
    }
    return teaching::double_sha256(bytes);
}

Result Ledger::check(const Transaction& tx) const {
    if (tx.input_count < 1 || tx.input_count > MAX_INPUTS) return {"input count", 0, {}};
    if (tx.output_count < 1 || tx.output_count > MAX_OUTPUTS) return {"output count", 0, {}};
    Amount incoming = 0, outgoing = 0;
    for (int i = 0; i < tx.input_count; ++i) {
        const OutPoint& key = tx.vin[i].previous;
        for (int j = 0; j < i; ++j) {
            if (same_key(tx.vin[j].previous, key)) return {"duplicate input", 0, {}};
        }
        int slot = find(key);
        if (slot < 0) return {"missing or spent", 0, {}};
        if (!add_amount(incoming, coins[slot].output.amount)) return {"input range", 0, {}};
    }
    for (int i = 0; i < tx.output_count; ++i) {
        if (!add_amount(outgoing, tx.vout[i].amount)) return {"output range", 0, {}};
    }
    if (outgoing > incoming) return {"overspend", 0, {}};
    if (count - tx.input_count + tx.output_count > CAPACITY) return {"ledger full", 0, {}};
    Hash256 id = transaction_id(tx);
    for (int i = 0; i < tx.output_count; ++i) {
        if (find({id, static_cast<std::uint32_t>(i)}) >= 0) return {"output key exists", 0, {}};
    }
    return {nullptr, incoming - outgoing, id};
}

void Ledger::remove(const OutPoint& key) {
    int slot = find(key);  // 之前删除的元素可能移动过，不能沿用旧槽位
    --count;
    coins[slot] = coins[count];
    coins[count] = {};
}

Result Ledger::apply(const Transaction& tx) {
    Result result = check(tx);  // 对当前账本、当前交易检查，不接受外部的检查回执
    if (result.error) return result;
    // 从此处开始只有定长对象赋值，无分配或可失败的库调用。
    for (int i = 0; i < tx.input_count; ++i) remove(tx.vin[i].previous);
    for (int i = 0; i < tx.output_count; ++i) {
        OutPoint key{result.txid, static_cast<std::uint32_t>(i)};
        coins[count++] = {key, tx.vout[i]};
    }
    return result;
}
}
