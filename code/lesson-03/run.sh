#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d /opt/homebrew/opt/openssl@3/lib/pkgconfig ]]; then
 export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
command -v pkg-config >/dev/null || { echo 'Requires pkg-config and OpenSSL development headers'; exit 1; }
pkg-config --atleast-version=3.0 openssl
BUILD="$HERE/../build/lesson-03"
mkdir -p "$BUILD"
# pkg-config output consists of compiler/linker flags, intentionally split.
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror -O2 ${EXTRA_CXXFLAGS:-} $(pkg-config --cflags openssl) "$HERE/ledger.cpp" "$HERE/lab03.cpp" -o "$BUILD/lab03" $(pkg-config --libs openssl)
"$BUILD/lab03"
