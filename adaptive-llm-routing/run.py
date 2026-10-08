"""
Main entry point for the Adaptive LLM Routing System.

Phase 1 execution modes:

    quick
        Run a small benchmark for quick testing.

    full
        Run the complete Phase 1 experiment suite.
"""

import sys


def print_usage():
    """Print command-line usage information."""

    print()
    print("Adaptive LLM Routing System")
    print()
    print("Usage:")
    print("    python run.py quick")
    print("    python run.py full")
    print()
    print("Modes:")
    print("    quick  - Run a small benchmark")
    print("    full   - Run the complete experiment suite")
    print()


def run_quick():
    """Run the quick Phase 1 benchmark."""

    from src.experiments.run_quick import main

    main()


def run_full():
    """Run the complete Phase 1 experiment suite."""

    from src.experiments.run_full import main

    main()


def main():
    """Main command-line entry point."""

    if len(sys.argv) < 2:
        print_usage()
        return

    mode = sys.argv[1].lower().strip()

    if mode == "quick":
        run_quick()

    elif mode == "full":
        run_full()

    else:
        print(
            f"Unknown mode: {mode}"
        )
        print_usage()


if __name__ == "__main__":
    main()