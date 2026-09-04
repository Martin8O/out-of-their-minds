# dev_history — «Не в своём уме» (working codename redacted for publication)

Newest at the top. One entry per finished prompt (wrap-up only).

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
