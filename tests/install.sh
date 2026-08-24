#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/optima-install-test.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

cp -R "$repo" "$tmp/repo"
printf '\nLOCAL_CLONE_SENTINEL\n' >> "$tmp/repo/skills/optima-eval-prep/SKILL.md"
mkdir -p "$tmp/local-home"
(
  cd "$tmp/repo"
  HOME="$tmp/local-home" sh install.sh >/dev/null
)
grep -q LOCAL_CLONE_SENTINEL "$tmp/local-home/.claude/skills/optima-eval-prep/SKILL.md"
cmp "$tmp/repo/skills/optima-eval-prep/scripts/check_bundle.py" \
  "$tmp/local-home/.claude/skills/optima-eval-prep/scripts/check_bundle.py"
printf 'PASS: sh install.sh uses local clone files\n'

mkdir -p "$tmp/bin" "$tmp/piped-home"
cat > "$tmp/bin/curl" <<'EOF'
#!/bin/sh
set -eu
output=""
url=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o) output="$2"; shift 2 ;;
    -*) shift ;;
    *) url="$1"; shift ;;
  esac
done
case "$url" in
  */SKILL.md) printf 'REMOTE_SKILL_SENTINEL\n' > "$output" ;;
  */scripts/check_bundle.py) printf 'REMOTE_SCRIPT_SENTINEL\n' > "$output" ;;
  *) exit 2 ;;
esac
EOF
chmod +x "$tmp/bin/curl"
(
  cd "$tmp/repo"
  : > sh
  cat install.sh | HOME="$tmp/piped-home" PATH="$tmp/bin:$PATH" sh >/dev/null
)
grep -q REMOTE_SKILL_SENTINEL "$tmp/piped-home/.claude/skills/optima-eval-prep/SKILL.md"
grep -q REMOTE_SCRIPT_SENTINEL \
  "$tmp/piped-home/.claude/skills/optima-eval-prep/scripts/check_bundle.py"
test -x "$tmp/piped-home/.claude/skills/optima-eval-prep/scripts/check_bundle.py"
printf 'PASS: cat install.sh | sh installs executable remote files\n'

sh -n "$repo/install.sh"
printf 'PASS: install.sh has valid POSIX shell syntax\n'
