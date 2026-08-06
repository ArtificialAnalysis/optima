#!/bin/sh
# Install the Optima eval skill into your coding agent's skills
# directory (Claude Code and/or Codex; defaults to Claude Code).
#
#   curl -fsSL https://raw.githubusercontent.com/ArtificialAnalysis/optima/main/install.sh | sh
#
# Run from a clone of this repo and it installs the local copy instead.
set -e

BASE_URL="${AA_SKILL_BASE_URL:-https://raw.githubusercontent.com/ArtificialAnalysis/optima/main/skills/optima-eval-prep}"
SKILL_NAME="optima-eval-prep"

# Where this script lives, if it was run from a clone rather than piped to sh.
SRC_DIR=""
case "$0" in
  */*) candidate="$(cd "$(dirname "$0")" && pwd)/skills/$SKILL_NAME" ;;
  *) candidate="" ;;
esac
[ -n "$candidate" ] && [ -f "$candidate/SKILL.md" ] && SRC_DIR="$candidate"

install_into() {
  mkdir -p "$1/$SKILL_NAME/scripts"
  if [ -n "$SRC_DIR" ]; then
    cp "$SRC_DIR/SKILL.md" "$1/$SKILL_NAME/SKILL.md"
    cp "$SRC_DIR/scripts/check_bundle.py" "$1/$SKILL_NAME/scripts/check_bundle.py"
  else
    curl -fsSL "$BASE_URL/SKILL.md" -o "$1/$SKILL_NAME/SKILL.md"
    curl -fsSL "$BASE_URL/scripts/check_bundle.py" -o "$1/$SKILL_NAME/scripts/check_bundle.py"
  fi
  installed="$installed
  $1/$SKILL_NAME"
}

installed=""
for dir in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  if [ -d "$(dirname "$dir")" ]; then
    install_into "$dir"
  fi
done

if [ -z "$installed" ]; then
  install_into "$HOME/.claude/skills"
fi

echo "Installed the Optima eval skill:$installed"
echo ""
echo "The skill starts by asking what your eval should measure."
