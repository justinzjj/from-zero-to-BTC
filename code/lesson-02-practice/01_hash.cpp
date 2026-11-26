/*
 * @Author: Justin
 * @Date: 2026-11-25 10:53:14
 * @filename: 
 * @version: 
 * @Description: 
 * @LastEditTime: 2026-11-26 09:39:28
 */
// 01：把数组交给SHA-256函数
// 阅读/练习：修改message，观察输入长度与摘要变化；二进制数组不要用strlen。
// 运行：bash run.sh 01（在本目录）；或从项目根目录调用完整脚本路径。
// 本文件可独立编译；只使用C++标准库与OpenSSL 3，没有教学封装函数。
#include <iostream>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/x509.h>
using namespace std;

int main()
{
    // char数组末尾自动补'\0'。sizeof包含它；本例只哈希前3字节。
    char message[] = "abc";
    unsigned char hash[32];
    unsigned int hash_length = 0;
    int result;

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
        return 1;
    }

    // 标准测试向量：SHA256("abc")，用于检查是否传对字节与长度。
    unsigned char expected[32] = {
        0xba,0x78,0x16,0xbf,0x8f,0x01,0xcf,0xea,
        0x41,0x41,0x40,0xde,0x5d,0xae,0x22,0x23,
        0xb0,0x03,0x61,0xa3,0x96,0x17,0x7a,0x9c,
        0xb4,0x10,0xff,0x61,0xf2,0x00,0x15,0xad
    };
    char digits[] = "0123456789abcdef";
    cout << "sha256=";
    for (int i = 0; i < 32; i++)
    {
        // 高4位和低4位分别变成一个十六进制字符。
        cout << digits[hash[i] >> 4] << digits[hash[i] & 15];
        if (hash[i] != expected[i])
        {
            cout << "\n标准向量不匹配\n";
            return 1;
        }
    }
    cout << "\n";
    // 学生练习：先预测把abc改成abd后，摘要是否相同。
    char changed[] = "abd";
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
        return 1;
    }

    bool same = true;
    for (int i = 0; i < 32; i++)
    {
        if (hash[i] != changed_hash[i]) same = false;
    }
    if (same) return 1;
    cout << "PASS 01: 标准向量正确，改消息后摘要不同\n";
    // 二进制数组不能用strlen找长度：中途可能出现0字节。
    return 0;
}
