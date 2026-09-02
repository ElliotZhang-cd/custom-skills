# ensure_junctions.ps1 - link-as-list (v6): create missing junctions for
# selfbuilt + mllw on the three Windows surfaces. Idempotent.
# Manual third-party items (manual-skills.md ledger) are NOT managed here;
# same-name real directories are skipped and reported.
$ErrorActionPreference = 'Continue'
$repo = Join-Path $env:USERPROFILE 'custom-skills'
$mllwSrc = Join-Path $env:USERPROFILE 'Documents\LLMWiki\skills\maintaining-llm-wiki'
$targets = @(
  (Join-Path $env:USERPROFILE '.workbuddy\skills'),
  (Join-Path $env:USERPROFILE '.trae-cn\skills'),
  (Join-Path $env:USERPROFILE '.zcode\skills')
)
$items = @()
Get-ChildItem $repo -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | ForEach-Object {
  $items += ,@($_.Name, $_.FullName)
}
if (Test-Path $mllwSrc) { $items += ,@('maintaining-llm-wiki', $mllwSrc) }
$miss = 0
foreach ($t in $targets) {
  if (-not (Test-Path $t)) { Write-Output ("  [skip] surface missing: " + $t); continue }
  foreach ($item in $items) {
    $s = $item[0]; $src = $item[1]
    $bak = Join-Path $t ($s + '.copy-bak')
    $dst = Join-Path $t $s
    if (Test-Path $bak) { Write-Output ("  [note] backup present: " + $bak) }
    if (Test-Path $dst) {
      $lt = (Get-Item $dst).LinkType
      if ($lt -ne 'Junction') { Write-Output ("  [note] real dir (manual item?): " + $dst) }
      continue
    }
    if (-not (Test-Path $src)) { Write-Output ("  [MISS] source missing: " + $src); $miss++; continue }
    New-Item -ItemType Junction -Path $dst -Value $src | Out-Null
    Write-Output ("  [link] " + $dst + " -> " + $src)
  }
}
if ($miss -gt 0) { exit 1 }
