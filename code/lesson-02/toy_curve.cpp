// 教学用小曲线 ECDSA：只演示数学，不可用于真实安全用途。
// 输入 z 是已转换的消息摘要整数；这里不实现哈希。
#include <iostream>
#include <optional>
#include <stdexcept>

namespace demo {
// y^2 = x^3 + 2x + 2 (mod 17)，G 的阶为 19。
constexpr int p = 17, a = 2, b = 2, n = 19;
struct Point { int x = 0, y = 0; bool infinity = true; };
constexpr Point G{5, 1, false};
struct Signature { int r, s; };

int mod(int x, int m) { return (x % m + m) % m; }

// 扩展欧几里得：求 x^(-1) mod m。
int inverse(int x, int m) {
    int r = m, next_r = mod(x, m), t = 0, next_t = 1;
    while (next_r) {
        int q = r / next_r;
        int tmp = r - q * next_r;
        r = next_r; next_r = tmp;
        tmp = t - q * next_t;
        t = next_t; next_t = tmp;
    }
    if (r != 1) throw std::invalid_argument("inverse does not exist");
    return mod(t, m);
}

bool on_curve(Point q) {
    return !q.infinity && q.x >= 0 && q.x < p && q.y >= 0 && q.y < p
        && mod(q.y*q.y - q.x*q.x*q.x - a*q.x - b, p) == 0;
}

// 内部点运算：输入必须是曲线点或无穷远点。
Point add(Point u, Point v) {
    if (u.infinity) return v;
    if (v.infinity) return u;
    if (u.x == v.x && mod(u.y + v.y, p) == 0) return {};
    int slope;
    if (u.x == v.x) // 倍点；y=0 的情况已在上面处理。
        slope = mod((3*u.x*u.x + a) * inverse(2*u.y, p), p);
    else
        slope = mod((v.y-u.y) * inverse(v.x-u.x, p), p);
    int x = mod(slope*slope-u.x-v.x, p);
    int y = mod(slope*(u.x-x)-u.y, p);
    return {x, y, false};
}

// 双倍—相加法；这里是点乘，不是坐标直接乘以 k。
Point multiply(int k, Point q) {
    if (k < 0) throw std::invalid_argument("negative scalar");
    Point result;
    while (k) {
        if (k & 1) result = add(result, q);
        q = add(q, q);
        k >>= 1;
    }
    return result;
}

// 为了可手算，调用者显式传入 nonce k。
// 实际签名必须安全地产生 k；同一私钥下不能跨消息复用 k。
// 返回空值表示 r 或 s 为零，需要重新选择 k。
std::optional<Signature> sign_digest(int z, int d, int k) {
    if (d < 1 || d >= n || k < 1 || k >= n)
        throw std::invalid_argument("d and k must be in [1,n-1]");
    int r = multiply(k, G).x % n;
    if (r == 0) return std::nullopt;
    int s = mod(inverse(k, n) * (mod(z, n) + r*d), n);
    if (s == 0) return std::nullopt;
    return Signature{r, s};
}

bool verify_digest(int z, Signature sig, Point public_key) {
    if (sig.r < 1 || sig.r >= n || sig.s < 1 || sig.s >= n) return false;
    if (!on_curve(public_key) || !multiply(n, public_key).infinity) return false;
    int w = inverse(sig.s, n);
    int u1 = mod(mod(z, n)*w, n), u2 = mod(sig.r*w, n);
    Point x = add(multiply(u1, G), multiply(u2, public_key));
    return !x.infinity && x.x % n == sig.r;
}
} // namespace demo

#ifndef ECDSA_DEMO_NO_MAIN
int main() {
    using namespace demo;
    const int d = 7, z = 13;
    Point q = multiply(d, G);
    // 固定 k=3 仅用于这一次教学示例；不应作为实际 nonce 生成方式。
    auto sig = sign_digest(z, d, 3);
    if (!sig) throw std::runtime_error("choose another nonce");
    std::cout << "Public key: (" << q.x << ", " << q.y << ")\n"
              << "Signature: (" << sig->r << ", " << sig->s << ")\n"
              << std::boolalpha
              << "Valid: " << verify_digest(z, *sig, q) << '\n'
              << "Tampered: " << verify_digest(z+1, *sig, q) << '\n';
}
#endif
