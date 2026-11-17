#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d /opt/homebrew/opt/openssl@3/lib/pkgconfig ]]; then
 export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
command -v pkg-config >/dev/null || { echo 'Requires pkg-config and OpenSSL development headers'; exit 1; }
pkg-config --atleast-version=3.0 openssl
BUILD="$HERE/../build/lesson-02"
mkdir -p "$BUILD"
# pkg-config output consists of compiler/linker flags, intentionally split.
FOUNDATIONS="$HERE/../lesson-01"
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror -O2 ${EXTRA_CXXFLAGS:-} -I"$FOUNDATIONS" $(pkg-config --cflags openssl) "$HERE/lab02.cpp" -o "$BUILD/lab02" $(pkg-config --libs openssl)
"$BUILD/lab02"
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror "$HERE/toy_curve.cpp" -o "$BUILD/toy_curve"
"$BUILD/toy_curve"
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror "$HERE/toy_curve_test.cpp" -o "$BUILD/toy_curve_test"
"$BUILD/toy_curve_test"
