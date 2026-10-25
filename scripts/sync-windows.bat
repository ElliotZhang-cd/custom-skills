@echo off
chcp 65001 >nul
rem ============================================================
rem sync-windows.bat - Windows side sync: pull + ensure-junctions + audit
rem Since v6 (2026-09-03) ALL Windows surfaces (workbuddy / zcode /
rem   dsh, the last registered in v7 2026-10-16)
rem   read selfbuilt via junctions to this repo, so
rem   there is NOTHING to robocopy-distribute anymore. This script
rem   refreshes the local clone (which the junctions follow), ensures
rem   every selfbuilt skill has a junction on every surface
rem   (link-as-list, idempotent), prunes the links this repo owns that no
rem   longer resolve to a skill, and runs the audit.
rem Usage: sync-windows.bat [--strict]
rem   double-click / interactive: audit failure only prints a note (historical
rem   behavior). --strict: exit 1 when the audit fails and skip the pause --
rem   for Task Scheduler / hooks. Either way the AUDIT OUTPUT is the verdict,
rem   never this script's exit code alone.
rem Audit: scripts\check_distribution.py (surfaces come from
rem        distribution-targets.json; manual items tracked via manual-skills.md)
rem NOTE: comments MUST stay ASCII-only. Chinese rem lines + chcp 65001 trigger
rem   cmd's multi-byte misparse (investigated 2026-08-13). Chinese in echo lines only.
rem History: robocopy distribution + .custom-src markers removed 2026-09-03
rem   (v6 all-junction, link-as-list via ensure_junctions.ps1);
rem   desktop DSH (.dsh\skills) registered 2026-10-16 as a Windows
rem   junction surface (v7); v7.1 2026-10-17 makes the link script also
rem   prune links it owns whose target is dead or is no longer a skill;
rem   v7.3 2026-10-17 retires the TRAE surface and makes the link script
rem   config-driven; v7.5 2026-10-25 drops the retired mllw category
rem   (docs/adr/0005) and adds --strict.
rem ============================================================
setlocal enabledelayedexpansion
set "PYTHONUTF8=1"
set "STRICT="
if /i "%~1"=="--strict" set "STRICT=1"
set "REPO=%USERPROFILE%\custom-skills"

if not exist "%REPO%\.git" (
    echo [sync] 仓库不存在，首次使用请先执行:
    echo        git clone https://github.com/ElliotZhang-cd/custom-skills.git "%REPO%"
    pause
    exit /b 1
)

echo [1/3] pulling latest from GitHub...
cd /d "%REPO%"
set "DIRTY="
git status --porcelain | findstr /R "." >nul
if !errorlevel! equ 0 set "DIRTY=1"
if defined DIRTY (
    echo [sync] 错误: 仓库有本地未提交修改（含未跟踪文件），--ff-only pull 会被拒绝:
    git status --short
    echo [sync] 处理: 改动已在远端则 git checkout -- . 丢弃；否则 git stash
    pause
    exit /b 1
)
git pull --ff-only origin master
if !errorlevel! neq 0 (
    echo [sync] pull via proxy failed, retrying direct...
    git -c http.proxy= -c https.proxy= pull --ff-only origin master
    if !errorlevel! neq 0 (
        echo [sync] pull 失败（代理与直连均不可达），请检查网络
        pause
        exit /b 1
    )
)
for /f "delims=" %%v in ('git log -1 --oneline') do echo [sync] 当前版本: %%v

echo [2/3] ensuring junctions (link-as-list: 三面补链 + 清理失效链)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO%\scripts\ensure_junctions.ps1"
if !errorlevel! neq 0 (
    echo [sync] 注意: 存在源缺失， junction 未完全建齐。
)

echo [3/3] 分发对账...
python "%REPO%\scripts\check_distribution.py"
set "AUDIT_RC=!errorlevel!"
if "!AUDIT_RC!"=="0" (
    echo [sync] 对账通过，全部分发面对齐。
    echo [sync] 完成。junction 即改即生效，下次启动工具可见。
) else (
    echo [sync] 注意: 上方存在缺口，按提示处理后重跑本脚本（以对账输出为准）。
)
if defined STRICT (
    if not "!AUDIT_RC!"=="0" exit /b 1
    exit /b 0
)
pause
exit /b 0
