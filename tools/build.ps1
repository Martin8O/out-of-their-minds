<#
.SYNOPSIS
    «Не в своём уме» - build EPUB, MOBI and A5 (book-size) PDF from the manuscript.

.DESCRIPTION
    Adapted from the parent Unplottable build for this Russian-language book.
    Runs the quality gate first (green required), assembles manuscript\ch*.md
    into one book-shaped markdown file via `python tools\gate.py --assemble`,
    wraps it in the front/back matter (book\00-front.md, book\zz-colophon.md,
    book\metadata.yaml) and runs pandoc over the lot. MOBI is produced from the
    EPUB with Calibre's ebook-convert (no LaTeX needed for that leg).

    A cover image at book\cover.png (or .jpg) is embedded in EPUB + MOBI when
    present; the build works without one.

    Requirements, checked and reported before anything is attempted:
      * python        - always needed (gate + assembly)
      * pandoc        - EPUB and PDF
      * ebook-convert - MOBI (ships with Calibre)
      * a LaTeX engine (xelatex / lualatex / tectonic) - PDF only.
        A Unicode engine is REQUIRED here: pdflatex cannot set Cyrillic with a
        system font.

.PARAMETER Format
    epub | pdf | mobi | all (default: all)

.PARAMETER OutDir
    Output directory (default: build\ - gitignored)

.PARAMETER SkipGate
    Build even if the gate is not green (diagnostics only; never for a release).

.EXAMPLE
    powershell tools\build.ps1
    powershell tools\build.ps1 -Format epub
    powershell tools\build.ps1 -Check
#>
[CmdletBinding()]
param(
    [ValidateSet('epub', 'pdf', 'mobi', 'all')][string]$Format = 'all',
    [string]$OutDir = 'build',
    [string]$Stem = 'ne-v-svoyom-ume',
    [string]$Title = 'Не в своём уме',
    [string]$Lang = 'ru-RU',
    [switch]$SkipGate,
    [switch]$Check
)

$ErrorActionPreference = 'Stop'

# Machine-specific settings (e.g. $env:TECTONIC_HOME) live here, outside version control.
$localConfig = Join-Path $PSScriptRoot 'local.ps1'
if (Test-Path $localConfig) { . $localConfig }

$repo = Split-Path -Parent $PSScriptRoot      # repo root
$stem = $Stem
$title = $Title

function Get-Tool([string]$name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source } else { return $null }
}

Write-Host "== Ne v svoyom ume - build ==" -ForegroundColor Cyan
Write-Host "root:   $repo"

$python = Get-Tool 'python'
$pandoc = Get-Tool 'pandoc'
$calibre = Get-Tool 'ebook-convert'
if (-not $calibre) {
    $candidates = @()
    if (${env:ProgramFiles}) { $candidates += (Join-Path ${env:ProgramFiles} 'Calibre2\ebook-convert.exe') }
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if ($pf86) { $candidates += (Join-Path $pf86 'Calibre2\ebook-convert.exe') }
    foreach ($p in $candidates) {
        if (-not $calibre -and (Test-Path $p)) { $calibre = $p }
    }
}
# pdflatex is deliberately absent from this list: it cannot typeset Cyrillic
# with a system font, which this book needs.
$engines = @('xelatex', 'lualatex', 'tectonic')
$engine = $null
foreach ($e in $engines) { if (-not $engine -and (Get-Tool $e)) { $engine = $e } }
# Optional self-contained tectonic: set TECTONIC_HOME to a folder holding
# tectonic.exe (parent ADR-010 - a full TeX distribution can exhaust a small
# system drive, and on this machine C: is off limits for project data).
$tectonicHome = $env:TECTONIC_HOME
if (-not $engine -and $tectonicHome -and (Test-Path (Join-Path $tectonicHome 'tectonic.exe'))) {
    $engine = Join-Path $tectonicHome 'tectonic.exe'
}
if ($engine -like '*tectonic*' -and -not $env:TECTONIC_CACHE_DIR -and $tectonicHome) {
    $env:TECTONIC_CACHE_DIR = Join-Path $tectonicHome 'cache'
}

Write-Host "python:        $(if ($python) { $python } else { 'NOT FOUND' })"
Write-Host "pandoc:        $(if ($pandoc) { $pandoc } else { 'NOT FOUND' })"
Write-Host "ebook-convert: $(if ($calibre) { $calibre } else { 'NOT FOUND' })"
Write-Host "pdf engine:    $(if ($engine) { $engine } else { 'NOT FOUND' })"

if (-not $python) {
    Write-Host ""
    Write-Host "python not found - cannot run the gate or assemble the manuscript." -ForegroundColor Red
    exit 3
}
if (-not $pandoc) {
    Write-Host ""
    Write-Host "pandoc not found - no EPUB/MOBI/PDF can be built." -ForegroundColor Yellow
    Write-Host "  install:  winget install --id JohnMacFarlane.Pandoc"
    Write-Host "  for PDF also a Unicode LaTeX engine, e.g.:"
    Write-Host "            winget install --id MiKTeX.MiKTeX     (provides xelatex)"
    Write-Host "  for MOBI: Calibre - https://calibre-ebook.com/"
    Write-Host ""
    Write-Host "Nothing was built. The manuscript itself is unaffected." -ForegroundColor Yellow
    exit 3
}

if ($Check) { Write-Host ""; Write-Host "-Check: tooling reported, nothing built."; exit 0 }

# --- gate first: nothing ships that is not green --------------------------
if (-not $SkipGate) {
    Write-Host ""
    Write-Host "quality gate ..." -ForegroundColor Cyan
    & $python (Join-Path $PSScriptRoot 'gate.py')
    if ($LASTEXITCODE -ne 0) {
        Write-Host "gate is not green - refusing to build. (-SkipGate overrides, diagnostics only.)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

$out = Join-Path $repo $OutDir
New-Item -ItemType Directory -Force -Path $out | Out-Null
$combined = Join-Path $out "$stem.md"

Write-Host ""
Write-Host "assembling ..." -ForegroundColor Cyan
& $python (Join-Path $PSScriptRoot 'gate.py') --assemble $combined
if ($LASTEXITCODE -ne 0) { Write-Host "assembly failed." -ForegroundColor Red; exit $LASTEXITCODE }

# --- front/back matter + metadata + cover ---------------------------------
$bookDir = Join-Path $repo 'book'
$front = Join-Path $bookDir '00-front.md'
$after = Join-Path $bookDir '99-afterword.md'
$colophon = Join-Path $bookDir 'zz-colophon.md'
$meta = Join-Path $bookDir 'metadata.yaml'

$inputs = @()
if (Test-Path $front) { $inputs += $front }
$inputs += $combined
if (Test-Path $after) { $inputs += $after }
if (Test-Path $colophon) { $inputs += $colophon }

$cover = $null
foreach ($c in @('cover.png', 'cover.jpg', 'cover.jpeg')) {
    $p = Join-Path $bookDir $c
    if (-not $cover -and (Test-Path $p)) { $cover = $p }
}
Write-Host "cover:         $(if ($cover) { $cover } else { 'none (title page only)' })"

# Level 1 headings are the four parts, level 2 the chapters (see book\parts.txt),
# so the contents list both and the EPUB splits one file per chapter.
$common = @(
    '--from', 'markdown+smart',
    '--standalone',
    '--toc', '--toc-depth=2'
)
if (Test-Path $meta) { $common += @('--metadata-file', $meta) }
$common += @('--metadata', "title=$title", '--metadata', "lang=$Lang")

$built = @()
$epub = Join-Path $out "$stem.epub"

if ($Format -in @('epub', 'mobi', 'all')) {
    Write-Host "pandoc -> EPUB ..." -ForegroundColor Cyan
    $epubArgs = @($inputs) + $common + @('--split-level=2')
    if ($cover) { $epubArgs += @("--epub-cover-image=$cover") }
    $epubArgs += @('--output', $epub)
    & $pandoc @epubArgs
    if ($LASTEXITCODE -eq 0) { $built += $epub }
    else { Write-Host "EPUB build failed (exit $LASTEXITCODE)." -ForegroundColor Red }
}

if ($Format -in @('mobi', 'all')) {
    if (-not (Test-Path $epub)) {
        Write-Host "no EPUB to convert - skipping MOBI." -ForegroundColor Yellow
    }
    elseif (-not $calibre) {
        Write-Host ""
        Write-Host "ebook-convert (Calibre) not found - skipping MOBI." -ForegroundColor Yellow
        Write-Host "  install Calibre from https://calibre-ebook.com/ (ebook-convert ships with it)"
    }
    else {
        $mobi = Join-Path $out "$stem.mobi"
        Write-Host "ebook-convert -> MOBI ..." -ForegroundColor Cyan
        & $calibre $epub $mobi --output-profile kindle
        if ($LASTEXITCODE -eq 0) { $built += $mobi }
        else { Write-Host "MOBI build failed (exit $LASTEXITCODE)." -ForegroundColor Red }
    }
}

if ($Format -in @('pdf', 'all')) {
    if (-not $engine) {
        Write-Host ""
        Write-Host "No Unicode LaTeX engine found - skipping PDF." -ForegroundColor Yellow
        Write-Host "  install:  winget install --id MiKTeX.MiKTeX   (then reopen the shell)"
    }
    else {
        $pdf = Join-Path $out "$stem.pdf"
        # A5 book block. At 10.5pt/1.8cm this sets roughly 320-340 words a page,
        # i.e. ~300 pages for 103k words - see docs\adr.md ADR-009 on why the
        # brief's "180-200 pages" is not reachable at A5 without unreadable type.
        # Palatino Linotype (body) and Consolas (mono) ship with Windows and both
        # carry full Cyrillic; a Unicode engine is required to use them.
        Write-Host "pandoc -> PDF (A5 book, $engine) ..." -ForegroundColor Cyan
        $pdfArgs = @($inputs) + $common + @(
            "--pdf-engine=$engine",
            '-V', 'papersize=a5',
            '-V', 'geometry:margin=1.8cm',
            '-V', 'fontsize=10.5pt',
            '-V', 'linkcolor=black',
            '-V', 'mainfont=Palatino Linotype',
            '-V', 'monofont=Consolas',
            '-V', 'header-includes=\emergencystretch=3em',
            '--output', $pdf
        )
        & $pandoc @pdfArgs
        if ($LASTEXITCODE -eq 0) { $built += $pdf }
        else { Write-Host "PDF build failed (exit $LASTEXITCODE)." -ForegroundColor Red }
    }
}

Write-Host ""
if ($built.Count -eq 0) {
    Write-Host "Nothing was built." -ForegroundColor Yellow
    exit 3
}
Write-Host "built:" -ForegroundColor Green
foreach ($f in $built) {
    $kb = [math]::Round((Get-Item $f).Length / 1KB, 1)
    Write-Host ("  {0}  ({1} KB)" -f $f, $kb)
}
exit 0
