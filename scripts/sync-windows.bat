@echo off
chcp 65001 >nul
rem ============================================================
rem sync-windows.bat - sync custom-skills on Windows side
rem Source of truth: GitHub -> this script (pull + distribute to workbuddy)
rem Usage: double-click, or schedule in Task Scheduler
rem NOTE: comments MUST stay ASCII-only. Chinese rem lines + chcp 65001 trigger
rem   cmd's multi-byte misparse; an ASCII "->" in a comment got split and its
rem   ">" became a redirection, creating a stray 0-byte file on every run
rem   (investigated 2026-08-13). Chinese is safe in echo lines only.
rem ============================================================
setlocal enabledelayedexpansion
set "REPO=%USERPROFILE%\custom-skills"
set "WB_SKILLS=%USERPROFILE%\.workbuddy\skills"


if not exist "%REPO%\.git" (
    echo [sync] 仓库不存在，首次使用请先执行:
    echo        git clone https://github.com/ElliotZhang-cd/custom-skills.git "%REPO%"
    pause
    exit /b 1
)

echo [1/2] pulling latest from GitHub...
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

echo [2/2] 分发自建 skill 到 workbuddy...
for %%s in (analyzing-bigfive analyzing-cognitive-functions analyzing-complex-systems maintaining-llm-wiki defining-products researching-user-costs) do (
    if exist "%REPO%\%%s\SKILL.md" (
        if not exist "%WB_SKILLS%\%%s" mkdir "%WB_SKILLS%\%%s"
        robocopy "%REPO%\%%s" "%WB_SKILLS%\%%s" /E /NFL /NDL /NJH /NJS /NP >nul
        if exist "%WB_SKILLS%\%%s\SKILL.md" (
            echo   [workbuddy] %%s 已同步
        ) else (
            echo   [workbuddy] %%s 同步失败: 目标 SKILL.md 不存在
        )
    ) else (
        echo   [workbuddy] %%s 源缺失: %REPO%\%%s\SKILL.md
    )
)

echo [sync] 完成。workbuddy 已分发。下次启动即生效。
pause
