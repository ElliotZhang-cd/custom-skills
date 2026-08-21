@echo off
chcp 65001 >nul
rem ============================================================
rem sync-windows.bat - sync custom-skills on Windows side
rem Source of truth: GitHub -> this script (pull + distribute + audit)
rem Usage: double-click, or schedule in Task Scheduler
rem Targets: workbuddy + TRAE (skills auto-discovered by SKILL.md,
rem          the repo IS the list - no hand-maintained names)
rem Second source: maintaining-llm-wiki from Documents\LLMWiki repo
rem Audit: scripts\check_distribution.py runs at the end and reports
rem        MISSING / EXTRA / BROKEN across all surfaces
rem NOTE: comments MUST stay ASCII-only. Chinese rem lines + chcp 65001 trigger
rem   cmd's multi-byte misparse; an ASCII "->" in a comment got split and its
rem   ">" became a redirection, creating a stray 0-byte file on every run
rem   (investigated 2026-08-13). Chinese is safe in echo lines only.
rem Change 2026-08-21: hand list removed; TRAE added; mllw second source;
rem   end-to-end audit appended.
rem ============================================================
setlocal enabledelayedexpansion
set "PYTHONUTF8=1"
set "REPO=%USERPROFILE%\custom-skills"
set "WB_SKILLS=%USERPROFILE%\.workbuddy\skills"
set "TRAE_SKILLS=%USERPROFILE%\.trae-cn\skills"
set "MLLW_SRC=%USERPROFILE%\Documents\LLMWiki\skills\maintaining-llm-wiki"

if not exist "%REPO%\.git" (
    echo [sync] 仓库不存在，首次使用请先执行:
    echo        git clone https://github.com/ElliotZhang-cd/custom-skills.git "%REPO%"
    pause
    exit /b 1
)

echo [1/4] pulling latest from GitHub...
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

echo [2/4] 分发自建 skill（自动发现，repo 即列表）到 workbuddy + TRAE...
for /d %%s in ("%REPO%\*") do (
    if exist "%%s\SKILL.md" call :distribute "%%~nxs" "%%s"
)

echo [3/4] 分发 maintaining-llm-wiki（第二源: LLMWiki 仓库）...
if exist "%MLLW_SRC%\SKILL.md" (
    call :distribute "maintaining-llm-wiki" "%MLLW_SRC%"
) else (
    echo   [warn] 源缺失: %MLLW_SRC%（LLMWiki 未克隆或已迁移？）
)

echo [4/4] 分发对账...
where python >nul 2>nul
if !errorlevel! neq 0 (
    echo   [skip] 未找到 python，跳过对账（可改在 WSL 跑 check_distribution.py）
) else (
    python "%REPO%\scripts\check_distribution.py"
    if !errorlevel! neq 0 (
        echo [sync] 注意: 上方存在缺口，按提示处理后重跑本脚本。
    ) else (
        echo [sync] 对账通过，全部分发面对齐。
    )
)

echo [sync] 完成。下次启动即生效。
pause
exit /b 0

:distribute
rem args: %1 = skill name, %2 = source dir. Targets: workbuddy always, TRAE if home exists.
set "TARGETS=%WB_SKILLS%"
if exist "%USERPROFILE%\.trae-cn" set "TARGETS=%TARGETS%;%TRAE_SKILLS%"
for %%t in (%TARGETS%) do (
    if not exist "%%t\%~1" mkdir "%%t\%~1"
    robocopy "%~2" "%%t\%~1" /E /NFL /NDL /NJH /NJS /NP >nul
    if exist "%%t\%~1\SKILL.md" (
        echo   [ok] %~1 已分发 %%t
        echo %~2>"%%t\%~1\.custom-src"
    ) else (
        echo   [FAIL] %~1 目标未生成 SKILL.md: %%t
    )
)
goto :eof
