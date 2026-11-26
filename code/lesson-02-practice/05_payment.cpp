// 05：签署付款字段
// 阅读/练习：重点看12字节的布局与编码循环；先预测改金额、改收款方的结果。
// 运行：bash run.sh 05（在本目录）；或从项目根目录调用完整脚本路径。
// 本文件可独立编译；只使用C++标准库与OpenSSL 3，没有教学封装函数。
#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/x509.h>
using namespace std;

int main()
{
    // 本例明确约定unsigned int为32位，避免平台差异影响4字节编码。
    if (sizeof(unsigned int) != 4)
    {
        cout << "本例需要32位unsigned int\n";
        return 1;
    }
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

    // 本次新增：payer=1预先绑定到上面的pub；不是任意提交公钥都能付款。
    // 接收端保存此绑定，本例用同一进程模拟钱包和验证端。
    unsigned int payer = 1;
    unsigned int receiver = 2;
    unsigned int amount = 60000;
    unsigned int fields[3] = {payer, receiver, amount};
    unsigned char message[12];
    // 固定格式：付款人4字节 + 收款人4字节 + 金额4字节，全部小端。
    // 这是新定义的教学演示格式，不是第1讲13字节草稿，也不是Bitcoin交易。
    // 不直接签结构体内存，避免填充、布局和机器字节序影响。
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            message[i * 4 + j] = (fields[i] >> (8 * j)) & 255U;
        }
    }
    unsigned char hash[32];
    unsigned int hash_length = 0;
    // EVP_Digest参数：输入数组、精确12字节、输出数组、输出长度地址、算法、ENGINE。
    // message不是字符串，不能用strlen，也不需要减去1。
    result = EVP_Digest(message, sizeof(message), hash, &hash_length,
                        EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算付款摘要失败\n";
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

    // 实验：只改金额。fields[2]是金额，重新编码，不直接改原hash。
    fields[2] = 60001;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
            message[i * 4 + j] = (fields[i] >> (8 * j)) & 255U;
    }
    unsigned char changed_hash[32];
    result = EVP_Digest(message, sizeof(message), changed_hash, &hash_length,
                        EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算改金额的摘要失败\n";
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
    cout << "changed_amount=" << result << " (expected 0)\n";
    if (result != 0)
    {
        cout << "验签结果不符合预期\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    // 恢复金额，只改收款方，确保每次仅改变一项。
    fields[2] = amount;
    fields[1] = 3;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 4; j++)
            message[i * 4 + j] = (fields[i] >> (8 * j)) & 255U;
    }
    result = EVP_Digest(message, sizeof(message), changed_hash, &hash_length,
                        EVP_sha256(), NULL);
    if (result != 1 || hash_length != 32)
    {
        cout << "计算改收款方的摘要失败\n";
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
    cout << "changed_receiver=" << result << " (expected 0)\n";
    if (result != 0)
    {
        cout << "验签结果不符合预期\n";
        EVP_PKEY_CTX_free(verify_ctx);
        EVP_PKEY_CTX_free(sign_ctx);
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    cout << "PASS 05: 固定付款字节可以签名；改金额或收款方后旧签名失败\n";
    // 本例还没有余额、UTXO、重放保护；验签通过只是交易检查的一部分。
    // 最后释放：先释放上下文，再释放它借用的密钥；数组自动回收。
    // EVP_PKEY_CTX_free释放操作上下文，无返回值。
    EVP_PKEY_CTX_free(verify_ctx);
    EVP_PKEY_CTX_free(sign_ctx);
    EVP_PKEY_free(pub);
    EVP_PKEY_free(key);
    return 0;
}
