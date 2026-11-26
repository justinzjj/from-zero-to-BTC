#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d /opt/homebrew/opt/openssl@3/lib/pkgconfig ]]; then
  export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
pkg-config --atleast-version=3.0 openssl
BUILD="$HERE/../build/lesson-02"
mkdir -p "$BUILD"
# pkg-config返回编译/链接参数，按参数列表展开。
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror -O2 ${EXTRA_CXXFLAGS:-} \
  -I"$HERE/../lesson-01" $(pkg-config --cflags openssl) \
  "$HERE/simple_ecdsa.cpp" -o "$BUILD/simple_ecdsa" $(pkg-config --libs openssl)
"$BUILD/simple_ecdsa"
