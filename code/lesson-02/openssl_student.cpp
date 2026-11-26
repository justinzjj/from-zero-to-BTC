// 学生版：固定数组、普通变量、if判断，直接调用OpenSSL 3。
#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/x509.h>
using namespace std;

int main()
{
    // 指针保存OpenSSL对象的位置。NULL表示还没有对象。
    EVP_PKEY *key = NULL;
    EVP_PKEY *pub = NULL;
    EVP_PKEY_CTX *ctx = NULL;

    unsigned char public_bytes[256]; // 公钥的DER编码
    unsigned char hash[32];          // SHA-256输出32字节
    unsigned char signature[128];    // 足够容纳本例的secp256k1 DER签名
    char message[] = "Alice pays Bob 60000 sat";
    unsigned int hash_length = 0;
    size_t signature_length = sizeof(signature); // OpenSSL要求的长度类型
    int result;

    // 1. 生成secp256k1密钥，key中同时包含公钥与私钥。
    key = EVP_PKEY_Q_keygen(NULL, NULL, "EC", "secp256k1");
    if (key == NULL)
    {
        cout << "生成密钥失败\n";
        return 1;
    }

    // 2. 只复制公钥给验证端。先检查数组够不够大，再写入。
    int public_length = i2d_PUBKEY(key, NULL);
    if (public_length <= 0 || public_length > (int)sizeof(public_bytes))
    {
        cout << "公钥长度错误\n";
        EVP_PKEY_free(key);
        return 1;
    }
    // 数组名指向第一个元素。库会移动write_position，所以另设一个指针。
    unsigned char *write_position = public_bytes;
    if (i2d_PUBKEY(key, &write_position) != public_length)
    {
        cout << "导出公钥失败\n";
        EVP_PKEY_free(key);
        return 1;
    }
    const unsigned char *read_position = public_bytes;
    pub = d2i_PUBKEY(NULL, &read_position, public_length);
    if (pub == NULL)
    {
        cout << "导入公钥失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    // 3. 消息 → SHA-256摘要。strlen不计字符串末尾的'\0'。
    // &hash_length：把变量地址交给库，让库写回输出长度。
    result = EVP_Digest(message, strlen(message), hash, &hash_length,
                        EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算摘要失败\n";
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 4. 初始化签名。ctx保存本次操作的配置。
    ctx = EVP_PKEY_CTX_new(key, NULL);
    if (ctx == NULL || EVP_PKEY_sign_init(ctx) != 1 ||
        EVP_PKEY_CTX_set_signature_md(ctx, EVP_sha256()) != 1)
    {
        cout << "初始化签名失败\n";
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 5. 对hash签名。库内部完成k、R、r、s计算，输出DER签名字节。
    // signature_length传入时是数组容量，返回时是实际签名长度。
    // 此接口不再哈希；set_signature_md也不会让hash再被哈希一次。
    result = EVP_PKEY_sign(ctx, signature, &signature_length, hash, hash_length);
    EVP_PKEY_CTX_free(ctx);
    ctx = NULL;
    if (result != 1)
    {
        cout << "签名失败\n";
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 6. 验签上下文只使用pub，不需要key中的私钥。
    ctx = EVP_PKEY_CTX_new(pub, NULL);
    if (ctx == NULL || EVP_PKEY_verify_init(ctx) != 1 ||
        EVP_PKEY_CTX_set_signature_md(ctx, EVP_sha256()) != 1)
    {
        cout << "初始化验签失败\n";
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 7. 原消息的摘要、公钥、签名一致：应返回1。
    // 返回1：有效；返回0：不匹配；负数：错误。只有1才接受。
    result = EVP_PKEY_verify(ctx, signature, signature_length, hash, hash_length);
    cout << "original_result=" << result << " (expected 1)\n";
    if (result != 1)
    {
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 8. 只改付款金额，并重新算摘要；仍然用旧签名验证。
    char changed_message[] = "Alice pays Bob 60001 sat";
    result = EVP_Digest(changed_message, strlen(changed_message), hash,
                        &hash_length, EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算新摘要失败\n";
        EVP_PKEY_CTX_free(ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }
    result = EVP_PKEY_verify(ctx, signature, signature_length, hash, hash_length);
    cout << "changed_result=" << result << " (expected 0)\n";
    cout << "signature_bytes=" << signature_length << '\n';

    // 9. 不再使用的库对象要释放。固定数组由程序自动管理。
    EVP_PKEY_CTX_free(ctx);
    EVP_PKEY_free(pub);
    EVP_PKEY_free(key);
    if (result != 0) return 1;
    return 0;
}
