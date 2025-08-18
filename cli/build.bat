@echo off
REM FocusForge CLI Build Script for Windows

echo 🚀 Building FocusForge CLI...

REM Check if Go is installed
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Go is not installed. Please install Go 1.21 or later.
    pause
    exit /b 1
)

REM Check Go version
for /f "tokens=3" %%i in ('go version') do set GO_VERSION=%%i
set GO_VERSION=%GO_VERSION:go=%

echo ✅ Go version %GO_VERSION% detected

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist focusforge-cli.exe del focusforge-cli.exe

REM Install dependencies
echo 📦 Installing dependencies...
go mod tidy
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Build for Windows
echo 🔨 Building CLI...
go build -o focusforge-cli.exe -ldflags="-s -w" .
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

REM Check if build was successful
if exist focusforge-cli.exe (
    echo ✅ Build successful!
    echo 📁 Binary: focusforge-cli.exe
    dir focusforge-cli.exe
    echo.
    echo 🎉 You can now run the CLI with:
    echo    focusforge-cli.exe
) else (
    echo ❌ Build failed - binary not found
    pause
    exit /b 1
)

pause
