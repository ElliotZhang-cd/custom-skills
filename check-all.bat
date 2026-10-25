@echo off
chcp 65001 >nul
rem ============================================================
rem check-all.bat - run the read-only reconciliation on BOTH ends
rem (Windows native python + WSL python3) in one shot, so "run the
rem audit on each end" no longer depends on memory.
rem Exit code 0 only when both ends pass -- safe to schedule in
rem Task Scheduler or call from a git hook. Comments stay ASCII-only
rem (same cmd multi-byte rule as sync-windows.bat).
rem ============================================================
setlocal enabledelayedexpansion
set "PYTHONUTF8=1"
set "REPO=%USERPROFILE%\custom-skills"

echo [check] Windows 端对账...
python "%REPO%\scripts\check_distribution.py"
set "WIN_RC=!errorlevel!"

echo [check] WSL 端对账...
wsl bash -lc "cd ~/custom-skills && python3 scripts/check_distribution.py"
set "WSL_RC=!errorlevel!"

echo [check] Windows 退出码 !WIN_RC! / WSL 退出码 !WSL_RC!（0=通过）
if not "!WIN_RC!"=="0" goto :fail
if not "!WSL_RC!"=="0" goto :fail
echo [check] 两端全绿。
exit /b 0
:fail
echo [check] 存在缺口：按上方输出处理（失败 = 声明的东西没到位或被顶替；提醒项逐条裁定）。
exit /b 1
