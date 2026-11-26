// 04：验签与主动篡改
// 阅读/练习：前半段复习生成密钥、编码公钥、签名；从verify_ctx开始是新内容。
// 运行：bash run.sh 04（在本目录）；或从项目根目录调用完整脚本路径。
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

    // 只导出公钥。DER是公钥的一种字节编码，不是Bitcoin地址。
    unsigned char public_bytes[256];
    // i2d_PUBKEY(key, NULL)：只查询公钥DER长度，不写入数据。
    // 第1个参数是密钥对象，第2个参数为NULL时返回所需字节数。
    int public_length = i2d_PUBKEY(key, NULL);
    if (public_length <= 0 || public_length > (int)sizeof(public_bytes))
    {
        cout << "公钥编码超过数组容量或查询失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    // 数组名指向首字节。另设指针，是因为i2d_PUBKEY会推进该指针。
    unsigned char *write_position = public_bytes;
    // &write_position：把“指针变量的地址”传给库，允许库修改该指针。
    // 返回实际写入的字节数；public_bytes数组本身不会移动。
    int written = i2d_PUBKEY(key, &write_position);
    if (written != public_length)
    {
        cout << "公钥导出失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    // const表示导入时不修改输入字节；read_position本身仍会前进。
    const unsigned char *read_position = public_bytes;
    // d2i_PUBKEY参数：NULL=创建新对象；&read_position=输入位置；
    // public_length=可读取的字节数。返回仅含公钥的新对象，失败返回NULL。
    EVP_PKEY *pub = d2i_PUBKEY(NULL, &read_position, public_length);
    if (pub == NULL)
    {
        cout << "公钥导入失败\n";
        EVP_PKEY_free(key);
        return 1;
    }

    if (read_position != public_bytes + public_length)
    {
        cout << "公钥字节未完整解析\n";
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
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
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_CTX_new参数：key=签名密钥；NULL=不指定旧式ENGINE。
    // 返回本次操作的上下文：保存密钥和算法配置；失败返回NULL。
    EVP_PKEY_CTX *sign_ctx = EVP_PKEY_CTX_new(key, NULL);
    if (sign_ctx == NULL)
    {
        cout << "创建签名上下文失败\n";
        EVP_PKEY_free(pub);
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
        EVP_PKEY_free(pub);
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
        EVP_PKEY_free(pub);
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
        EVP_PKEY_free(pub);
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
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    cout << "signature_bytes=" << signature_length << '\n';
    // 实际长度可能变化；只能读取signature_length个字节，不能打印整个数组容量。
    // 验证端只使用pub。EVP_PKEY_CTX_new参数仍是密钥对象与NULL。
    EVP_PKEY_CTX *verify_ctx = EVP_PKEY_CTX_new(pub, NULL);
    if (verify_ctx == NULL)
    {
        cout << "创建验签上下文失败\n";
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_verify_init(ctx)：把上下文初始化为验签操作，成功返回1。
    result = EVP_PKEY_verify_init(verify_ctx);
    if (result != 1)
    {
        cout << "初始化验签失败\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 与签名端一致：输入是SHA-256摘要；不会自动重新哈希。
    result = EVP_PKEY_CTX_set_signature_md(verify_ctx, EVP_sha256());
    if (result != 1)
    {
        cout << "设置验签摘要类型失败\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_verify参数：上下文、签名字节、签名实际长度、摘要、摘要长度。
    // 返回1=有效；0=不匹配；负数=运行错误或某些畸形签名错误。
    // 只能把1当作通过；这个正常/消息篡改实验预期为1。
    result = EVP_PKEY_verify(verify_ctx, signature, signature_length,
                             hash, hash_length);
    cout << "original=" << result << " (expected 1)\n";
    if (result != 1)
    {
        cout << "验签结果不符合预期\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 实验A：只修改消息，重新算摘要，保留旧签名与公钥。
    char changed[] = "Alice pays Bob 60001 sat";
    unsigned char changed_hash[32];
    unsigned int changed_length = 0;
    // EVP_Digest一次计算摘要，参数依次是：
    // 1 changed：输入字节数组；2 sizeof(changed) - 1：本例文本的字节数，不含末尾'\0'；
    // 3 changed_hash：输出数组；4 &changed_length：让库写回实际输出长度；
    // 5 EVP_sha256()：选择SHA-256；6 NULL：不指定旧式ENGINE。
    // 返回1表示成功。SHA-256输出32字节，不是32个文本字符。
    result = EVP_Digest(changed, sizeof(changed) - 1, changed_hash, &changed_length,
                        EVP_sha256(), NULL);
    if (result != 1 || changed_length != 32)
    {
        cout << "计算SHA-256失败\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_verify参数：上下文、签名字节、签名实际长度、摘要、摘要长度。
    // 返回1=有效；0=不匹配；负数=运行错误或某些畸形签名错误。
    // 只能把1当作通过；这个正常/消息篡改实验预期为0。
    result = EVP_PKEY_verify(verify_ctx, signature, signature_length,
                             changed_hash, hash_length);
    cout << "changed_message=" << result << " (expected 0)\n";
    if (result != 0)
    {
        cout << "验签结果不符合预期\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 实验B：只改签名；原消息摘要不变。复制实际长度，避免读未初始化字节。
    unsigned char changed_signature[128];
    for (size_t i = 0; i < signature_length; i++) changed_signature[i] = signature[i];
    changed_signature[signature_length - 1] ^= 1;
    result = EVP_PKEY_verify(verify_ctx, changed_signature, signature_length,
                             hash, hash_length);
    // 畸形签名可能返回负数，不能一概预言返回0；仅1表示被接受。
    cout << "changed_signature_rejected=" << (result != 1) << '\n';
    if (result == 1)
    {
        cout << "修改签名后意外通过\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // EVP_PKEY_Q_keygen生成密钥对象，参数依次是：
    // NULL：默认库环境；NULL：不指定实现属性；"EC"：椭圆曲线密钥；
    // "secp256k1"：具体曲线。返回对象指针，失败返回NULL。
    // 此对象同时包含私钥和公钥；不要把整个对象交给验证端。
    EVP_PKEY *other = EVP_PKEY_Q_keygen(NULL, NULL, "EC", "secp256k1");
    if (other == NULL)
    {
        cout << "生成密钥失败\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 实验C：换成另一把公钥。此例上下文借用other对象中的公开部分。
    // other含其自己的私钥，但EVP_PKEY_verify只使用公钥；不是原授权者的密钥。
    EVP_PKEY_CTX *other_ctx = EVP_PKEY_CTX_new(other, NULL);
    if (other_ctx == NULL)
    {
        cout << "创建其他公钥上下文失败\n";
        EVP_PKEY_free(other);
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    result = EVP_PKEY_verify_init(other_ctx);
    if (result != 1)
    {
        cout << "初始化其他公钥验签失败\n";
        EVP_PKEY_CTX_free(other_ctx);
        EVP_PKEY_free(other);
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    result = EVP_PKEY_CTX_set_signature_md(other_ctx, EVP_sha256());
    if (result != 1)
    {
        cout << "设置其他公钥摘要类型失败\n";
        EVP_PKEY_CTX_free(other_ctx);
        EVP_PKEY_free(other);
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    result = EVP_PKEY_verify(other_ctx, signature, signature_length, hash, hash_length);
    cout << "wrong_key=" << result << " (expected 0)\n";
    if (result != 0)
    {
        cout << "错误公钥实验结果异常\n";
        EVP_PKEY_CTX_free(other_ctx);
        EVP_PKEY_free(other);
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    cout << "PASS 04: 原消息通过；消息、公钥、签名改变均未通过\n";
    // 最后释放：先释放上下文，再释放它借用的密钥；数组自动回收。
    // EVP_PKEY_CTX_free释放操作上下文，无返回值。
    EVP_PKEY_CTX_free(other_ctx);
    EVP_PKEY_free(other);
    EVP_PKEY_CTX_free(verify_ctx);
    EVP_PKEY_CTX_free(sign_ctx);
    EVP_PKEY_free(pub);
    EVP_PKEY_free(key);
    return 0;
}
