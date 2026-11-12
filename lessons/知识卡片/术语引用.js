// Each independently opened step, explanation or dialog has its own first mentions.
(() => {
  const entries = {
    '01': '双 SHA-256|双 SHA256|SHA-256|SHA256|RIPEMD-160|HASH160|wtxid|txid|字节序|交易标识|公钥哈希',
    '02': 'secp256k1|压缩公钥|标量乘法|私钥|公钥',
    '03': '助记词|BIP39|BIP84|HMAC-SHA512|BIP32|链码|扩展公钥|扩展私钥|普通派生|硬化派生|链码派生|子密钥派生',
    '04': '收款地址|Bech32|见证版本|见证程序|scriptPubKey|收款脚本|找零脚本',
    '05': '脚本缓存|脚本索引|脚本匹配|原生 P2WPKH 输出|P2WPKH|scriptSig|脚本操作码|锁定条件',
    '05a': '见证栈|输入见证|见证数据|见证|witness',
    '06': 'UTXO|未花费交易输出|旧输出 U|前序输出|输出编号|输出序号|COutPoint|outpoint|CompactSize|交易序列化|序列化',
    '07': 'Branch and Bound|分支限界搜索|选币|虚拟大小|费率|找零',
    '08': 'BIP143|SIGHASH_ALL|scriptCode|签名摘要|计算摘要',
    '09': 'ECDSA|DER|验签|签名',
    '10': 'P2P|getdata|wtxidrelay|inv|中继|邻居连接|交易通告',
    '11': '内存池|冲突替换|替换策略|入池|RBF',
    '12': '见证承诺|见证根|见证树|Merkle 路径|Merkle 树|Merkle 根|交易树根|包含证明|SPV',
    '13': '候选块|coinbase|区块补贴|补贴|减半|成熟期|区块重量|sigops',
    '14': '工作量证明|PoW|80 字节区块头|nBits|网络目标|难度调整|nonce',
    '15': 'Stratum V1|Stratum|extraNonce|额外 nonce|普通份额|份额目标|份额|模板构造|作业协调|控制器|ASIC',
    '15a': 'Bob 竞争出块|Bob 同时运营右侧的挖矿设施|Bob 的出块侧',
    '16': '累计工作量|最长链|共同祖先|重组|竞争分支|分支选择',
    '17': '逆序移除|逆序断块|断开旧块|断开 K|初始同步|活动链|区块索引|撤销记录|撤销数据|裁剪|断块通知|接块事件',
    '18': '区块时间戳|相对锁|绝对锁|nTime|MTP|nLockTime|锁定时间|时间锁|CLTV|CSV|软分叉|规则激活',
    '19': '聪|sat',
    '20': '独立钱包|全节点|钱包',
    '21': '区块奖励|奖励交易|挖矿激励|手续费'
  };
  const cardFor = new Map();
  for (const [id, aliases] of Object.entries(entries)) {
    for (const term of aliases.split('|')) cardFor.set(term.toLowerCase(), id);
  }
  // Aliases contain literal letters, digits, spaces, Chinese characters and hyphens.
  const alternatives = [...cardFor.keys()].sort((a, b) => b.length - a.length);
  const pattern = new RegExp(alternatives.join('|'), 'gi');
  const sections = document.querySelectorAll(
    'main > header, main > h1, .case, .readout, .panel, .detail, #walk, ' +
    '#arch, #alice, #bob, #module-detail, main > details, dialog'
  );
  function annotate(section) {
    const seen = new Set();
    const texts = [];
    const walker = document.createTreeWalker(section, NodeFilter.SHOW_TEXT);
    // Account for surviving links when a renderer replaces only part of a section.
    for (const a of section.querySelectorAll('a.btc-term')) {
      a.replaceWith(document.createTextNode(a.textContent));
    }
    section.normalize();
    walker.currentNode = section;
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.parentElement.closest('a,button,nav,summary,svg,script,style,template')) texts.push(node);
    }
    for (const node of texts) {
      const value = node.data;
      const fragment = document.createDocumentFragment();
      let end = 0;
      for (const match of value.matchAll(pattern)) {
        const term = match[0], key = term.toLowerCase(), at = match.index;
        if (seen.has(key)) continue;
        if (/^[a-z]/i.test(term) && /[a-z0-9_]/i.test(value.charAt(at-1))) continue;
        if (/[a-z0-9]$/i.test(term) && /[a-z0-9_]/i.test(value.charAt(at+term.length))) continue;
        seen.add(key);
        const link = document.createElement('a');
        const id = cardFor.get(key);
        const encodingTerm = ['compactsize','交易序列化','序列化'].includes(key);
        link.href = key === 'utxo' ? 'btc-utxo.html' : '知识卡片/阅读.html#card-' + (encodingTerm ? 'example-06' : id);
        link.target = '_blank';
        link.rel = 'noopener';
        link.className = 'btc-term';
        link.title = key === 'utxo' ? '打开 UTXO 专题（新标签页）' : '打开知识卡 ' + id + '（新标签页）';
        link.textContent = term;
        fragment.append(value.slice(end, at), link);
        end = at + term.length;
      }
      if (end) {
        fragment.append(value.slice(end));
        node.replaceWith(fragment);
      }
    }
  }
  for (const section of sections) {
    const options = {subtree:true, childList:true, characterData:true};
    const observer = new MutationObserver(() => {
      observer.disconnect();
      annotate(section);
      observer.observe(section, options);
    });
    annotate(section);
    observer.observe(section, options);
  }
})();
