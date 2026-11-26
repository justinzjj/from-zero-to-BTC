// 02：生成密钥，只传递公钥
// 阅读/练习：先看key生成，再看public_bytes与pub；用纸画出三个对象的区别。
// 运行：bash run.sh 02（在本目录）；或从项目根目录调用完整脚本路径。
// 本文件可独立编译；只使用C++标准库与OpenSSL 3，没有教学封装函数。
#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/x509.h>
using namespace std;

int main()
{
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

    // 指针位置不同说明对象独立；导出的是公钥信息，不包含私钥。
    cout << "public_DER_bytes=" << public_length << '\n';
    // 再导出一次，检查导入后的对象保留了相同公钥。
    unsigned char copied_bytes[256];
    int copied_length = i2d_PUBKEY(pub, NULL);
    if (copied_length <= 0 || copied_length > (int)sizeof(copied_bytes))
    {
        cout << "再次导出公钥的容量错误\n";
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    unsigned char *copied_position = copied_bytes;
    int copied_written = i2d_PUBKEY(pub, &copied_position);
    if (copied_written != copied_length || copied_length != public_length)
    {
        cout << "公钥长度不一致\n";
        EVP_PKEY_free(pub);
        EVP_PKEY_free(key);
        return 1;
    }

    for (int i = 0; i < public_length; i++)
    {
        if (public_bytes[i] != copied_bytes[i])
        {
            cout << "公钥内容不一致\n";
            EVP_PKEY_free(pub);
            EVP_PKEY_free(key);
            return 1;
        }
    }
    cout << "PASS 02: 公钥导出与导入成功\n";
    // EVP_PKEY_free参数是要释放的对象；无返回值。数组不需要调用它。
    EVP_PKEY_free(pub);
    EVP_PKEY_free(key);
    return 0;
}
