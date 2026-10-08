@echo off
REM Quick Start Script for Resilient Experiments (Windows)

echo.
echo ============================================================
echo   EPICS PROJECT - RESILIENT EXPERIMENT RUNNER
echo ============================================================
echo.
echo This will run the full 150-task experiment suite with:
echo   - Automatic checkpoint saving
echo   - Rate limit handling
echo   - Provider fallback
echo   - Error recovery
echo.
echo Estimated time: 3-4 hours
echo.

set /p confirm="Start resilient experiment? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo Cancelled.
    exit /b 0
)

echo.
echo Starting resilient experiments...
echo.
echo Monitor progress in another terminal with:
echo   python monitor_progress.py --watch
echo.

python run.py resilient

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   EXPERIMENT INTERRUPTED OR FAILED
    echo ============================================================
    echo.
    echo Progress has been saved to checkpoints.
    echo Resume with:
    echo   python run.py resilient --resume
    echo.
    pause
) else (
    echo.
    echo ============================================================
    echo   EXPERIMENTS COMPLETE!
    echo ============================================================
    echo.
    echo Check results in data/results/
    echo.
    pause
)
