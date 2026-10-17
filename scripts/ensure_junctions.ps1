# ensure_junctions.ps1 - link-as-list (v7.3): keep the Windows junction surfaces
# equal to the skill set this repo owns. Idempotent. Comments stay ASCII-only.
#
#   config : the surface list is READ from distribution-targets.json in this
#            script's own directory (whitelist-driven; never hardcoded). Only
#            entries with platform == "win" are considered, and of those only
#            role == "junction" ones are linked / pruned. A missing or
#            unparsable config is a hard error (exit 1), never a silent no-op.
#   add    : every selfbuilt skill (a repo dir holding SKILL.md) + mllw gets a
#            junction pointing at its source on every junction surface. On
#            surfaces whose expect list contains "thirdparty", every skill in
#            the npx store (%USERPROFILE%\.agents\skills, real dirs) also gets
#            a junction pointing at that store entry -- npx owns the store
#            (repo layer) only; the platform layer is this script + links +
#            reconciliation.
#   lazy   : if a surface's PARENT dir exists (the tool is installed) but the
#            skills dir does not, the skills dir is created and reported as
#            "[new] surface created: ...". Tools that materialize their skills
#            root lazily (desktop DSH) are therefore owned here.
#   prune  : a junction/symlink on a surface whose target lies under a managed
#            root (this repo, LLMWiki\skills or the npx store) but no longer
#            resolves to a skill (renamed / retired / dead target) is removed.
#            Only the link is deleted, never a target, and never a foreign link.
#   warn   : a surface whose parent is missing too (tool not installed) prints
#            "[WARN] surface missing (tool not installed?)". That only sets
#            exit 1 when the surface is required: true in the whitelist, so
#            "tool not installed" is not misreported as a sync failure.
# Real directories are NEVER replaced here: legacy manual third-party copies
# (manual-skills.md ledger) and anything the CLI materialized into a surface are
# left alone and reported. Once a name is in the npx store, reconciliation
# flags such a copy as [STALE]; a human deletes it, then this script links it.
$ErrorActionPreference = 'Continue'
$repo = Join-Path $env:USERPROFILE 'custom-skills'
$mllwSrc = Join-Path $env:USERPROFILE 'Documents\LLMWiki\skills\maintaining-llm-wiki'
$store = Join-Path $env:USERPROFILE '.agents\skills'   # npx 仓库层（第三方存储面）
$configPath = Join-Path $PSScriptRoot 'distribution-targets.json'

function Get-Prop($obj, [string]$name, $default) {
  if ($null -eq $obj) { return $default }
  $p = $obj.PSObject.Properties[$name]
  if ($null -eq $p -or $null -eq $p.Value) { return $default }
  return $p.Value
}

# --- surfaces come from the whitelist only ---------------------------------
if (-not (Test-Path $configPath)) {
  Write-Output ("  [ERROR] config missing: " + $configPath + " (whitelist is the only surface source)")
  exit 1
}
try {
  $cfg = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
  Write-Output ("  [ERROR] config parse failed: " + $configPath + " - " + $_.Exception.Message)
  exit 1
}
if ($null -eq $cfg -or $null -eq $cfg.surfaces) {
  Write-Output ("  [ERROR] config has no 'surfaces' array: " + $configPath)
  exit 1
}

$targets = @()
foreach ($s in @($cfg.surfaces)) {
  if ((Get-Prop $s 'platform' 'posix') -ne 'win') { continue }
  $sid = [string](Get-Prop $s 'id' '')
  $rel = @(Get-Prop $s 'relpath' @() | Where-Object { $_ })
  if ($rel.Count -eq 0) {
    Write-Output ("  [WARN] surface with empty relpath, skipped: " + $sid)
    continue
  }
  $targets += [pscustomobject]@{
    Id       = $sid
    Role     = [string](Get-Prop $s 'role' 'junction')
    Required = [bool](Get-Prop $s 'required' $false)
    Expect   = @(Get-Prop $s 'expect' @())
    Path     = (Join-Path $env:USERPROFILE ($rel -join '\'))
  }
}
Write-Output ("  [cfg]  " + $targets.Count + " Windows surface(s) from distribution-targets.json")

# Managed roots: only links pointing below these are ours to prune. A root that
# does not exist stays out of the list, so an unavailable repo or LLMWiki can
# never cause a pruning spree.
$managedRoots = @()
foreach ($root in @($repo, (Split-Path $mllwSrc -Parent), $store)) {
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

# third-party items live in the npx store as real directories (our own entries
# there are junctions, so LinkType plus the name check keeps them out).
$owned = @{}
foreach ($i in $items) { $owned[[string]$i[0]] = $true }
$tpItems = @()
if (Test-Path $store) {
  Get-ChildItem $store -Directory -Force | Where-Object {
    (-not $_.LinkType) -and (-not $owned.ContainsKey($_.Name)) -and
    (Test-Path (Join-Path $_.FullName 'SKILL.md'))
  } | ForEach-Object { $tpItems += ,@($_.Name, $_.FullName) }
}
$miss = 0
$added = 0
$cleaned = 0
$missingRequired = 0

foreach ($t in $targets) {
  $tPath = $t.Path
  if ($t.Role -ne 'junction') {
    Write-Output ("  [skip] surface " + $t.Id + " role=" + $t.Role + " (not a junction surface; only role=junction is linked here)")
    continue
  }

  if (-not (Test-Path $tPath)) {
    $parent = Split-Path $tPath -Parent
    if (Test-Path $parent) {
      # tool installed, skills root not materialized yet -> lazy-create owns it
      try {
        New-Item -ItemType Directory -Path $tPath -Force | Out-Null
        Write-Output ("  [new] surface created: " + $tPath)
      } catch {
        Write-Output ("  [WARN] surface create failed " + $tPath + ": " + $_.Exception.Message)
        if ($t.Required) { $missingRequired++ }
        continue
      }
    } else {
      Write-Output ("  [WARN] surface missing (tool not installed?): " + $tPath)
      if ($t.Required) { $missingRequired++ }
      continue
    }
  }

  # --- prune first, so a renamed skill's stale link cannot block its new link ---
  # NOTE: Test-Path on a dead junction returns True (verified on 5.1 and 7.x),
  # so liveness must be judged on the resolved TARGET, not on the link path.
  foreach ($e in @(Get-ChildItem $tPath -Force)) {
    if ("$($e.LinkType)" -notin @('Junction', 'SymbolicLink')) { continue }
    $tgt = Get-LinkTarget $e
    if (-not (Test-UnderManagedRoot $tgt)) { continue }   # foreign link: not ours
    if ((Test-Path $tgt) -and (Test-Path (Join-Path $tgt 'SKILL.md'))) { continue }  # healthy
    $bak = Join-Path $tPath ($e.Name + '.copy-bak')
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
    $bak = Join-Path $tPath ($s + '.copy-bak')
    $dst = Join-Path $tPath $s
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

  # --- third-party: npx owns the store, this script links it into surfaces ---
  if (@($t.Expect) -contains 'thirdparty') {
    foreach ($item in $tpItems) {
      $s = $item[0]; $src = $item[1]
      $dst = Join-Path $tPath $s
      if (Test-Path $dst) {
        $lt = "$((Get-Item $dst).LinkType)"
        if ($lt -ne 'Junction') {
          Write-Output ("  [note] real copy where a third-party junction is expected: " +
                        $dst + " (delete the copy, then re-run to link the store entry)")
        }
        continue
      }
      New-Item -ItemType Junction -Path $dst -Value $src | Out-Null
      Write-Output ("  [link] " + $dst + " -> " + $src)
      $added++
    }
  }
}
Write-Output ("  [sum]  added " + $added + " / cleaned " + $cleaned + " / source-missing " + $miss)
if ($missingRequired -gt 0) {
  Write-Output ("  [WARN] " + $missingRequired + " required surface(s) absent on this host (see [WARN] lines above)")
}
if ($miss -gt 0 -or $missingRequired -gt 0) { exit 1 }
