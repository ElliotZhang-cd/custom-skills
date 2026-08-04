@echo off
chcp 65001 >nul
rem 入口脚本：转发到仓库内真相版 sync-windows.bat（自举：pull 后自动获得最新脚本）
call "%~dp0scripts\sync-windows.bat"
