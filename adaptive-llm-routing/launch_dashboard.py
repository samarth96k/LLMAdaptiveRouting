#!/usr/bin/env python3
"""
Dashboard Launcher — Ensures correct paths and runs Streamlit dashboard.

Usage: python launch_dashboard.py
"""

import sys
import subprocess
from pathlib import Path

# Get the project directory (adaptive-llm-routing/)
PROJECT_DIR = Path(__file__).resolve().parent

print("=" * 60)
print("🚀 Adaptive LLM Routing Dashboard Launcher")
print("=" * 60)
print()

# Check if we're in the right directory
print(f"📁 Project directory: {PROJECT_DIR}")
print()

# Check if results exist
results_dir = PROJECT_DIR / "data" / "results"
if not results_dir.exists():
    print("❌ Error: Results directory not found!")
    print(f"   Expected: {results_dir}")
    print()
    print("💡 Run experiments first:")
    print("   python run.py quick")
    sys.exit(1)

# Check for result files
result_files = list(results_dir.glob("exp*.json"))
if not result_files:
    print("❌ Error: No experiment results found!")
    print(f"   Looking in: {results_dir}")
    print()
    print("💡 Run experiments first:")
    print("   python run.py quick")
    sys.exit(1)

print(f"✅ Found {len(result_files)} result files:")
for f in result_files:
    size_kb = f.stat().st_size / 1024
    print(f"   - {f.name} ({size_kb:.1f} KB)")
print()

# Check if streamlit is installed
try:
    import streamlit
    print(f"✅ Streamlit installed (version {streamlit.__version__})")
except ImportError:
    print("❌ Error: Streamlit not installed!")
    print()
    print("💡 Install it:")
    print("   pip install streamlit")
    sys.exit(1)

print()
print("=" * 60)
print("🌐 Launching dashboard...")
print("=" * 60)
print()
print("📌 Access the dashboard at:")
print("   Local:   http://localhost:8501")
print("   Network: (will show after launch)")
print()
print("⌨️  Press Ctrl+C to stop the server")
print()

# Change to project directory and launch
dashboard_path = PROJECT_DIR / "dashboard" / "app.py"

try:
    subprocess.run(
        ["streamlit", "run", str(dashboard_path)],
        cwd=str(PROJECT_DIR),
        check=True
    )
except KeyboardInterrupt:
    print("\n\n👋 Dashboard stopped.")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error launching dashboard: {e}")
    sys.exit(1)
