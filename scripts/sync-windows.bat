@echo off
chcp 65001 >nul
rem ============================================================
rem sync-windows.bat - Windows side sync: pull + ensure-junctions + audit
rem Since v6 (2026-09-03) ALL Windows surfaces (workbuddy / TRAE / zcode)
rem   read selfbuilt + mllw via junctions to this repo (or LLMWiki), so
rem   there is NOTHING to robocopy-distribute anymore. This script
rem   refreshes the local clone (which the junctions follow), ensures
rem   every selfbuilt/mllw skill has a junction on every surface
rem   (link-as-list, idempotent), and runs the audit.
rem Usage: double-click, or schedule in Task Scheduler
rem Audit: scripts\check_distribution.py (five surfaces; manual items
rem        tracked via manual-skills.md ledger)
rem NOTE: comments MUST stay ASCII-only. Chinese rem lines + chcp 65001 trigger
rem   cmd's multi-byte misparse (investigated 2026-08-13). Chinese in echo lines only.
rem History: robocopy distribution + .custom-src markers removed 2026-09-03
rem   (v6 all-junction, link-as-list via ensure_junctions.ps1);
rem   see LLMWiki skill-maintenance-workflow v6.
rem ============================================================
setlocal enabledelayedexpansion
set "PYTHONUTF8=1"
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
    echo [sync] pull 失败（已排除本地修改干扰），请检查网络/代理
    pause
    exit /b 1
)
for /f "delims=" %%v in ('git log -1 --oneline') do echo [sync] 当前版本: %%v

echo [2/3] ensuring junctions (link-as-list: selfbuilt + mllw on three surfaces)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO%\scripts\ensure_junctions.ps1"
if !errorlevel! neq 0 (
    echo [sync] 注意: 存在源缺失， junction 未完全建齐。
)

echo [3/3] 分发对账（五面）...
python "%REPO%\scripts\check_distribution.py"
if !errorlevel! neq 0 (
    echo [sync] 注意: 上方存在缺口，按提示处理后重跑本脚本。
) else (
    echo [sync] 对账通过，全部分发面对齐。
)

echo [sync] 完成。junction 即改即生效，下次启动工具可见。
pause
exit /b 0
