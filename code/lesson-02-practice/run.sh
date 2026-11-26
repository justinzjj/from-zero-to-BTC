#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d /opt/homebrew/opt/openssl@3/lib/pkgconfig ]]; then
  export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
command -v pkg-config >/dev/null || { echo '需要 pkg-config 和 OpenSSL 3 开发文件'; exit 1; }
pkg-config --atleast-version=3.0 openssl
BUILD="$HERE/../build/lesson-02-practice"
mkdir -p "$BUILD"
CHOICE="${1:-all}"
case "$CHOICE" in
  all) FILES=(01_hash 02_key_and_public 03_sign 04_verify 05_payment) ;;
  01|1) FILES=(01_hash) ;;
  02|2) FILES=(02_key_and_public) ;;
  03|3) FILES=(03_sign) ;;
  04|4) FILES=(04_verify) ;;
  05|5) FILES=(05_payment) ;;
  *) echo '用法：bash run.sh [all|01|02|03|04|05]'; exit 2 ;;
esac
for NAME in "${FILES[@]}"; do
  echo "编译运行：$NAME"
  # pkg-config返回多个编译和链接参数，此处按参数展开。
  "${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror -O2 ${EXTRA_CXXFLAGS:-} \
    $(pkg-config --cflags openssl) "$HERE/$NAME.cpp" -o "$BUILD/$NAME" \
    $(pkg-config --libs openssl)
  "$BUILD/$NAME"
done
