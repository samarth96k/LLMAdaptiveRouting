#!/bin/bash
# Quick Start Script for Resilient Experiments (Linux/Mac)

echo ""
echo "============================================================"
echo "  EPICS PROJECT - RESILIENT EXPERIMENT RUNNER"
echo "============================================================"
echo ""
echo "This will run the full 150-task experiment suite with:"
echo "  - Automatic checkpoint saving"
echo "  - Rate limit handling"
echo "  - Provider fallback"
echo "  - Error recovery"
echo ""
echo "Estimated time: 3-4 hours"
echo ""

read -p "Start resilient experiment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Starting resilient experiments..."
echo ""
echo "Monitor progress in another terminal with:"
echo "  python monitor_progress.py --watch"
echo ""

python run.py resilient

if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "  EXPERIMENT INTERRUPTED OR FAILED"
    echo "============================================================"
    echo ""
    echo "Progress has been saved to checkpoints."
    echo "Resume with:"
    echo "  python run.py resilient --resume"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "  EXPERIMENTS COMPLETE!"
    echo "============================================================"
    echo ""
    echo "Check results in data/results/"
    echo ""
fi
