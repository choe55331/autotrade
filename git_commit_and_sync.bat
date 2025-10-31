@echo off
REM ============================================================
REM Git Commit and Sync Script
REM Commit all changes with a message, then sync with remote
REM ============================================================

echo.
echo ========================================
echo    Git Commit and Sync
echo ========================================
echo.

REM Check if commit message is provided
if "%~1"=="" (
    echo ERROR: Please provide a commit message
    echo Usage: git_commit_and_sync.bat "Your commit message here"
    echo.
    pause
    exit /b 1
)

set COMMIT_MSG=%~1

REM Get current branch name
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
echo Current branch: %BRANCH%
echo Commit message: %COMMIT_MSG%
echo.

REM Step 1: Add all changes
echo [1/5] Staging all changes...
git add -A
if errorlevel 1 (
    echo ✗ Failed to stage changes
    pause
    exit /b 1
)
echo ✓ All changes staged
echo.

REM Step 2: Commit changes
echo [2/5] Committing changes...
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo ✗ Failed to commit (maybe no changes to commit?)
    pause
    exit /b 1
)
echo ✓ Commit successful
echo.

REM Step 3: Fetch latest changes from remote
echo [3/5] Fetching latest changes from remote...
git fetch origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to fetch from remote
    pause
    exit /b 1
)
echo ✓ Fetch successful
echo.

REM Step 4: Pull with rebase
echo [4/5] Pulling latest changes with rebase...
git pull --rebase origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to pull. You may have merge conflicts.
    echo Please resolve conflicts manually.
    pause
    exit /b 1
)
echo ✓ Pull successful
echo.

REM Step 5: Push to remote
echo [5/5] Pushing to remote...
git push origin %BRANCH%
if errorlevel 1 (
    echo ✗ Failed to push to remote
    pause
    exit /b 1
)
echo ✓ Push successful
echo.

echo ========================================
echo    Commit and Sync Complete! ✓
echo ========================================
echo.
pause
