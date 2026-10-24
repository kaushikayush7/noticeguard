@echo off
set LOCALHOST=%COMPUTERNAME%
if /i "%LOCALHOST%"=="ayush" (taskkill /f /pid 15928)
if /i "%LOCALHOST%"=="ayush" (taskkill /f /pid 5880)
if /i "%LOCALHOST%"=="ayush" (taskkill /f /pid 23592)
if /i "%LOCALHOST%"=="ayush" (taskkill /f /pid 17812)

del /F cleanup-ansys-ayush-17812.bat
