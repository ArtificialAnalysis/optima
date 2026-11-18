#!/bin/sh
# Install the Optima CLI from the latest release of this repo.
#
#   curl -fsSL https://raw.githubusercontent.com/ArtificialAnalysis/optima/main/install-cli.sh | sh
#
# Installs to ~/.local/bin, or to $OPTIMA_INSTALL_DIR. Run it again to update.
set -eu

RELEASE_URL="https://github.com/ArtificialAnalysis/optima/releases/latest/download"
INSTALL_DIR="${OPTIMA_INSTALL_DIR:-$HOME/.local/bin}"

fail() {
  echo "Optima CLI not installed: $1" >&2
  exit 1
}

case "$(uname -s)/$(uname -m)" in
  Darwin/arm64) target="aarch64-apple-darwin" ;;
  Darwin/x86_64)
    # A Rosetta shell on Apple silicon reports x86_64.
    if [ "$(sysctl -n sysctl.proc_translated 2>/dev/null || true)" = "1" ]; then
      target="aarch64-apple-darwin"
    else
      fail "there is no build for Intel Macs."
    fi
    ;;
  Linux/x86_64 | Linux/amd64) target="x86_64-unknown-linux-musl" ;;
  Linux/aarch64 | Linux/arm64) target="aarch64-unknown-linux-musl" ;;
  *) fail "there is no build for $(uname -s) on $(uname -m)." ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "$RELEASE_URL/optima-$target" -o "$tmp/optima" || fail "the download of optima-$target failed."
curl -fsSL "$RELEASE_URL/SHA256SUMS" -o "$tmp/SHA256SUMS" || fail "the download of SHA256SUMS failed."

expected="$(awk -v name="optima-$target" '$2 == name { print $1 }' "$tmp/SHA256SUMS")"
if command -v sha256sum >/dev/null 2>&1; then
  actual="$(sha256sum "$tmp/optima" | cut -d ' ' -f 1)"
elif command -v shasum >/dev/null 2>&1; then
  actual="$(shasum -a 256 "$tmp/optima" | cut -d ' ' -f 1)"
else
  fail "this computer has no sha256sum or shasum to check the download."
fi
[ -n "$expected" ] || fail "SHA256SUMS has no checksum for optima-$target."
[ "$actual" = "$expected" ] || fail "optima-$target does not match its checksum in SHA256SUMS."

chmod +x "$tmp/optima"
version="$("$tmp/optima" --version)" || fail "optima-$target does not run on this computer."

mkdir -p "$INSTALL_DIR" || fail "cannot write to $INSTALL_DIR."
# Rename within the folder, so a running optima is never overwritten in place.
cp "$tmp/optima" "$INSTALL_DIR/.optima.new" || fail "cannot write to $INSTALL_DIR."
mv -f "$INSTALL_DIR/.optima.new" "$INSTALL_DIR/optima" || fail "cannot write to $INSTALL_DIR."

echo "Installed $version to $INSTALL_DIR/optima"
login="optima login"
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *)
    login="$INSTALL_DIR/optima login"
    echo ""
    echo "$INSTALL_DIR is not on your PATH. Add this line to your shell's startup file, such as ~/.zshrc or ~/.bashrc:"
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    ;;
esac
echo ""
echo "Then sign in: $login"
