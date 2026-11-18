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

## Optima CLI

The `optima` command turns a file of your tasks into a benchmark, runs the models you pick on it, and prints each model's score and cost. You can run it yourself, or a coding agent can run it for you.

### Install

```sh
curl -fsSL https://raw.githubusercontent.com/ArtificialAnalysis/optima/main/install-cli.sh | sh
```

The script downloads the CLI for macOS on Apple silicon, or for Linux on x86-64 or Arm, and checks it against the release's checksum. It installs `optima` in `~/.local/bin`, or in `$OPTIMA_INSTALL_DIR` if you set it. To update the CLI, run the same command again.

Artificial Analysis turns the CLI on for each organization.

### Sign in

```
$ optima login
Opening artificialanalysis.ai/connect in your browser
Signed in to Acme Inc as dana@example.com
```

In the browser, pick an organization and click Allow. If no browser can open, for example over SSH, run `optima login --no-browser`. Open the link that it prints in a browser on any computer, then paste the code that the page shows.

### Run a benchmark

```
$ optima create tickets.csv --name "Support triage"
Created 3b9e01c2 in Acme Inc · Support triage · 40 tasks · Rubric
Columns: Question → Prompt · Expected → Known answer · Notes not used
First task:
  Prompt        A customer writes that the order arrived damaged and asks what…
  Known answer  Offer a replacement and a prepaid return label.

$ optima launch 3b9e01c2 --model claude-opus-5-5 --model gemini-3-8-flash:high
Acme Inc · Support triage · 40 tasks · Rubric · 2 models
Available credit $85.00

  Generation          $10.90
  Grading              $1.50
  Estimated total     $12.40

Launch run for $12.40? [y/N] y
Run 8f2c1a0e launched · $12.40 held
Follow it in the web app:
https://artificialanalysis.ai/orgs/acme/optima/benchmarks/3b9e01c2-…/runs/8f2c1a0e-…
Follow it: optima watch 8f2c1a0e-4b7d-4e21-9c3a-5d6e7f8a9b0c

$ optima watch 8f2c1a0e
Acme Inc · Support triage · run 8f2c1a0e · Complete · 40 tasks · Rubric
Grading: Graded

Model                  Mean score  Cost / task  Total cost
claude-opus-5-5               82%        $0.19       $7.62
gemini-3-8-flash:high         74%        $0.07       $2.98

Used $11.95
https://artificialanalysis.ai/orgs/acme/optima/benchmarks/3b9e01c2-…/results/8f2c1a0e-…
```

- The file is a `.csv`, `.tsv`, `.json`, `.jsonl`, `.xlsx` or `.xlsm`. Each row needs a prompt, plus a known answer or answer criteria. Making a benchmark costs nothing.
- `optima models` lists the models you can pick and their effort levels. `gemini-3-8-flash:high` runs that model at high effort.
- A run spends your organization's credit, which you add in the web app. A launch sets the estimated total aside as a hold, and the run never spends more than the hold. If a run reaches its hold, Optima stops it and grades the answers that it has. When the run ends, Optima charges what it used and returns the rest.
- `watch` waits until the run ends and its grading finishes, then prints the results. Ctrl-C stops the wait, not the run.
- `optima --help` lists every command.

### For coding agents

Every command takes `--json`, and then prints one JSON object on stdout. With `--json`, `launch` never asks: it exits 3 with the estimate and the exact command to run once the person agrees.

### When a command fails

When a command fails because of an unexpected error, or because it could not finish its request to Optima, its last line is `Request ID: <id>`. Send that ID to your usual contact at Artificial Analysis, so they can find what the command sent.
