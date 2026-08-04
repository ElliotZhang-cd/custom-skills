@echo off
chcp 65001 >nul
rem ============================================================
rem sync-windows.bat - Windows 侧同步 custom-skills 并分发
rem 真相源: WSL ~/custom-skills -> GitHub -> 本脚本 (pull + 分发)
rem 用法: 双击运行，或加入任务计划定期执行
rem 注意: UTF-8 编码 + CRLF 行尾 + chcp 65001（否则中文乱码）
rem ============================================================
setlocal enabledelayedexpansion
set "REPO=%USERPROFILE%\custom-skills"
set "WB_SKILLS=%USERPROFILE%\.workbuddy\skills"
set "HERMES_CFG=%USERPROFILE%\AppData\Local\hermes\config.yaml"

if not exist "%REPO%\.git" (
    echo [sync] 仓库不存在，首次使用请先执行:
    echo        git clone https://github.com/ElliotZhang-cd/custom-skills.git "%REPO%"
    pause
    exit /b 1
)

echo [1/3] pulling latest from GitHub...
cd /d "%REPO%"
git pull --ff-only origin master
if !errorlevel! neq 0 (
    echo [sync] pull 失败，请检查网络/代理
    pause
    exit /b 1
)
for /f "delims=" %%v in ('git log -1 --oneline') do echo [sync] 当前版本: %%v

echo [2/3] 分发自建 skill 到 workbuddy...
for %%s in (analyzing-bigfive analyzing-cognitive-functions analyzing-complex-systems maintaining-llm-wiki) do (
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

echo [3/3] 校验 hermes 配置...
if exist "%HERMES_CFG%" (
    if exist "%REPO%\maintaining-llm-wiki\SKILL.md" (
        findstr /I /C:"custom-skills" "%HERMES_CFG%" >nul
        if !errorlevel! equ 0 (
            echo   [hermes] external_dirs 已配置，直接读取 %REPO%（无需复制，避免旧版遮蔽）
        ) else (
            echo   [hermes] 警告: external_dirs 未指向当前仓库，请检查 %HERMES_CFG%
        )
    ) else (
        echo   [hermes] 警告: 仓库内容不完整（缺 SKILL.md）
    )
) else (
    echo   [hermes] 警告: 未找到 config.yaml
)

echo [sync] 完成。hermes 直接读仓库已最新；workbuddy 已分发。下次启动即生效。
pause
