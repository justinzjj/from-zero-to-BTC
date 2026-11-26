#pragma once
#include "../lesson-01/foundations.hpp"

namespace lesson03 {
using teaching::Amount;
using teaching::Hash256;
constexpr int MAX_INPUTS = 4, MAX_OUTPUTS = 4, CAPACITY = 4;

struct OutPoint { Hash256 txid; std::uint32_t index; };
struct TxIn { OutPoint previous; };
struct TxOut { Amount amount; std::uint32_t recipient; };
struct Transaction {
    int input_count = 0, output_count = 0;
    TxIn vin[MAX_INPUTS]{};
    TxOut vout[MAX_OUTPUTS]{};
};
struct Coin { OutPoint key; TxOut output; };
// error 为空指针代表成功。fee 和 txid 仅在成功时有意义。
struct Result { const char* error; Amount fee; Hash256 txid; };

bool same_key(const OutPoint& a, const OutPoint& b);
class Ledger {
    Coin coins[CAPACITY]{};
    int count = 0;
    // 仅在完整检查后调用；外部无法直接增删记录。
    void remove(const OutPoint& key);
public:
    static Ledger fixture();  // 创建独立实验起点，不向现有账本充值
    int size() const { return count; }
    bool read(int index, Coin& copy) const;  // 返回副本，越界时返回 false
    int find(const OutPoint& key) const;    // 返回当前槽位，缺失返回 -1
    Result check(const Transaction& tx) const;
    Result apply(const Transaction& tx);
};
}
