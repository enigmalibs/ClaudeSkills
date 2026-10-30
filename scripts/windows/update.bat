@echo off
rem Runs update.ps1 from this folder with the execution policy bypassed for this run only,
rem passing every argument through:  update.bat -DryRun
setlocal
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1" %*
set "UPDATE_EXIT=%ERRORLEVEL%"
rem Started by a double-click (this file's name is in the cmd command line): keep the window
rem open so the output can be read.
echo %CMDCMDLINE% | "%SystemRoot%\System32\find.exe" /i "%~nx0" >nul && pause
exit /b %UPDATE_EXIT%
