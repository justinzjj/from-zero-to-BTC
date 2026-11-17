#include "crypto.hpp"
#include <iostream>
#include <chrono>
using namespace teaching;
int main() {
    auto alice=generate_key();auto pub=public_only(alice.get());auto other=generate_key();
    auto message=encode({2,parse_amount("0.00060000")}); auto sig=sign_message(alice.get(),message);
    auto compressed=compressed_public(pub.get());
    require(compressed.size()==33&&(compressed[0]==2||compressed[0]==3),"compressed SEC1");
    auto id=hash160(compressed);require(id.size()==20,"HASH160 length");
    require(verify_message(pub.get(),message,sig),"valid signature");
    require(!verify_message(pub.get(),encode({2,60001}),sig),"tampered amount accepted");
    require(!verify_message(pub.get(),encode({3,60000}),sig),"tampered recipient accepted");
    require(!verify_message(other.get(),message,sig),"wrong public key accepted");
    require(!verify_message(pub.get(),message,Bytes{0}),"malformed signature accepted");
    auto bad=sig;bad.back()^=1;require(!verify_message(pub.get(),message,bad),"tampered signature accepted");
    auto h=sha256(message);auto wrong=sign_message(alice.get(),Bytes(h.begin(),h.end()));
    require(!verify_message(pub.get(),message,wrong),"double hash mismatch accepted");
    auto again=sign_message(alice.get(),message);require(verify_message(pub.get(),message,again),"second signature");
    constexpr int count=200;auto start=std::chrono::steady_clock::now();
    for(int i=0;i<count;++i)require(verify_message(pub.get(),message,sig),"benchmark verify");
    auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"wire_hex="<<hex(message)<<"\npublic_bytes="<<compressed.size()<<"\nkey_id_bytes="<<id.size()<<"\nsignature_DER_bytes="<<sig.size()<<"\nvalid=true\ntampered_amount=false\ntampered_recipient=false\nwrong_key=false\nmalformed_signature=false\nextra_hash=false\nverify_average_us="<<double(us)/count<<"\nPASS: public-only verify, authorization mutations, encoding, hash boundary\n";
}
