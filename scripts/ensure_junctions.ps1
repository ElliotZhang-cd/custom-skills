# ensure_junctions.ps1 - link-as-list (v6/v7.1): keep the four Windows surfaces
# equal to the skill set this repo owns. Idempotent.
#   add   : every selfbuilt skill (a repo dir holding SKILL.md) + mllw gets a
#           junction pointing at its source on every surface.
#   prune : a junction/symlink on a surface whose target lies under a managed
#           root (this repo or LLMWiki\skills) but no longer resolves to a skill
#           (renamed / retired / dead target) is removed. Only the link is
#           deleted, never a target, and never a foreign link.
# Manual third-party items (manual-skills.md ledger) are NOT managed here:
# real directories are skipped and reported.
$ErrorActionPreference = 'Continue'
$repo = Join-Path $env:USERPROFILE 'custom-skills'
$mllwSrc = Join-Path $env:USERPROFILE 'Documents\LLMWiki\skills\maintaining-llm-wiki'
$targets = @(
  (Join-Path $env:USERPROFILE '.workbuddy\skills'),
  (Join-Path $env:USERPROFILE '.trae-cn\skills'),
  (Join-Path $env:USERPROFILE '.zcode\skills'),
  (Join-Path $env:USERPROFILE '.dsh\skills')
)
# v7: desktop DSH materializes its skills root lazily, so link-as-list owns it:
# create it as soon as the DSH home exists (a missing surface is otherwise skipped).
$dshHome = Join-Path $env:USERPROFILE '.dsh'
$dshSkills = Join-Path $dshHome 'skills'
if ((Test-Path $dshHome) -and -not (Test-Path $dshSkills)) {
  New-Item -ItemType Directory -Path $dshSkills -Force | Out-Null
  Write-Output ("  [new] surface created: " + $dshSkills)
}

# Managed roots: only links pointing below these are ours to prune. A root that
# does not exist stays out of the list, so an unavailable repo or LLMWiki can
# never cause a pruning spree.
$managedRoots = @()
foreach ($root in @($repo, (Split-Path $mllwSrc -Parent))) {
  if (Test-Path $root) { $managedRoots += (Resolve-Path $root).Path.TrimEnd('\') }
}

function Get-LinkTarget([System.IO.FileSystemInfo]$item) {
  try { $t = @($item.Target); if ($t.Count -gt 0) { return [string]$t[0] } } catch { }
  return $null
}

function Test-UnderManagedRoot([string]$path) {
  if (-not $path) { return $false }
  try { $full = [System.IO.Path]::GetFullPath($path) } catch { return $false }
  if ($full.StartsWith('\\?\')) { $full = $full.Substring(4) }
  foreach ($r in $managedRoots) {
    if ($full.Equals($r, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    if ($full.StartsWith($r + '\', [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
  }
  return $false
}

$items = @()
Get-ChildItem $repo -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } | ForEach-Object {
  $items += ,@($_.Name, $_.FullName)
}
if (Test-Path $mllwSrc) { $items += ,@('maintaining-llm-wiki', $mllwSrc) }
$miss = 0
$added = 0
$cleaned = 0
foreach ($t in $targets) {
  if (-not (Test-Path $t)) { Write-Output ("  [skip] surface missing: " + $t); continue }

  # --- prune first, so a renamed skill's stale link cannot block its new link ---
  # NOTE: Test-Path on a dead junction returns True (verified on 5.1 and 7.x),
  # so liveness must be judged on the resolved TARGET, not on the link path.
  foreach ($e in @(Get-ChildItem $t -Force)) {
    if ("$($e.LinkType)" -notin @('Junction', 'SymbolicLink')) { continue }
    $tgt = Get-LinkTarget $e
    if (-not (Test-UnderManagedRoot $tgt)) { continue }   # foreign link: not ours
    if ((Test-Path $tgt) -and (Test-Path (Join-Path $tgt 'SKILL.md'))) { continue }  # healthy
    $bak = Join-Path $t ($e.Name + '.copy-bak')
    if (Test-Path $bak) { Write-Output ("  [note] backup present: " + $bak) }
    try {
      (Get-Item $e.FullName).Delete()   # removes the reparse point only
      Write-Output ("  [clean] " + $e.FullName + " -> " + $tgt + " (dead/not a skill)")
      $cleaned++
    } catch {
      Write-Output ("  [WARN] delete failed " + $e.FullName + ": " + $_.Exception.Message)
    }
  }

  # --- link-as-list: add what is missing ---
  foreach ($item in $items) {
    $s = $item[0]; $src = $item[1]
    $bak = Join-Path $t ($s + '.copy-bak')
    $dst = Join-Path $t $s
    if (Test-Path $bak) { Write-Output ("  [note] backup present: " + $bak) }
    if (Test-Path $dst) {
      $lt = "$((Get-Item $dst).LinkType)"
      if ($lt -ne 'Junction') {
        if ($lt) { Write-Output ("  [note] " + $lt + " left alone (not a junction): " + $dst) }
        else { Write-Output ("  [note] real dir (manual item?): " + $dst) }
      }
      continue
    }
    if (-not (Test-Path $src)) { Write-Output ("  [MISS] source missing: " + $src); $miss++; continue }
    New-Item -ItemType Junction -Path $dst -Value $src | Out-Null
    Write-Output ("  [link] " + $dst + " -> " + $src)
    $added++
  }
}
Write-Output ("  [sum]  added " + $added + " / cleaned " + $cleaned + " / source-missing " + $miss)
if ($miss -gt 0) { exit 1 }
