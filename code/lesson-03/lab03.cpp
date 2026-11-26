#include "ledger.hpp"
#include <cstring>
#include <iostream>
using namespace lesson03;

// require(condition, message) 复用前课断言；失败抛出错误，由 main 统一报告。
using teaching::require;

static Transaction payment(OutPoint old) {
    Transaction tx;
    tx.input_count = 1;
    tx.vin[0].previous = old;
    tx.output_count = 2;
    tx.vout[0] = {60000, 2};
    tx.vout[1] = {39000, 1};
    return tx;
}

static void print_book(const Ledger& book) {
    for (int i = 0; i < book.size(); ++i) {
        Coin coin{};
        require(book.read(i, coin), "read failed");
        // hex 将摘要按存储顺序显示；不是 Bitcoin 浏览器的 txid 显示约定。
        std::cout << teaching::hex(coin.key.txid) << ":" << coin.key.index
                  << "  owner=" << coin.output.recipient << "  sat=" << coin.output.amount << "\n";
    }
}

// 对比所有有效行、顺序及字段。结构体填充字节不属于账本内容。
static bool same_book(const Ledger& a, const Ledger& b) {
    if (a.size() != b.size()) return false;
    for (int i = 0; i < a.size(); ++i) {
        Coin x{}, y{};
        if (!a.read(i, x) || !b.read(i, y)) return false;
        if (!same_key(x.key, y.key) || x.output.amount != y.output.amount ||
            x.output.recipient != y.output.recipient) return false;
    }
    return true;
}

static void reject(Ledger& book, const Transaction& tx, const char* expected, const char* label) {
    Ledger before = book;
    Result result = book.apply(tx);
    // strcmp(a,b) 按字符串内容比较，返回 0 表示相同。
    require(result.error && std::strcmp(result.error, expected) == 0, label);
    require(same_book(before, book), "rejection changed ledger");
    std::cout << label << " -> " << result.error << " | unchanged\n";
}

int main() try {
    Ledger book = Ledger::fixture();
    Coin old{};
    require(book.read(0, old) && book.find(old.key) == 0, "fixture lookup");
    std::cout << "BEFORE\n";
    print_book(book);
    Transaction tx = payment(old.key);
    Ledger initial = book;
    Result preview = book.check(tx);
    require(!preview.error && same_book(book, initial), "preview changed ledger");
    Result paid = book.apply(tx);
    require(!paid.error && paid.fee == 1000 && paid.txid == preview.txid, "normal payment");
    // 固定编码样本独立计算所得，防止字段顺序或小端宽度悄悄改变。
    require(teaching::hex(paid.txid) ==
            "096003dcc53f5853d941f4cb9ff51934b988bec1d4670b9e3a1e40bfa623ecc7",
            "v3 transaction encoding");
    require(book.size() == 2 && book.find(old.key) == -1, "old output still live");
    for (int i = 0; i < tx.output_count; ++i) {
        Coin created{};
        int slot = book.find({paid.txid, static_cast<std::uint32_t>(i)});
        require(book.read(slot, created) && created.output.amount == tx.vout[i].amount &&
                created.output.recipient == tx.vout[i].recipient, "wrong new coin");
    }
    std::cout << "ACCEPT fee=" << paid.fee << "\nAFTER\n";
    print_book(book);
    reject(book, tx, "missing or spent", "replay");

    Ledger fresh = initial;
    Transaction bad = tx;
    bad.input_count = 2;
    bad.vin[1] = bad.vin[0];
    reject(fresh, bad, "duplicate input", "same input twice");
    bad.vin[1].previous.index = 99;
    reject(fresh, bad, "missing or spent", "second input missing");
    bad = tx;
    bad.vout[0].amount = 62000;
    reject(fresh, bad, "overspend", "edit after successful preview");
    bad.vout[1].amount = -1;
    reject(fresh, bad, "output range", "negative second output");
    bad.vout[0].amount = teaching::MAX_MONEY + 1;
    reject(fresh, bad, "output range", "above limit");
    bad.vout[0].amount = teaching::MAX_MONEY;
    bad.vout[1].amount = 1;
    reject(fresh, bad, "output range", "running sum above limit");
    bad.vout[1].amount = std::numeric_limits<Amount>::max();
    reject(fresh, bad, "output range", "would overflow int64");
    for (int count : {-1, 0, MAX_INPUTS + 1}) {
        bad = tx;
        bad.input_count = count;
        reject(fresh, bad, "input count", "bad vin length");
    }
    for (int count : {-1, 0, MAX_OUTPUTS + 1}) {
        bad = tx;
        bad.output_count = count;
        reject(fresh, bad, "output count", "bad vout length");
    }
    bad = tx;
    bad.vin[0].previous = {paid.txid, 0};
    bad.vout[0].amount = 0;
    bad.output_count = 4;  // 2 - 1 + 4 = 5；即使金额合法也放不下
    reject(book, bad, "ledger full", "capacity");
    bad.output_count = 3;
    Ledger full = book;
    require(!full.apply(bad).error && full.size() == CAPACITY, "exact capacity");
    Coin copy{};
    require(!full.read(-1, copy) && !full.read(full.size(), copy), "invalid read index");
    require(full.read(0, copy), "read copy");
    Ledger snapshot = full;
    copy.output.amount = -1;
    require(same_book(full, snapshot), "read exposed writable state");

    // 花两个不同序号的输出，第二次删除前槽位可能已调换。
    Transaction merge{};
    merge.input_count = 2;
    merge.vin[0].previous = {paid.txid, 0};
    merge.vin[1].previous = {paid.txid, 1};
    merge.output_count = 1;
    merge.vout[0] = {99000, 1};
    Result merged = book.apply(merge);
    require(!merged.error && merged.fee == 0 && book.size() == 1, "merge with zero fee");

    bad = tx;
    bad.vout[0].recipient = 9;
    Result redirected = fresh.apply(bad);
    require(!redirected.error && redirected.txid != paid.txid, "authorization boundary");
    std::cout << "recipient-only edit -> ACCEPT | authorization unchecked\n";
    std::cout << "sizeof(Transaction)=" << sizeof(Transaction) << " sizeof(Coin)=" << sizeof(Coin)
              << " sizeof(Ledger)=" << sizeof(Ledger) << "\nALL CHECKS PASSED\n";
} catch (const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 1;
}
