#define ECDSA_DEMO_NO_MAIN
#include "toy_curve.cpp"
#include <cassert>

int main() {
    using namespace demo;
    assert(multiply(19, G).infinity);
    const auto q = multiply(7, G);
    assert(q.x == 0 && q.y == 6);
    const auto sig = sign_digest(13, 7, 3);
    assert(sig && sig->r == 10 && sig->s == 15);
    assert(verify_digest(13, *sig, q));
    assert(!verify_digest(14, *sig, q));
    assert(!verify_digest(13, {0, 15}, q));
    assert(!verify_digest(13, {10, 19}, q));
    assert(!verify_digest(13, *sig, Point{}));
    assert(!verify_digest(13, *sig, {1, 1, false}));
    assert(!verify_digest(13, *sig, {17, 6, false}));
    const auto second=sign_digest(14,7,3);
    assert(second && second->s==9 && second->r==sig->r);
    int recovered_k=mod((13-14)*inverse(sig->s-second->s,n),n);
    int recovered_d=mod((sig->s*recovered_k-13)*inverse(sig->r,n),n);
    assert(recovered_k==3 && recovered_d==7);
    // 遍历小曲线上的所有私钥、nonce 和摘要代表值。
    for (int d = 1; d < n; ++d)
        for (int k = 1; k < n; ++k)
            for (int z = 0; z < n; ++z) {
                auto s = sign_digest(z, d, k);
                if (s) assert(verify_digest(z, *s, multiply(d, G)));
            }
    std::cout << "All ECDSA tests passed\n";
}
