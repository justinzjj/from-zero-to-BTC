#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d /opt/homebrew/opt/openssl@3/lib/pkgconfig ]]; then
  export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fi
pkg-config --atleast-version=3.0 openssl
BUILD="$HERE/../build/lesson-02"
mkdir -p "$BUILD"
"${CXX:-c++}" -std=c++17 -Wall -Wextra -Werror -O2 ${EXTRA_CXXFLAGS:-} \
  $(pkg-config --cflags openssl) "$HERE/openssl_student.cpp" \
  -o "$BUILD/openssl_student" $(pkg-config --libs openssl)
"$BUILD/openssl_student"
