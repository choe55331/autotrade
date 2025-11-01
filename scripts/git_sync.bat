@echo off
REM ============================================================
REM Git Auto Sync Script
REM Automatically pull latest changes and push your commits
REM ============================================================

echo.
echo ========================================
echo    Git Auto Sync
echo ========================================
echo.

REM Get current branch name
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
echo Current branch: %BRANCH%
echo.

REM Step 1: Check for uncommitted changes
echo [1/4] Checking for uncommitted changes...
git diff --quiet
if errorlevel 1 (
    echo WARNING: You have uncommitted changes!
    echo Please commit or stash them first.
    pause
    exit /b 1
)
echo ✓ No uncommitted changes
echo.

REM Step 2: Fetch latest changes from remote
echo [2/4] Fetching latest changes from remote...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to fetch from remote
    pause
    exit /b 1
)
echo ✓ Fetch successful
echo.

REM Step 3: Pull with rebase
echo [3/4] Pulling latest changes with rebase...
git pull --rebase origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to pull. You may have merge conflicts.
    echo Please resolve conflicts manually.
    pause
    exit /b 1
)
echo ✓ Pull successful
echo.

REM Step 4: Push local commits
echo [4/4] Pushing your commits to remote...
git push origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to push to remote
    pause
    exit /b 1
)
echo ✓ Push successful
echo.

echo ========================================
echo    Sync Complete! ✓
echo ========================================
echo.
pause
