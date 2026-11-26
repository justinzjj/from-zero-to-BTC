// 03：对摘要签名
// 阅读/练习：重点看sign_init之后的调用；区分signature数组容量和signature_length。
// 运行：bash run.sh 03（在本目录）；或从项目根目录调用完整脚本路径。
// 本文件可独立编译；只使用C++标准库与OpenSSL 3，没有教学封装函数。
#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/x509.h>
using namespace std;

int main()
{
    int result;

    // EVP_PKEY_Q_keygen生成密钥对象，参数依次是：
    // NULL：默认库环境；NULL：不指定实现属性；"EC"：椭圆曲线密钥；
    // "secp256k1"：具体曲线。返回对象指针，失败返回NULL。
    // 此对象同时包含私钥和公钥；不要把整个对象交给验证端。
    EVP_PKEY *key = EVP_PKEY_Q_keygen(NULL, NULL, "EC", "secp256k1");
    if (key == NULL)
    {
        cout << "生成密钥失败\n";
        return 1;
    }

    // 前面已经学过：准备消息并计算摘要。
    char message[] = "Alice pays Bob 60000 sat";
    unsigned char hash[32];
    unsigned int hash_length = 0;
    // EVP_Digest一次计算摘要，参数依次是：
    // 1 message：输入字节数组；2 sizeof(message) - 1：本例文本的字节数，不含末尾'\0'；
    // 3 hash：输出数组；4 &hash_length：让库写回实际输出长度；
    // 5 EVP_sha256()：选择SHA-256；6 NULL：不指定旧式ENGINE。
    // 返回1表示成功。SHA-256输出32字节，不是32个文本字符。
    result = EVP_Digest(message, sizeof(message) - 1, hash, &hash_length,
                        EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算SHA-256失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_CTX_new参数：key=签名密钥；NULL=不指定旧式ENGINE。
    // 返回本次操作的上下文：保存密钥和算法配置；失败返回NULL。
    EVP_PKEY_CTX *sign_ctx = EVP_PKEY_CTX_new(key, NULL);
    if (sign_ctx == NULL)
    {
        cout << "创建签名上下文失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_sign_init只有一个参数：待初始化的上下文。
    // EC密钥在这里使用ECDSA。返回1表示成功。
    result = EVP_PKEY_sign_init(sign_ctx);
    if (result != 1)
    {
        cout << "初始化签名失败\n";
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(key);
        return 1;
    }

    // 参数：上下文、摘要算法。说明随后传入的是SHA-256摘要。
    // 注意：这个设置不会再次计算SHA-256。
    result = EVP_PKEY_CTX_set_signature_md(sign_ctx, EVP_sha256());
    if (result != 1)
    {
        cout << "设置签名摘要类型失败\n";
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(key);
        return 1;
    }

    unsigned char signature[128]; // 只针对本例secp256k1；其他算法不能照搬容量。
    size_t signature_length = 0;  // size_t是库要求的无符号长度类型。
    // EVP_PKEY_sign参数：上下文、输出数组、长度变量地址、输入摘要、摘要长度。
    // 第2参数NULL：只查询输出需要的最大容量，第3参数接收该容量。
    result = EVP_PKEY_sign(sign_ctx, NULL, &signature_length, hash, hash_length);
    if (result != 1 || signature_length > sizeof(signature))
    {
        cout << "签名容量查询失败或数组太小\n";
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(key);
        return 1;
    }

    // 正式调用前，signature_length必须表示可写容量。
    signature_length = sizeof(signature);
    // 返回1：签名成功；库把DER签名写入signature，并写回实际长度。
    // 库内部生成nonce、计算r/s；这里不手写数学，也不再次哈希。
    result = EVP_PKEY_sign(sign_ctx, signature, &signature_length, hash, hash_length);
    if (result != 1 || signature_length == 0)
    {
        cout << "签名失败\n";
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(key);
        return 1;
    }

    cout << "signature_bytes=" << signature_length << '\n';
    // 实际长度可能变化；只能读取signature_length个字节，不能打印整个数组容量。
    char digits[] = "0123456789abcdef";
    cout << "signature_DER=";
    for (size_t i = 0; i < signature_length; i++)
    {
        cout << digits[signature[i] >> 4] << digits[signature[i] & 15];
    }
    cout << "\nPASS 03: 签名生成成功；有效性在下一个demo验证\n";
    // 最后释放：先释放上下文，再释放它借用的密钥；数组自动回收。
    // EVP_PKEY_CTX_free释放操作上下文，无返回值。
    EVP_PKEY_CTX_free(sign_ctx);
    EVP_PKEY_free(key);
    return 0;
}
