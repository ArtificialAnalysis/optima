---
name: optima-eval-prep
description: Make a custom Optima (Artificial Analysis) benchmark from the user's own work. Stage real task instances, ground-truth notes, and the documents behind them, write the brief, and package a ZIP the user drops on the platform's upload screen. Use when the user says "make an eval", "build an eval", "prep an eval", "get an eval ready", "make a benchmark from my codebase / docs / tickets / this chat", or "which model is best at [our task]".
metadata:
  author: Artificial Analysis
  version: '1.1'
---

# Optima eval prep

Use when the user wants a custom Optima benchmark built from their own
work. You stage the material; the platform's build agent designs the
benchmark. The hand-off is one ZIP and nothing else: the user drops it on
the upload screen and presses Continue. The brief travels inside the
archive and the evaluation type is stamped on it, so there is nothing to
type, paste or pick on the site.

## Rules

- If the request names no subject (the standard install line doesn't), ask
  one question first and nothing else. You are usually already in the
  user's repo, so offer it as an option instead of asking to be pointed at
  one. When this conversation contains real work, name it and offer it as
  the default:
  `Want the eval built from what we've done in this chat (<the actual
  work>)? Or I can build it from this repo, from a folder of documents or
  tickets you point me at, or from a use case you describe.`
  In a fresh session: `What should this eval measure? I can build it from
  this repo, from a folder of documents or tickets you point me at, or from
  a use case you describe.`
- You do not finalize the benchmark. Task count, task wording, scoring
  levels, and weights are the build agent's call, so do not over-specify
  either in the brief.
- Give the build agent concrete material: real instances paired with the
  outputs that were accepted, established answers with their evidence, and
  the mistakes people actually make. It can only be as specific as what you
  give it.
- Never upload on the user's behalf. Never commit the bundle into a repo.
- Everything in the ZIP is uploaded. Replace confidential documents with
  generated stand-ins that keep the real structure, field names, length,
  and messiness, and declare them in the manifest.

## What the grader can check

The grader reads the answer; it never runs it, so a use case only works if a
fixed right answer can be verified by reading — check this before staging
anything, and if a use case fails, say so and propose the nearest gradeable
reformulation. Two things fail it. Anything graded by execution — "passes the
test suite", "returns the right rows" — has to be restated toward what reading
can verify, with a note on what is no longer measured; and anything needing
bespoke tools or systems, like an internal API or database, has to be restated
around supplied files. 

The web is available if the user turns it on: agentic runs have a Web search
switch ("Let the agent look things up while it works"), off by default and
agentic-only, so a task may depend on looking something up as long as the
*right answer* is still fixed — "summarise this company's latest filing" is
fine when you attach the filing and grade against it, whereas "what is the
share price today" is not gradeable at all, because the answer moves
regardless of who can browse. Long agentic work is likewise fine: runs get a
generous per-task turn budget, so multi-step work that produces a file is a
normal task, not an edge case.

## Intake

Pin down:

1. The work: what the org does, and the one repeating task worth measuring.
2. The inputs: what a real instance arrives with, in which formats, roughly
   how long.
3. Good vs bad in the user's words, as concrete observations ("reviewers
   reject answers that miss the auto-renewal clause"). These become rubric
   criteria, so prefer specific and evidenced over general.
4. The answer shape: a short written answer, a filled document, a label
   from a fixed set (get the exact set), or a produced file.
5. Categories: the 2+ meaningfully different kinds of this work.
6. Scale and confidentiality: how many tasks, and which material cannot be
   uploaded as-is.
7. The evaluation type, agreed with the user. `agentic` whenever any task's
   required output is anything other than plain text typed in a reply: a
   spreadsheet, a document, a slide deck, code files, any produced file.
   `document_input` only when every answer is plain text about attached
   files; `qa` only when every answer is plain text with no attached
   inputs. When in doubt, `agentic`. The type is stamped into the archive
   at packaging, so the user never picks it on the site.

When working from a repo or chat: name the repeating unit of work ("review
one pull request", not "do what this conversation did"). Find more
instances of that unit in history and files; each becomes a task. Follow-up
fixes are especially useful: each points at the change that introduced the
defect, so it gives you an instance and its correct answer together.
Include instances where the right answer is "nothing to report"; without
clean inputs the benchmark cannot penalize invented findings.

## Stage the sources

- Use real files where possible. Redact rather than fabricate when
  redaction is enough.
- Generate stand-ins for what cannot go. Write the actual file with code;
  never name a file you did not create. Keep the stand-in as long and messy
  as the real thing.
- Every filename says what the file is: `supplier_contract_signed_2024.pdf`,
  not `doc1.pdf`.
- Group into folders by kind: `contracts/`, `claims/`, `examples/`. Archive
  paths are preserved in what the build agent reads.
- Put worked examples in `examples/`: a past input paired with the output a
  senior person actually produced.
- Put outcome evidence in its own folder: follow-up fixes, post-mortems,
  reviewer rejections. These record what the right answer turned out to be
  without being answers themselves. Say in the manifest what each item is
  evidence of.
- Do the task yourself where the answer is checkable: compute the figure,
  find the clause, assign the label. Record the result in `02_TASK_SEEDS.md`
  with its evidence.

## Root documents

Three files at the ZIP root. Numeric prefixes make them sort, and get read,
first.

`00_BRIEF.md` describes the work, not the benchmark. Drop empty sections
rather than padding them:

```markdown
# <What the org does, in a sentence>

## The task we want measured
<The repeating job: what arrives, what has to come out, what makes it hard.>

## What's attached
<The archive at folder level: what is real, redacted, or generated, and why.>

## What a good answer looks like
<Concrete and evidenced, in the org's own words.>

## What a weak answer looks like
<Mistakes actually seen. "Misses the auto-renewal clause because it sits
under Termination" beats "incomplete analysis".>

## How this work divides
<The categories.>

## The shape of an answer
<Written answer / filled document / label from the exact fixed set / file.>

## Scale
<How many tasks.>

## Over to you
Design the benchmark as you see fit. Task count, wording, and grading are
your call. Show me the plan before you build it.
```

Keep the closing section; it hands design authority to the build agent.

`01_SOURCES.md` is the manifest. One entry per file: path, what it is,
provenance (real, redacted, or generated), and what to notice about it.
Where a file establishes a right answer, cross-reference its entry in
`02_TASK_SEEDS.md`.

`02_TASK_SEEDS.md` has one entry per candidate instance of the work:

- input files (archive paths);
- the established answer or accepted output, or a pointer into `examples/`;
- the evidence, quoted or located exactly: `adjusted balance is $842,317.44
  (Reconciliation!D48 in claims/ledger_q4.xlsx)`;
- wrong answers seen, or plausible near-misses worth penalizing.

State facts with evidence, not scoring scales. Include the clean instances
where the right answer is "nothing to report".

## Package and check

Build the archive with Python's `zipfile` in write mode, skipping dotfiles,
and stamp the evaluation type and the benchmark's display name into the
archive comment. The upload screen reads the comment, names the benchmark,
and starts the build agent with that type:

```python
with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
    ...
    # eval_type: qa / document_input / agentic. name: a short title for the
    # work being measured, a few words, and it must come last.
    archive.comment = b"optima eval_type=agentic name=Invoice Reconciliation"
```

Write mode replaces any existing archive cleanly; shell `zip -r` updates an
existing file in place and keeps stale members from earlier attempts, so
avoid it.

Before hand-off run the checker installed next to this file:

`python <this skill's directory>/scripts/check_bundle.py <path-to-zip>`

Before hand-off confirm: every filename self-describing; provenance stated
for every file; nothing confidential the user has not cleared; every known
answer in `02_TASK_SEEDS.md` with evidence; every input the brief names is
in the archive, or the brief says the task was restated without it.

## Hand off

The ZIP carries everything, including the brief. The user only drops it;
there is nothing to type or paste.

Do these yourself (`open` on macOS, `xdg-open` on Linux, `start` on
Windows), and say what you did:

1. Reveal the ZIP: `open -R <zip>` on macOS; elsewhere open its folder.
2. Open the upload page. The original request usually carries it ("My
   Optima upload page: <url>"); open that exact URL. Without one, open
   `https://artificialanalysis.ai/optima/upload`. Both redirect through
   sign-in to the screen the ZIP is dropped on.

End your final message with exactly this list:

1. The tab that just opened is the upload screen. Sign in if prompted.
2. Drag the ZIP from the window that just opened onto it, or use **Choose
   file**. Continue starts the build agent on the bundle.
3. The build agent reads it, asks what it still needs, and proposes a plan
   (task count, categories, grading) for your approval before building.
   You can redirect it in that chat at any point.
4. <2 or 3 checks specific to this bundle: outcome evidence used for
   grading rather than handed out as task material; clean instances kept as
   false-positive controls; anything generated, trimmed, or deliberately
   left in.>
