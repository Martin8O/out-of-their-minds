#!/usr/bin/env python3
"""the book - the quality gate (P1).

One command, standard library only:

    python tools\\gate.py                 full run over manuscript/ against bible/
    python tools\\gate.py --cards         audit bible/chapter-grid.md itself
    python tools\\gate.py --selftest      prove every check fires on seeded bad input
    python tools\\gate.py --assemble F    write one book-shaped markdown file to F
    python tools\\gate.py PATH [PATH...]  check only these chapter files

Spec: `bible/style-guide.md` sections 7-9 (front-matter schema, enforced lists,
thresholds).  The style guide is PARSED at run time: the enforced lists in
section 8 are never copied into this file, so extending a list in the guide
extends the gate.  Section 9's numbers live in THRESHOLDS below, quoted from
the guide.

Russian-specific checks (vs. the parent Unplottable gate): Cyrillic word
count; em-dash dialogue convention (quote-mark speech is an error); forbidden
Spivak/Makhaon lexicon; Latin-script leak detection; Russian said-bookism
tags; banned AI-tics list in Russian.

Exit: 0 green (warnings allowed) - 1 hard violations - 2 gate could not run.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:  # keep Cyrillic printable in a Windows console
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parent.parent          # 
MANUSCRIPT = ROOT / "manuscript"
BIBLE = ROOT / "bible"
STYLE_GUIDE = BIBLE / "style-guide.md"
GRID = BIBLE / "chapter-grid.md"
LEDGER = BIBLE / "foreshadowing-ledger.md"

FM_KEYS = ["chapter", "title", "pov", "date_in_story",
           "target_words", "plants", "payoffs", "status"]
POVS = ["draco", "hermione", "oscar", "tilly", "other"]
STATUSES = ["stub", "draft", "revised", "final", "probe"]

THRESHOLDS = {
    "chapter_hard": (2400, 3800),     # style-guide 9: hard band
    "chapter_target": (2700, 3400),   # target band -> warn outside
    "book_band": (90000, 110000),     # brief: 90-110k words
    "latin_leak_warn": 3,             # non-whitelisted Latin tokens per chapter
}

WORD_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+(?:-[А-Яа-яЁёA-Za-z]+)*")
LATIN_RE = re.compile(r"\b[A-Za-z]{2,}\b")
CH_FILE_RE = re.compile(r"^ch(\d{2})-[a-z0-9-]+\.md$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STRAIGHT_QUOTE_SPEECH = re.compile(r'^\s*["“„][А-ЯЁ]')  # "Речь or “Речь or „Речь
TAG_VERB_RE_TMPL = r",\s*[—-]\s*(?:%s)\b"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def dump(self) -> int:
        for w in self.warnings:
            print(f"  WARN  {w}")
        for e in self.errors:
            print(f"  FAIL  {e}")
        if self.errors:
            print(f"\nGATE: RED - {len(self.errors)} hard violation(s), "
                  f"{len(self.warnings)} warning(s)")
            return 1
        print(f"\nGATE: GREEN - 0 hard violations, {len(self.warnings)} warning(s)")
        return 0


# --------------------------------------------------------------------------
# style-guide section-8 list parsing
# --------------------------------------------------------------------------

def parse_guide_lists(text: str) -> dict[str, list[str]]:
    """Parse `### 8.N <name>` subsections into named bullet lists.

    Bullet format: `- item` or `- item → replacement` (item = text before →).
    Returns keys: forbidden_lexicon, banned_tics, said_bookisms, latin_whitelist.
    """
    keymap = {
        "8.1": "forbidden_lexicon",
        "8.2": "banned_tics",
        "8.3": "said_bookisms",
        "8.4": "latin_whitelist",
    }
    lists: dict[str, list[str]] = {v: [] for v in keymap.values()}
    current: str | None = None
    for line in text.splitlines():
        m = re.match(r"^###\s+(8\.\d)\b", line)
        if m:
            current = keymap.get(m.group(1))
            continue
        if re.match(r"^#{1,3}\s", line):
            current = None
            continue
        if current and line.strip().startswith("- "):
            item = line.strip()[2:]
            item = item.split("→")[0].split("(")[0].strip().strip("*`")
            if item:
                lists[current].append(item)
    return lists


def load_guide() -> dict[str, list[str]]:
    if not STYLE_GUIDE.exists():
        print(f"gate: cannot run - missing {STYLE_GUIDE}")
        sys.exit(2)
    return parse_guide_lists(STYLE_GUIDE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# front matter / text plumbing
# --------------------------------------------------------------------------

def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    meta: dict[str, str] = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 4:]


def parse_id_list(raw: str) -> list[str]:
    raw = raw.strip().strip("[]")
    return [p.strip() for p in raw.split(",") if p.strip()]


def word_count(body: str) -> int:
    return len(WORD_RE.findall(body))


def narration_lines(body: str):
    """Prose minus artefact blocks (blockquotes) and headings."""
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(">") or s.startswith("#"):
            continue
        yield line


# --------------------------------------------------------------------------
# bible tables
# --------------------------------------------------------------------------

def parse_table(path: Path, min_cols: int) -> list[list[str]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < min_cols or set(cells[0]) <= set("-: ") or not cells[0]:
            continue
        rows.append(cells)
    return rows


def load_grid() -> dict[int, dict[str, str]]:
    """chapter-grid.md rows: | ch | title | pov | date | target | plants | payoffs | intent | hook | status |"""
    grid: dict[int, dict[str, str]] = {}
    for cells in parse_table(GRID, 10):
        if not cells[0].isdigit():
            continue
        grid[int(cells[0])] = {
            "title": cells[1], "pov": cells[2], "date": cells[3],
            "target": cells[4], "plants": cells[5], "payoffs": cells[6],
            "intent": cells[7], "hook": cells[8], "status": cells[9],
        }
    return grid


def load_ledger() -> dict[str, dict[str, str]]:
    """foreshadowing-ledger.md rows: | id | name | plant ch | payoff ch | status |"""
    ledger: dict[str, dict[str, str]] = {}
    for cells in parse_table(LEDGER, 5):
        rid = cells[0].strip("*` ")
        if not re.match(r"^[A-Za-z]+\d+$", rid):
            continue
        ledger[rid] = {"name": cells[1], "plant": cells[2],
                       "payoff": cells[3], "status": cells[4]}
    return ledger


# --------------------------------------------------------------------------
# per-chapter checks
# --------------------------------------------------------------------------

def check_chapter(path_name: str, text: str, guide: dict[str, list[str]],
                  grid: dict[int, dict[str, str]], rep: Report) -> dict:
    meta, body = split_front_matter(text)
    tag = path_name

    for key in FM_KEYS:
        if key not in meta:
            rep.err(f"{tag}: front-matter missing key '{key}'")
    status = meta.get("status", "")
    if status and status not in STATUSES:
        rep.err(f"{tag}: unknown status '{status}'")
    pov = meta.get("pov", "")
    if pov and pov not in POVS:
        rep.err(f"{tag}: unknown pov '{pov}' (allowed: {', '.join(POVS)})")
    date = meta.get("date_in_story", "")
    if date and not DATE_RE.match(date):
        rep.err(f"{tag}: date_in_story '{date}' not YYYY-MM-DD")

    m = CH_FILE_RE.match(path_name)
    ch_no = int(m.group(1)) if m else None
    if ch_no is None:
        rep.err(f"{tag}: filename not chNN-slug.md")
    elif meta.get("chapter") and meta["chapter"].strip() != str(ch_no):
        rep.err(f"{tag}: front-matter chapter={meta['chapter']} != filename {ch_no}")

    # card mirror
    if ch_no is not None and grid:
        card = grid.get(ch_no)
        if card is None:
            rep.err(f"{tag}: no card in chapter-grid.md for chapter {ch_no}")
        else:
            if pov and card["pov"] != pov:
                rep.err(f"{tag}: pov '{pov}' != card '{card['pov']}'")
            if date and card["date"] != date:
                rep.err(f"{tag}: date {date} != card {card['date']}")
            if meta.get("target_words") and card["target"] != meta["target_words"]:
                rep.err(f"{tag}: target_words {meta['target_words']} != card {card['target']}")
            for field in ("plants", "payoffs"):
                fm_ids = set(parse_id_list(meta.get(field, "")))
                card_ids = set(parse_id_list(card[field])) - {"-", ""}
                if fm_ids != card_ids:
                    rep.err(f"{tag}: {field} {sorted(fm_ids)} != card {sorted(card_ids)}")

    if status == "stub":
        return {"meta": meta, "ch": ch_no, "words": 0}

    words = word_count(body)
    lo, hi = THRESHOLDS["chapter_hard"]
    tlo, thi = THRESHOLDS["chapter_target"]
    if words < lo or words > hi:
        rep.err(f"{tag}: {words} words outside hard band {lo}-{hi}")
    elif words < tlo or words > thi:
        rep.warn(f"{tag}: {words} words outside target band {tlo}-{thi}")

    # dialogue convention: speech opened with quote marks instead of em-dash
    for i, line in enumerate(body.splitlines(), 1):
        if STRAIGHT_QUOTE_SPEECH.match(line):
            rep.err(f"{tag}:{i}: speech opened with quote marks - dialogue is em-dash "
                    f"(«ёлочки» only for titles/documents/written matter)")

    prose = "\n".join(narration_lines(body))
    low = prose.lower()

    for item in guide["forbidden_lexicon"]:
        if item.lower() in low:
            rep.err(f"{tag}: forbidden lexicon '{item}' (Rosman law - see glossary)")

    for item in guide["banned_tics"]:
        n = low.count(item.lower())
        if n:
            rep.err(f"{tag}: banned tic '{item}' x{n}")

    if guide["said_bookisms"]:
        verbs = "|".join(re.escape(v) for v in guide["said_bookisms"])
        for mm in re.finditer(TAG_VERB_RE_TMPL % verbs, prose, re.I):
            rep.warn(f"{tag}: said-bookism tag '{mm.group(0).strip()}' - default is сказал/спросил "
                     f"or an action beat")

    whitelist = {w.lower() for w in guide["latin_whitelist"]}
    leaks = [t for t in LATIN_RE.findall(prose) if t.lower() not in whitelist]
    if len(leaks) > THRESHOLDS["latin_leak_warn"]:
        rep.warn(f"{tag}: {len(leaks)} Latin-script tokens in prose "
                 f"(first: {', '.join(leaks[:5])}) - untranslated leak?")

    return {"meta": meta, "ch": ch_no, "words": words}


# --------------------------------------------------------------------------
# book-level checks
# --------------------------------------------------------------------------

def check_book(results: list[dict], grid: dict[int, dict[str, str]],
               ledger: dict[str, dict[str, str]], rep: Report) -> None:
    by_ch = {r["ch"]: r for r in results if r["ch"] is not None}

    # ledger <-> front-matter sync
    for rid, row in ledger.items():
        for field, col in (("plants", "plant"), ("payoffs", "payoff")):
            ref = row[col].strip()
            if not ref.isdigit():
                continue
            ch = int(ref)
            r = by_ch.get(ch)
            if r is None:
                continue  # chapter not in this run
            ids = parse_id_list(r["meta"].get(field, ""))
            if rid not in ids:
                rep.err(f"ledger {rid}: chapter {ch} must list it in '{field}' "
                        f"(has {ids or '[]'})")
    known = set(ledger)
    for r in results:
        for field in ("plants", "payoffs"):
            for rid in parse_id_list(r["meta"].get(field, "")):
                if known and rid not in known:
                    rep.err(f"ch{r['ch']}: {field} id '{rid}' not in foreshadowing-ledger")

    # timeline monotonic per grid order
    dated = sorted(((r["ch"], r["meta"].get("date_in_story", "")) for r in results
                    if r["ch"] is not None and DATE_RE.match(r["meta"].get("date_in_story", ""))))
    for (c1, d1), (c2, d2) in zip(dated, dated[1:]):
        if d2 < d1:
            rep.err(f"timeline: ch{c2} ({d2}) earlier than ch{c1} ({d1})")

    total = sum(r["words"] for r in results)
    non_stub = [r for r in results if r["words"]]
    blo, bhi = THRESHOLDS["book_band"]
    if grid and len(non_stub) == len(grid) and not (blo <= total <= bhi):
        rep.err(f"book: {total} words outside band {blo}-{bhi}")


def audit_cards(rep: Report) -> None:
    grid = load_grid()
    ledger = load_ledger()
    if not grid:
        rep.err(f"no parsable cards in {GRID}")
        return
    total = 0
    for ch, card in sorted(grid.items()):
        for field in ("title", "pov", "date", "target", "intent", "hook", "status"):
            if not card[field] or card[field] == "-":
                rep.err(f"card {ch}: empty field '{field}'")
        if card["pov"] not in POVS:
            rep.err(f"card {ch}: unknown pov '{card['pov']}'")
        if not DATE_RE.match(card["date"]):
            rep.err(f"card {ch}: date '{card['date']}' not YYYY-MM-DD")
        if card["target"].isdigit():
            total += int(card["target"])
        else:
            rep.err(f"card {ch}: target '{card['target']}' not a number")
        for field in ("plants", "payoffs"):
            for rid in parse_id_list(card[field]):
                if rid != "-" and ledger and rid not in ledger:
                    rep.err(f"card {ch}: {field} id '{rid}' not in ledger")
    seq = sorted(grid)
    if seq != list(range(1, len(seq) + 1)):
        rep.err(f"grid: chapter numbers not contiguous 1..N: {seq}")
    dates = [grid[c]["date"] for c in seq]
    for i in range(1, len(dates)):
        if dates[i] < dates[i - 1]:
            rep.err(f"grid: ch{seq[i]} date {dates[i]} earlier than ch{seq[i-1]}")
    blo, bhi = THRESHOLDS["book_band"]
    if not (blo <= total <= bhi):
        rep.err(f"grid: target sum {total} outside band {blo}-{bhi}")
    else:
        print(f"  grid: {len(grid)} cards, target sum {total} (band {blo}-{bhi})")
    # ledger closure: every row's plant+payoff chapters exist in grid
    for rid, row in ledger.items():
        for col in ("plant", "payoff"):
            ref = row[col].strip()
            if ref.isdigit() and int(ref) not in grid:
                rep.err(f"ledger {rid}: {col} chapter {ref} not in grid")


# --------------------------------------------------------------------------
# assemble
# --------------------------------------------------------------------------

def assemble(out: Path) -> None:
    files = sorted(MANUSCRIPT.glob("ch*.md"))
    parts = []
    for f in files:
        meta, body = split_front_matter(f.read_text(encoding="utf-8"))
        parts.append(f"\n\n# Глава {meta.get('chapter', '?')}. {meta.get('title', '')}\n\n{body.strip()}")
    out.write_text("".join(parts), encoding="utf-8")
    print(f"assembled {len(files)} chapters -> {out}")


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def selftest() -> int:
    guide = {
        "forbidden_lexicon": ["аврор", "аппарац"],
        "banned_tics": ["не мог не"],
        "said_bookisms": ["воскликнул"],
        "latin_whitelist": ["ok"],
    }
    grid = {1: {"title": "Т", "pov": "draco", "date": "2009-05-02", "target": "3000",
                "plants": "P1", "payoffs": "", "intent": "i", "hook": "h", "status": "planned"}}
    fails = []

    def expect(name: str, fired: bool) -> None:
        print(f"  {'ok ' if fired else 'MISS'} {name}")
        if not fired:
            fails.append(name)

    def run(name: str, text: str, needle: str, fname: str = "ch01-test.md") -> None:
        rep = Report()
        res = check_chapter(fname, text, guide, grid, rep)
        check_book([res], grid, {"P1": {"name": "n", "plant": "1", "payoff": "2", "status": "open"}}, rep)
        expect(name, any(needle in m for m in rep.errors + rep.warnings))

    fm = ("---\nchapter: 1\ntitle: Т\npov: draco\ndate_in_story: 2009-05-02\n"
          "target_words: 3000\nplants: [P1]\npayoffs: []\nstatus: draft\n---\n")
    prose_ru = ("Слова тут. " * 300).strip()  # 600 words -> under hard band

    run("missing front-matter key", "---\nchapter: 1\n---\nтекст", "missing key")
    run("unknown pov", fm.replace("pov: draco", "pov: severus") + prose_ru, "unknown pov")
    run("bad date", fm.replace("2009-05-02", "May 2nd") + prose_ru, "not YYYY-MM-DD")
    run("word band", fm + prose_ru, "outside hard band")
    run("card pov mirror", fm.replace("pov: draco", "pov: hermione") + prose_ru, "!= card")
    run("plants mirror", fm.replace("plants: [P1]", "plants: []") + prose_ru, "plants")
    run("quote-mark speech", fm + prose_ru + '\n\n"Привет", — сказал он.', "quote marks")
    run("forbidden lexicon", fm + prose_ru + "\nСтарый аврор кивнул.", "forbidden lexicon")
    run("banned tic", fm + prose_ru + "\nОн не мог не заметить.", "banned tic")
    run("said-bookism", fm + prose_ru + "\n— Нет, — воскликнул он.", "said-bookism")
    run("latin leak", fm + prose_ru + "\nHello world dear reader again.", "Latin-script")
    run("ledger sync", fm.replace("plants: [P1]", "plants: []")
        .replace("chapter: 1", "chapter: 1") + prose_ru, "must list it")
    run("unknown ledger id", fm.replace("plants: [P1]", "plants: [P1, X9]") + prose_ru, "not in foreshadowing-ledger")

    # guide parser round-trip
    parsed = parse_guide_lists(
        "### 8.1 Запрещённый лексикон\n- аврор → мракоборец\n- окаянт\n"
        "### 8.2 Запрещённые тики\n- не мог не\n"
        "### 8.3 Глагольные ярлыки\n- воскликнул\n"
        "### 8.4 Латиница — белый список\n- v0\n")
    expect("guide parser", parsed["forbidden_lexicon"] == ["аврор", "окаянт"]
           and parsed["banned_tics"] == ["не мог не"]
           and parsed["said_bookisms"] == ["воскликнул"]
           and parsed["latin_whitelist"] == ["v0"])

    if fails:
        print(f"\nSELFTEST: RED - {len(fails)} check(s) did not fire: {fails}")
        return 1
    print("\nSELFTEST: GREEN - every check fires")
    return 0


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--cards", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--assemble", metavar="FILE")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rep = Report()
    if args.cards:
        audit_cards(rep)
        return rep.dump()
    if args.assemble:
        assemble(Path(args.assemble))
        return 0

    guide = load_guide()
    grid = load_grid()
    ledger = load_ledger()

    if args.paths:
        files = [Path(p) for p in args.paths]
    else:
        files = sorted(MANUSCRIPT.glob("ch*.md")) if MANUSCRIPT.exists() else []

    if not files:
        print("gate: no chapter files yet - checking bible only")
        audit_cards(rep) if GRID.exists() else None
        return rep.dump()

    results = []
    for f in files:
        results.append(check_chapter(f.name, f.read_text(encoding="utf-8"), guide, grid, rep))
    check_book(results, grid, ledger, rep)
    total = sum(r["words"] for r in results)
    print(f"  checked {len(files)} file(s), {total} words")
    return rep.dump()


if __name__ == "__main__":
    sys.exit(main())
