#pragma once
#include "foundations.hpp"
#include <openssl/core_names.h>
#include <openssl/x509.h>
#include <memory>
namespace teaching {
using Key=std::unique_ptr<EVP_PKEY,decltype(&EVP_PKEY_free)>;
using Context=std::unique_ptr<EVP_MD_CTX,decltype(&EVP_MD_CTX_free)>;
/* 数学原理：secp256k1 的坐标在模 p 的域中计算，p=2^256-2^32-977。
 * 曲线 y^2 = x^3 + 7 (mod p)。G为标准基点，n为G的阶。
 * 库生成 1<=d<n 的私钥，计算公钥 Q=dG；不由应用手工实现点运算。
 */
inline Key generate_key() { Key k(EVP_PKEY_Q_keygen(nullptr,nullptr,"EC","secp256k1"),EVP_PKEY_free); require(bool(k),"key generation"); return k; }
// Export public information only; verifier receives no private scalar.
inline Key public_only(EVP_PKEY* key) {
    int size=i2d_PUBKEY(key,nullptr);require(size>0,"public size");Bytes der(size);auto* p=der.data();
    require(i2d_PUBKEY(key,&p)==size,"public export");const auto* q=der.data();
    Key pub(d2i_PUBKEY(nullptr,&q,size),EVP_PKEY_free);require(bool(pub)&&q==der.data()+size,"public import");return pub;
}
inline Bytes compressed_public(EVP_PKEY* key) {
    require(EVP_PKEY_set_utf8_string_param(key,OSSL_PKEY_PARAM_EC_POINT_CONVERSION_FORMAT,"compressed")==1,"point format");
    std::size_t size=0;require(EVP_PKEY_get_octet_string_param(key,OSSL_PKEY_PARAM_PUB_KEY,nullptr,0,&size)==1,"public length");
    Bytes out(size);require(EVP_PKEY_get_octet_string_param(key,OSSL_PKEY_PARAM_PUB_KEY,out.data(),out.size(),&size)==1,"public encoding");out.resize(size);return out;
}
inline Bytes hash160(const Bytes& bytes) { auto h=sha256(bytes);return digest(Bytes(h.begin(),h.end()),EVP_ripemd160()); }
// Input is MESSAGE BYTES. EVP performs SHA256 internally exactly once.
/* 数学原理：这里输入原始消息 m，EVP内部计算一次SHA-256并得到摘要整数z。
 * ECDSA签名：库安全地产生nonce k，计算 R=kG，r=x_R mod n，
 * s=k^(-1)*(z+r*d) mod n；r或s为0则重试。输出DER编码的(r,s)。
 * 坐标运算模p，签名标量运算模n；私钥d和nonce k不发送给验证端。
 * nonce由OpenSSL管理，不承诺与Core的RFC6979/low-R路径一致。
 * 本接口不是Bitcoin BIP143：后者对规定预映像做双SHA-256后签名。
 */
inline Bytes sign_message(EVP_PKEY* key,const Bytes& message) {
    Context ctx(EVP_MD_CTX_new(),EVP_MD_CTX_free);require(bool(ctx),"sign context");
    require(EVP_DigestSignInit(ctx.get(),nullptr,EVP_sha256(),nullptr,key)==1,"sign init");
    std::size_t size=0;require(EVP_DigestSign(ctx.get(),nullptr,&size,message.data(),message.size())==1,"signature size");
    Bytes sig(size);require(EVP_DigestSign(ctx.get(),sig.data(),&size,message.data(),message.size())==1,"signature");sig.resize(size);return sig;
}
/* 数学原理：验证端以同一消息得到z，解析DER，检查公钥与r/s范围。
 * w=s^(-1) mod n；u1=z*w mod n；u2=r*w mod n；X=u1*G+u2*Q。
 * 若X是无穷远点则拒绝；否则检查 x_X mod n == r。
 * 正确性：Q=dG，使 X=(z+r*d)*s^(-1)*G=kG=R。
 * 这些步骤由EVP内部执行；该等式不替代安全假设或公钥归属检查。
 * 应用仍须绑定预期公钥；验签通过不证明余额、未双花或交易确认。
 */
inline bool verify_message(EVP_PKEY* pub,const Bytes& message,const Bytes& signature) {
    Context ctx(EVP_MD_CTX_new(),EVP_MD_CTX_free);require(bool(ctx),"verify context");
    require(EVP_DigestVerifyInit(ctx.get(),nullptr,EVP_sha256(),nullptr,pub)==1,"verify init");
    // Return 0 or a malformed-signature error as verification failure; init errors throw.
    return EVP_DigestVerify(ctx.get(),signature.data(),signature.size(),message.data(),message.size())==1;
}
}
