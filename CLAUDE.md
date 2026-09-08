# CLAUDE.md — «Не в своём уме» (working codename redacted; final title locked in P1)

A ~90–110k-word **Dramione romantic comedy** (30–35 chapters, 180–200 printed pages) set in the
post-war Harry Potter universe (2009, eleven years after the Battle of Hogwarts). Fan fiction:
canon world and canon characters, original plot. Written **natively in RUSSIAN** (ROSMAN lexicon).
Written to a private commission; the brief is the binding product spec: `Local/brief.md`.

**Scope note:** this is a subproject inside the Fun Fic repository. Within this directory, THIS file
overrides the parent `CLAUDE.md` (which governs *Unplottable*). Parent hard rules that remain in
force here: C: drive forbidden · `Local/` never committed · commits only at wrap-up, scoped ·
bible-first · ledger discipline · gate green before commit.

**Division of labour:** all content decisions (cast gaps, chapter turns, sentences) belong to the
assistant within the rails of the commissioning brief; method, scope and pacing belong to the author.
**Never ask content questions**; decide, log the decision, move on.

## Read first, every session
1. `Local/bootstrap.md` (current state, next step) → then `Local/brief.md` +
   the relevant `bible/` sections for the prompt at hand.

## Plan of record — THREE prompts, no more
- **P1 · Concept & skeleton** — bible, plot architecture, chapter grid, ledger, style guide (RU), gate.
- **P2 · Write the whole book** — multi-agent drafting per chapter card, gate inside the run.
- **P3 · Review, polish, finalize** — review panels, edit passes, typeset EPUB/MOBI/A5 PDF.
Details: `Local/all prompts.md` · standard: `Local/Prompts requirements.md`.

## Hard rules
- **Language: RUSSIAN prose** — written natively, never translated. ROSMAN terminology for all HP
  names/spells/places, consistent throughout (glossary: `bible/glossary.md`). Repo docs and chat
  stay English/Czech as usual; Russian is confined to `manuscript/` and prose-bearing bible fields.
- **Canon tiers:** HP books 1–7 binding · post-book divergences allowed only where the commissioning brief
  requires them, each logged in `bible/invented-canon.md` · no Cursed Child.
- **Brief is binding (Tier-0 for content):** genre (romcom, slow burn, 18+), the fixed plot spine
  (gala 2 May 2009 · two foster children · mistranslated ancient ritual · body swap · escalating
  identity anomalies · no traditional villain · Argentine-tango final scene), character cores of
  Draco/Hermione incl. their false beliefs, romance progression order, humor/drama/intimacy
  balance (~60–70 % inner life · 20–35 % tension/affection · ~10 % explicit), scene/dialogue/
  anti-AI craft rules. Deviations from the brief only with a logged ADR reason.
- **Bible-first:** no fact in prose without a `bible/` home, logged in the SAME prompt.
- **Ledger discipline:** twists/plants/payoffs only via `bible/foreshadowing-ledger.md`;
  front-matter `plants:`/`payoffs:` stay in sync. The ledger is OPEN (new book).
- **Story rails:** magic never solves emotional problems · children immune to the anomalies ·
  anomalies start funny, turn threatening · no artificial separations/misunderstanding drama ·
  ending constructive (the tango). Era-tech and world facts stay 2009-plausible.
- **`Local/` never committed**; commits only at wrap-up ("X is done" authorizes); scoped adds.
- Docs (`docs/`, bootstrap) change only at wrap-up, never mid-prompt.

## Conventions
- Chapters: `manuscript/chNN-slug.md` with YAML front-matter
  `chapter, title, pov, date_in_story, target_words, plants, payoffs, status`.
  Bands: target 2.7–3.4k, hard 2.4–3.8k words (35 chapters ≈ 108k).
- POV: close 3rd past, one head per scene, dual leads (Draco/Hermione alternating; grid decides).
- Registers per `bible/style-guide.md` (authored in Russian, IS the gate's config).
- Probes/experiments → `Local/scratch/` only, never committed, never reused verbatim.

## Run commands (scaffolded in P1)
- Quality gate: `python tools\gate.py` (green required before any commit)
- Build EPUB/MOBI/A5 PDF: adapted from parent `tools/build.ps1` in P3.

## Workflow
Same loop as the parent project: "let's start «X»" → just-in-time refine + plan → OK → execute with
verification DURING → "«X» is done" → lean wrap-up (gate, ADR, dev_history, bootstrap head ≤5×5,
model-fit line, scoped commit). Announce every next prompt with its tier + `▶ Run on: <tier> · <effort>`.
