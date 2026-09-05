# dev_history — «Не в своём уме» (working codename redacted for publication)

Newest at the top. One entry per finished prompt (wrap-up only).

## 2026-09-05 — P3 · Review, polish, ship
**117 fixes applied across 26 chapter files, 6 bible files and the gate · gate GREEN · --cards GREEN · --selftest GREEN · 102 830 words · EPUB + A5 PDF built.**

Eight cold-read panels ran in parallel over the finished book (voice ×3 by chapter range, continuity, structure, fair-play, romance, humour) and returned **156 findings**. Every finding acted on was verified against the prose first, and that mattered: **four confident findings, including one graded blocker, were misreadings of deliberate work** — the leads' apparent gender slips in front of Oscar are the no-lying wave and are flagged on the page at ch19 («потому что сегодня фразы договаривали себя сами»); the ink that "migrates" to Hermione's forearm in ch32 is Bellatrix's carving, canon-exact; the "long legs" after the reversal are habit-bleed with the joke two clauses later; and two of the three citations under L1a-01 are correct by design. Dispositions for all 156 are logged in `Local/review/TRIAGE.md`: 117 applied, 12 rejected with reasons, the rest deferred to a named residual list.

What the review actually caught. **One frame break**: three places had British characters naming *Russian* as their working language (ch14, ch18, ch27) — the single sentence type that undoes a natively-written Russian book; all three now turn on register, not language. **Continuity**: the war at eight years instead of eleven; Draco held at twenty-eight for twenty-three chapters past his 5 June birthday; the lemon pie's Wednesdays at twenty-eight years against eleven; the ГАВНЭ pamphlet hidden in a drawer in ch30 and on an open shelf in ch33; ten teas counted as eleven; the wave-6 day counter a day short from ch25 on; and a six-week hole where the orphanage closes in October in Part II–III and on 31 August in Part IV. The spine held: all 33 dates match the real 2009 calendar, every named weekday is right, and the endgame night arithmetic reconciles from night 1 = 3/4 May to night 99 = 9/10 August. **Four refrains had become machinery** and were thinned, not purged: the staircase (15 → 10, keeping ch32's, where the stair that has announced children all book announces the two of them), «ровно столько, сколько» (17 → 10), «как читают опись» (4 → 1), «Волна пришла на решении» (5 → 2), plus «сказало её лицо» ten times in ch13 (→ 3). **Fair play**: the mystery is fair — 21 of 22 ledger rows clean — and the two majors were repaired for a clause each (Mrs Crabbe now locks up a shop in Draco's 1999 sighting, so her coin-reading no longer arrives inside its own reveal; the August determination now turns on the witness July left unnamed).

The one Tier-0 shortfall is logged rather than papered over. `plot-architecture.md` §5 carded **two** explicit scenes; the book has one. The ch32 scene was the right target and was deepened — «Дальше было тепло, тесно и неловко» is precisely the эвфемистический кисель §5 forbids, standing where the rule asks for warm and concrete — and now escalates in its own register, turning the swap's premise (he knows this body from the inside and not at all from here) from the threat it opens on into what it gives back. The second scene was not written: ch33's hard band leaves ~380 words and the only place it fits is after «Игла сошла к середине и пошла по пустому кругу», which is the book's best last line. **ADR-009** records the decision and the accepted deviation; §5 was amended so the bible stops promising what the book does not deliver. Three proximity beats were also tilted by one clause each to put *longing* into a band that had only tenderness.

Ship. `tools/build.ps1` adapted for Russian A5; `gate.py --assemble` now emits the four part divisions from `book/parts.txt`; `book/` given metadata, front matter, a colophon draft and a cover (`tools/make-cover.py` — a tango step chart, two tracks converging on one ember, rendered with Pillow at 2× and downsampled). The gate gained a check: two ASCII `"` were closing nested `„…“` invisibly, so a straight quote in prose is now an error, with a selftest case proving it fires. The toolchain had to be rebuilt from scratch — nothing survived on this machine — following the parent's ADR-010 exactly: pandoc 3.11 via winget, portable **tectonic 0.17** at `D:\tools\tectonic` so C: stays untouched. **EPUB 598 KB** (cover embedded, 42 nav entries, parts and chapters both listed) and **A5 PDF 378 pages** (ADR-011: the brief's 180–200 pages is arithmetically incompatible with its own 90–110k words; the word count wins). All 33 chapters moved `status: draft → final`.

Residual, ranked, for a possible P4: the OBSERVERS engine goes off-page after ch5 and three of the eight running jokes stop running (~1 200 words across four chapters — the biggest single gain still available); ch23 wants a redraft, being the one chapter whose scheduled event happens behind a closed door; the recusal's public cost is chosen but never staged. **ADR-010** records that P3 triaged rather than obeyed. Model-fit: orchestration at frontier/high, eight panels at frontier/high in parallel (~3.1 M subagent tokens) → **fit**; the verification-before-action discipline is what made the panels safe to use.

## 2026-09-04 — P2 · The whole book written
**33/33 chapters, 102 825 words (gate count), ledger closed 22/22, gate GREEN · --cards GREEN · --selftest GREEN.** Four band warnings (ch18, ch25, ch32, ch33), all inside the hard 2400–3800 corridor.

Drafted per the P2 shape: chapters strictly in order, one draft agent per chapter fed the card + style guide + bible extracts + the previous chapter + the rolling `Local/story-state.md`, then gate → card-fidelity check → deepen in-run → bible/ledger/story-state/run-log written in the same prompt. Set pieces at max, the rest at high. Full per-chapter record in `Local/P2-run-log.md`.

The run spanned two machines: ch01–ch19 (5 Aug) and ch20–ch23 (1 Sep) were drafted before the migration to the desktop; ch24–ch33 (4 Sep) after it. **The reopening found the migration had left ch23 drafted but unbooked** — no run-log row, no story-state roll — and, in the course of closing it, **a real continuity defect**: ch23 (16 July) had copied ch22's «девятый день» for wave 6 four days later, when the correct count from 4 July is the thirteenth. Fixed in prose, then booked.

Two working-note corrections worth recording. **(1)** The chapter grid's `status: planned` on every row is not staleness but the frozen-card convention — the live tracker is the run log; nothing there needed touching. **(2)** The story-state constraint «no character has said the name Crabbe before ch32» was simply wrong: it contradicted the frozen ch29 card, which is titled «Пенсия миссис Крэбб». Corrected in-run — the name is on the page from ch29, and what P6 actually held back to ch32 is the inference that she always knew, and knew by the coinage («Министерство не платит галлеонами чеканки девяносто седьмого года»).

Bible grew from IC-096 to **IC-158** in-run, including the law of wave 8 («the wave takes the DECISION, not the deed», with children's immunity proved to run both ways) written into `world-rules.md` §2. The 9/10 August deadline was derived on the page from the rite's own count and not the waves' — eleven circles × nine nights = 99, night one 3/4 May — and verified independently to the day.

ADR-007 logs the one deliberate deviation from the frozen grid (first intimacy at the head of ch32); ADR-008 gives the book its own local repository. Model-fit: set pieces at frontier/max via draft agents, the rest at frontier/high; ch24 written inline at high before the agent-per-chapter workflow was resumed at the author's prompt — **fit**, and the agent-per-chapter shape is what held the last nine chapters' continuity.

## 2026-08-05 — P1 · Concept & skeleton
Multi-agent concept tournament (4 non-converging authors: comedy / mystery / family /
genre-savvy; 3 judge lenses: brief-fidelity / commissioning-reader / emotional-core+fair-play;
7 agents, all returned). Winner: comedy architecture «Не в своём уме» (totals 266·263·259·249);
9 grafts adopted + 6 risk mitigations — full record `Local/scratch/P1-panel/synthesis.md`.
Bible written: characters (leads with want/wound/lie/costs, Оскар Данн + Тилли Крофт, circles),
world-rules (rite law, 9 anomaly waves mapped to romance rungs, guardrail "magic only ratifies"),
plot-architecture (4 parts, 3 comedy machines, 8 running jokes, 5 set pieces, intimacy
architecture), timeline (2 May – 29 Aug 2009), foreshadowing-ledger (21 rows), chapter-grid
(33 cards, target sum 102,200 in 90–110k band), glossary (Rosman law + plot lexicon),
style-guide (Russian, binding, machine sections 8.1–8.4), invented-canon (16 rows). Tooling:
`tools/gate.py` — Russian-aware gate (front-matter, bands, card-mirror, ledger sync, forbidden
lexicon, tics, said-bookisms, quote-speech, Latin leak, timeline; --cards, --selftest,
--assemble) — selftest green, cards green. Three Russian voice probes green against the guide.
ADR-005 premise lock, ADR-006 repo placement. Model-fit: used frontier/high (+7 subagents) →
fit.

## 2026-08-04 — P0 · Project founded (scaffold)
Directory the project directory created inside the Fun Fic repo with the classic structure: `CLAUDE.md`,
`docs/adr.md` (ADR-001…004), `Local/` (brief verbatim, bootstrap, 3-prompt plan, prompt standard),
empty `bible/` + `manuscript/` to be filled by P1/P2. the commissioning brief captured verbatim as the
binding product spec; three-prompt plan of record locked (concept → full multi-agent draft →
review/polish/ship). No prose written. Model-fit: used frontier/high → fit.
