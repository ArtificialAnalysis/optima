# Optima skills

Agent skills for building custom benchmarks on the [Artificial Analysis Eval
Platform](https://artificialanalysis.ai/optima).

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/ArtificialAnalysis/optima/main/install.sh | sh
```

Installs into `~/.claude/skills/` and `~/.codex/skills/` — whichever exist,
Claude Code by default. Running `./install.sh` from a clone installs the
local copy instead of downloading.

Then ask your agent to "make an eval" and it will pick the skill up.

## Skills

| Skill | What it does |
| --- | --- |
| [`optima-eval-prep`](skills/optima-eval-prep/SKILL.md) | Turns the user's own work — a repo, a folder of documents or tickets, or the current conversation — into a staged source bundle: real task instances, ground-truth notes with evidence, and the documents behind them, packaged as a ZIP for the platform's **Describe your use case** screen. The platform's build agent designs the benchmark from it. |
