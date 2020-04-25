rem @echo off
rem pushd "c:\Users\THINKPAD\AppData\Local"
rem for /f "delims=" %%a in (' dir /ad /b ') do call :size "%%~fa"
rem sort /r < "%temp%\dirsize.tmp"
rem del "%temp%\dirsize.tmp"
rem popd
rem pause
rem goto :eof

rem :size
rem for /f "tokens=3" %%b in ('dir /s "%~1" 2^>nul ^|find " File(s) "') do set "n=%%b"
rem set dirsize=%n%
rem REM set dirsize=%dirsize:,=%
rem set dirsize=                 %dirsize%
rem set dirsize=%dirsize:~-18%
rem >>"%temp%\dirsize.tmp" echo %dirsize% "%~1"

start cmd /k ".\venv\mpf-dev\Scripts\activate.bat"

