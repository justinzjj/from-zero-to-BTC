#pragma once
#include <openssl/evp.h>
#include <array>
#include <algorithm>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
namespace teaching {
using Amount = std::int64_t;
using Bytes = std::vector<unsigned char>;
using Hash256 = std::array<unsigned char, 32>;
constexpr Amount COIN = 100000000;
constexpr Amount MAX_MONEY = 21000000LL * COIN;
inline void require(bool ok, const char* why) { if (!ok) throw std::runtime_error(why); }
// Deliberately strict input grammar: digits, optionally '.' followed by 1..8 digits.
inline Amount parse_amount(const std::string& s) {
    require(!s.empty() && s.size() <= 32, "amount length");
    Amount whole=0, fraction=0; unsigned digits=0; bool dot=false, before=false;
    for (char c:s) {
        if (c=='.') { require(!dot && before,"decimal point"); dot=true; continue; }
        require(c>='0' && c<='9',"amount character"); int d=c-'0';
        if (!dot) { before=true; require(whole <= (21000000-d)/10,"amount overflow"); whole=whole*10+d; }
        else { require(digits<8,"amount precision"); fraction=fraction*10+d; ++digits; }
    }
    require(!dot || digits>0,"empty fraction");
    while(digits<8) { fraction*=10; ++digits; }
    Amount value=whole*COIN+fraction; require(value<=MAX_MONEY,"amount range"); return value;
}
inline void put_le(Bytes& b, std::uint64_t v, unsigned width) {
    require(width>=1 && width<=8,"integer width");
    for(unsigned i=0;i<width;++i) b.push_back(static_cast<unsigned char>(v>>(8*i)));
}
struct Reader {
    const Bytes& bytes; std::size_t pos=0;
    std::uint64_t le(unsigned width) {
        require(width>=1 && width<=8 && width<=bytes.size()-pos,"truncated integer");
        std::uint64_t v=0; for(unsigned i=0;i<width;++i) v|=std::uint64_t(bytes[pos++])<<(8*i); return v;
    }
};
// An intent, NOT a UTXO transaction; recipient IDs are provisional integers.
struct PaymentDraft { std::uint32_t recipient; Amount amount; };
inline Bytes encode(const PaymentDraft& d) {
    require(d.amount>=0 && d.amount<=MAX_MONEY,"draft amount");
    Bytes b; b.reserve(13); b.push_back(1); put_le(b,d.recipient,4); put_le(b,d.amount,8); return b;
}
inline PaymentDraft decode(const Bytes& b) {
    require(b.size()==13,"draft size"); Reader r{b}; require(r.le(1)==1,"draft version");
    auto recipient=static_cast<std::uint32_t>(r.le(4)); auto value=r.le(8);
    require(value<=static_cast<std::uint64_t>(MAX_MONEY),"draft range");
    return {recipient,static_cast<Amount>(value)};
}
inline Bytes digest(const Bytes& bytes, const EVP_MD* md) {
    require(md!=nullptr,"digest unavailable"); Bytes out(EVP_MAX_MD_SIZE); unsigned size=0;
    require(EVP_Digest(bytes.data(),bytes.size(),out.data(),&size,md,nullptr)==1,"digest failed");
    out.resize(size); return out;
}
inline Hash256 sha256(const Bytes& bytes) {
    auto b=digest(bytes,EVP_sha256()); require(b.size()==32,"digest size"); Hash256 h{};
    std::copy(b.begin(),b.end(),h.begin()); return h;
}
inline Hash256 double_sha256(const Bytes& b) { auto h=sha256(b); return sha256(Bytes(h.begin(),h.end())); }
template<class T> inline std::string hex(const T& bytes) {
    const char* digits="0123456789abcdef"; std::string out; out.reserve(bytes.size()*2);
    for(auto b:bytes) { out+=digits[b>>4]; out+=digits[b&15]; } return out;
}
inline Bytes unhex(const std::string& s) {
    require(s.size()%2==0,"hex length");
    auto nibble=[](char c)->unsigned { if(c>='0'&&c<='9')return c-'0'; if(c>='a'&&c<='f')return c-'a'+10; if(c>='A'&&c<='F')return c-'A'+10; throw std::runtime_error("hex digit"); };
    Bytes out; for(std::size_t i=0;i<s.size();i+=2)out.push_back(static_cast<unsigned char>(nibble(s[i])*16+nibble(s[i+1]))); return out;
}
}
