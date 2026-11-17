#pragma once
#include "foundations.hpp"
#include <openssl/core_names.h>
#include <openssl/x509.h>
#include <memory>
namespace teaching {
using Key=std::unique_ptr<EVP_PKEY,decltype(&EVP_PKEY_free)>;
using Context=std::unique_ptr<EVP_MD_CTX,decltype(&EVP_MD_CTX_free)>;
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
inline Bytes sign_message(EVP_PKEY* key,const Bytes& message) {
    Context ctx(EVP_MD_CTX_new(),EVP_MD_CTX_free);require(bool(ctx),"sign context");
    require(EVP_DigestSignInit(ctx.get(),nullptr,EVP_sha256(),nullptr,key)==1,"sign init");
    std::size_t size=0;require(EVP_DigestSign(ctx.get(),nullptr,&size,message.data(),message.size())==1,"signature size");
    Bytes sig(size);require(EVP_DigestSign(ctx.get(),sig.data(),&size,message.data(),message.size())==1,"signature");sig.resize(size);return sig;
}
inline bool verify_message(EVP_PKEY* pub,const Bytes& message,const Bytes& signature) {
    Context ctx(EVP_MD_CTX_new(),EVP_MD_CTX_free);require(bool(ctx),"verify context");
    require(EVP_DigestVerifyInit(ctx.get(),nullptr,EVP_sha256(),nullptr,pub)==1,"verify init");
    // Return 0 or a malformed-signature error as verification failure; init errors throw.
    return EVP_DigestVerify(ctx.get(),signature.data(),signature.size(),message.data(),message.size())==1;
}
}
