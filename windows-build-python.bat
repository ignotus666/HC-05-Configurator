@echo off
REM windows-build-python.bat: Clean build, version extraction, PyInstaller, and NSIS packaging

REM Clean previous build artifacts
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Extract version from debian/control
for /f "tokens=2 delims=: " %%A in ('findstr /B /C:"Version:" debian\control') do set VERSION=%%A
set VERSION=%VERSION: =%

REM Ensure VERSION is in X.X.X.X format for NSIS
for /f "tokens=1-4 delims=." %%a in ("%VERSION%") do (
    set V1=%%a
    set V2=%%b
    set V3=%%c
    set V4=%%d
)
if "%V2%"=="" set V2=0
if "%V3%"=="" set V3=0
if "%V4%"=="" set V4=0
set VERSION_NSI=%V1%.%V2%.%V3%.%V4%

REM Build the .exe with PyInstaller (from src/main.py)
pyinstaller --onefile --windowed --add-data ".\hc-05.ico;." --name "HC-05 Configurator" src\main.py

REM Copy .ico, .nsi, and LICENSE files into dist for NSIS
copy .\hc-05.ico dist\
copy installer.nsi dist\
copy LICENSE dist\

REM Run NSIS, passing the version as a define (run from dist so files are found)
pushd dist
makensis /DVERSION=%VERSION% /DVERSION_NSI=%VERSION_NSI% installer.nsi
popd

echo Build complete: dist\HC-05 Configurator.exe and setup executable created.
pause
