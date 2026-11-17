#include "foundations.hpp"
#include <iostream>
using namespace teaching;
template<class F> void rejects(F f) { bool failed=false; try { f(); } catch(const std::runtime_error&) { failed=true; } require(failed,"invalid input accepted"); }
int main() {
    require(parse_amount("0.00060000")==60000,"amount conversion");
    require(parse_amount("0.00000001")==1,"one sat");
    require(parse_amount("21000000")==MAX_MONEY,"max money");
    for(auto s:{"", "-1", "+1", "1e-8", "NaN", "1.", ".1", "1.000000001", "21000000.00000001", "99999999999999999999999999999999", "1 2"}) rejects([&]{parse_amount(s);});
    auto b=encode({2,parse_amount("0.00060000")});
    require(hex(b)=="010200000060ea000000000000","wire golden vector");
    require(encode(decode(b))==b,"round trip");
    require(encode({2,parse_amount("0.0006")})==b,"equivalent amounts");
    for(std::size_t n=0;n<b.size();++n)rejects([&]{decode(Bytes(b.begin(),b.begin()+n));});
    auto bad=b;bad.push_back(0);rejects([&]{decode(bad);});
    bad=b;bad[0]=2;rejects([&]{decode(bad);});
    bad=b;for(std::size_t i=5;i<13;++i)bad[i]=255;rejects([&]{decode(bad);});
    require(unhex(hex(b))==b,"hex round trip");rejects([]{unhex("0");});rejects([]{unhex("gg");});
    require(hex(sha256(Bytes{'a','b','c'}))=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","SHA256 known vector");
    auto changed=encode({2,60001});require(sha256(changed)!=sha256(b),"modified draft digest");
    std::cout<<"amount_sat=60000\nwire_bytes="<<b.size()<<"\nwire_hex="<<hex(b)<<"\nsha256="<<hex(sha256(b))<<"\ndouble_sha256="<<hex(double_sha256(b))<<"\nsizeof_PaymentDraft="<<sizeof(PaymentDraft)<<"\nPASS: amount, golden encoding, bounds, roundtrip, SHA256 vector, mutation\n";
}
