/*
 * @Author: Justin
 * @Date: 2026-11-20 09:34:47
 * @filename: 
 * @version: 
 * @Description: 
 * @LastEditTime: 2026-11-26 09:32:48
 */
// OpenSSL 3 摘要级 ECDSA：对应讲义的 SignDigest / VerifyDigest。
// 复用已有的密钥生成、公钥提取与第1讲编码，重点只看下面两个函数。
#include "crypto.hpp"
#include <iostream>
using namespace teaching;
using PKeyContext = std::unique_ptr<EVP_PKEY_CTX, decltype(&EVP_PKEY_CTX_free)>;

Bytes sign_digest(EVP_PKEY* private_key, const Hash256& hash) {
    PKeyContext ctx(EVP_PKEY_CTX_new(private_key, nullptr), EVP_PKEY_CTX_free);
    require(bool(ctx), "create sign context");
    require(EVP_PKEY_sign_init(ctx.get()) == 1, "sign init");
    require(EVP_PKEY_CTX_set_signature_md(ctx.get(), EVP_sha256()) == 1, "set SHA256");

    // 库内部：生成k → R=kG → r=x_R mod n → s=k^(-1)(z+r*d) mod n。
    // r/s为0时由库重试；输出DER编码。这一接口不再对hash做SHA-256。
    std::size_t size = 0;
    require(EVP_PKEY_sign(ctx.get(), nullptr, &size, hash.data(), hash.size()) == 1,
            "get signature size");
    Bytes signature(size);
    require(EVP_PKEY_sign(ctx.get(), signature.data(), &size,
                          hash.data(), hash.size()) == 1, "sign digest");
    signature.resize(size);
    return signature;
}

bool verify_digest(EVP_PKEY* public_key, const Hash256& hash, const Bytes& signature) {
    PKeyContext ctx(EVP_PKEY_CTX_new(public_key, nullptr), EVP_PKEY_CTX_free);
    require(bool(ctx), "create verify context");
    require(EVP_PKEY_verify_init(ctx.get()) == 1, "verify init");
    require(EVP_PKEY_CTX_set_signature_md(ctx.get(), EVP_sha256()) == 1, "set SHA256");

    // 库内部：解析DER、检查范围 → w=s^(-1) → X=(z*w)G+(r*w)Q。
    // X不是无穷远点且 x_X mod n == r 才通过；调用者不再哈希。
    int result = EVP_PKEY_verify(ctx.get(), signature.data(), signature.size(),
                                 hash.data(), hash.size());
    if (result < 0) throw std::runtime_error("verify error or malformed signature");
    return result == 1; // 1=通过；0=签名不匹配。
}

int main() try {

    auto alice = generate_key();             // EC / secp256k1；已有crypto.hpp接口
    auto public_key = public_only(alice.get()); // 验证端没有私钥
    auto message = encode({2, 60000});        // 复用第1讲的13字节付款草稿
    auto hash = sha256(message);             // 明确在外层做一次SHA-256
    auto signature = sign_digest(alice.get(), hash);

    bool valid = verify_digest(public_key.get(), hash, signature);
    auto changed_hash = sha256(encode({2, 60001}));
    bool changed = verify_digest(public_key.get(), changed_hash, signature);
    auto other = generate_key();
    auto other_public = public_only(other.get());
    bool wrong_key = verify_digest(other_public.get(), hash, signature);
    require(valid && !changed && !wrong_key, "unexpected verification result");
    // 与现有message接口交叉核对：确认恰好一次哈希，DER也能互通。
    require(verify_message(public_key.get(), message, signature), "message interop");
    require(verify_digest(public_key.get(), hash, sign_message(alice.get(), message)),
            "digest interop");
    std::cout << std::boolalpha << "valid=" << valid
              << "\ntampered=" << changed << "\nwrong_key=" << wrong_key
              << "\nPASS: digest/message interoperability\n";
} catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
    return 1;
}
