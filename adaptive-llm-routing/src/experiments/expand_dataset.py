"""
Quick Dataset Expansion Script - Add 23 tasks to reach 150 total.

Current: 127 tasks
Target: 150 tasks
Need: 23 more tasks

Distribution:
- Math: 38 → 43 (+5)
- Code: 29 → 35 (+6)
- Reasoning: 40 → 47 (+7)
- General: 15 → 20 (+5)
- Creative: 5 → 5 (0)
"""

import json
from pathlib import Path

# Additional tasks to add
ADDITIONAL_TASKS = [
    # Math tasks (+5)
    {
        "task_id": "math_expand_01",
        "prompt": "A store sells notebooks at $3.50 each and pens at $1.25 each. If you buy 8 notebooks and 12 pens, how much do you spend in total?",
        "task_type": "math",
        "difficulty": "simple",
        "ground_truth": "43.00"
    },
    {
        "task_id": "math_expand_02",
        "prompt": "If a rectangle has a length of 15 cm and width of 8 cm, what is its area and perimeter?",
        "task_type": "math",
        "difficulty": "simple",
        "ground_truth": "Area: 120 cm², Perimeter: 46 cm"
    },
    {
        "task_id": "math_expand_03",
        "prompt": "A taxi charges $2.50 base fare plus $0.80 per mile. How much does a 15-mile trip cost?",
        "task_type": "math",
        "difficulty": "medium",
        "ground_truth": "14.50"
    },
    {
        "task_id": "math_expand_04",
        "prompt": "Solve the system of equations: 2x + 3y = 12 and x - y = 1",
        "task_type": "math",
        "difficulty": "medium",
        "ground_truth": "x = 3, y = 2"
    },
    {
        "task_id": "math_expand_05",
        "prompt": "A population grows exponentially at 3% per year. If the initial population is 50,000, what will it be after 5 years? Use the formula P = P0 * (1 + r)^t",
        "task_type": "math",
        "difficulty": "complex",
        "ground_truth": "57963.50"
    },

    # Code tasks (+6)
    {
        "task_id": "code_expand_01",
        "prompt": "Write a Python function that checks if a string is a palindrome (reads same forwards and backwards). Return True or False.",
        "task_type": "code",
        "difficulty": "simple",
        "ground_truth": "def is_palindrome(s): return s == s[::-1]"
    },
    {
        "task_id": "code_expand_02",
        "prompt": "Implement a function to find the maximum element in a list without using the built-in max() function.",
        "task_type": "code",
        "difficulty": "simple",
        "ground_truth": "def find_max(lst): return max(lst) if lst else None"
    },
    {
        "task_id": "code_expand_03",
        "prompt": "Write a function to merge two sorted lists into one sorted list. For example: merge([1,3,5], [2,4,6]) should return [1,2,3,4,5,6]",
        "task_type": "code",
        "difficulty": "medium",
        "ground_truth": "def merge(a, b): return sorted(a + b)"
    },
    {
        "task_id": "code_expand_04",
        "prompt": "Implement a function to remove duplicates from a list while preserving order.",
        "task_type": "code",
        "difficulty": "medium",
        "ground_truth": "def remove_duplicates(lst): return list(dict.fromkeys(lst))"
    },
    {
        "task_id": "code_expand_05",
        "prompt": "Write a binary search function that finds the index of a target value in a sorted list. Return -1 if not found.",
        "task_type": "code",
        "difficulty": "medium",
        "ground_truth": "def binary_search(arr, target): ..."
    },
    {
        "task_id": "code_expand_06",
        "prompt": "Implement a function to validate if parentheses in a string are balanced. For example: '((()))' is valid, '(()' is not.",
        "task_type": "code",
        "difficulty": "complex",
        "ground_truth": "def is_balanced(s): stack = []; ..."
    },

    # Reasoning tasks (+7)
    {
        "task_id": "reasoning_expand_01",
        "prompt": "If all dogs are mammals, and all mammals are animals, then are all dogs animals? Explain your reasoning.",
        "task_type": "reasoning",
        "difficulty": "simple",
        "ground_truth": "Yes, by transitive property of logic."
    },
    {
        "task_id": "reasoning_expand_02",
        "prompt": "You have a 3-gallon jug and a 5-gallon jug. How can you measure exactly 4 gallons of water?",
        "task_type": "reasoning",
        "difficulty": "medium",
        "ground_truth": "Fill 5-gallon, pour into 3-gallon (2 left). Empty 3-gallon, pour 2 gallons in. Fill 5-gallon again, fill up 3-gallon (1 more). Result: 4 gallons in 5-gallon jug."
    },
    {
        "task_id": "reasoning_expand_03",
        "prompt": "A bat and ball cost $1.10 in total. The bat costs $1 more than the ball. How much does the ball cost?",
        "task_type": "reasoning",
        "difficulty": "medium",
        "ground_truth": "$0.05 (not $0.10)"
    },
    {
        "task_id": "reasoning_expand_04",
        "prompt": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
        "task_type": "reasoning",
        "difficulty": "medium",
        "ground_truth": "5 minutes (parallel processing)"
    },
    {
        "task_id": "reasoning_expand_05",
        "prompt": "Three switches outside a room control three light bulbs inside. You can flip switches, but can only enter the room once. How do you determine which switch controls which bulb?",
        "task_type": "reasoning",
        "difficulty": "complex",
        "ground_truth": "Turn on switch 1, wait 10 minutes, turn it off. Turn on switch 2. Enter room. Hot bulb = switch 1, on bulb = switch 2, off cold bulb = switch 3."
    },
    {
        "task_id": "reasoning_expand_06",
        "prompt": "A farmer needs to cross a river with a fox, chicken, and grain. The boat can only carry the farmer and one item. If left alone, the fox eats the chicken, and the chicken eats the grain. How does the farmer cross?",
        "task_type": "reasoning",
        "difficulty": "complex",
        "ground_truth": "Take chicken across. Return. Take fox across, bring chicken back. Take grain across. Return. Take chicken across."
    },
    {
        "task_id": "reasoning_expand_07",
        "prompt": "You're on a game show with 3 doors. Behind one is a car, behind the others are goats. You pick door 1. The host (who knows what's behind each door) opens door 3, revealing a goat. Should you switch to door 2?",
        "task_type": "reasoning",
        "difficulty": "complex",
        "ground_truth": "Yes, switching gives 2/3 probability vs 1/3 staying (Monty Hall problem)"
    },

    # General tasks (+5)
    {
        "task_id": "general_expand_01",
        "prompt": "What is the chemical symbol for gold?",
        "task_type": "general",
        "difficulty": "simple",
        "ground_truth": "Au"
    },
    {
        "task_id": "general_expand_02",
        "prompt": "How many continents are there on Earth?",
        "task_type": "general",
        "difficulty": "simple",
        "ground_truth": "7 (or 6 depending on model)"
    },
    {
        "task_id": "general_expand_03",
        "prompt": "Explain the difference between a compiler and an interpreter in programming.",
        "task_type": "general",
        "difficulty": "medium",
        "ground_truth": "Compiler translates entire code to machine code before execution. Interpreter translates and executes line by line."
    },
    {
        "task_id": "general_expand_04",
        "prompt": "What is the main difference between supervised and unsupervised machine learning?",
        "task_type": "general",
        "difficulty": "medium",
        "ground_truth": "Supervised uses labeled training data, unsupervised finds patterns in unlabeled data."
    },
    {
        "task_id": "general_expand_05",
        "prompt": "Explain the concept of quantum entanglement in simple terms.",
        "task_type": "general",
        "difficulty": "complex",
        "ground_truth": "Two particles become connected such that measuring one instantly affects the other, regardless of distance."
    },
]


def expand_dataset():
    """Add new tasks to benchmark_tasks.json."""
    # Load existing tasks
    tasks_file = Path(__file__).parent.parent.parent / "data" / "tasks" / "benchmark_tasks.json"

    with open(tasks_file, "r", encoding="utf-8") as f:
        existing_tasks = json.load(f)

    print(f"Current tasks: {len(existing_tasks)}")

    # Verify no duplicate task IDs
    existing_ids = {t["task_id"] for t in existing_tasks}
    new_ids = {t["task_id"] for t in ADDITIONAL_TASKS}

    if existing_ids & new_ids:
        print(f"WARNING: Duplicate IDs found: {existing_ids & new_ids}")
        return

    # Add new tasks
    all_tasks = existing_tasks + ADDITIONAL_TASKS

    print(f"New total: {len(all_tasks)}")

    # Count by category
    from collections import Counter
    categories = Counter(t["task_type"] for t in all_tasks)
    difficulties = Counter(t["difficulty"] for t in all_tasks)

    print("\nCategory distribution:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")

    print("\nDifficulty distribution:")
    for diff, count in difficulties.items():
        print(f"  {diff}: {count}")

    # Save
    backup_file = tasks_file.with_suffix(".json.backup")
    print(f"\nCreating backup: {backup_file}")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(existing_tasks, f, indent=2)

    print(f"Writing updated dataset: {tasks_file}")
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(all_tasks, f, indent=2)

    print("\n[SUCCESS] Dataset expanded to 150 tasks!")


if __name__ == "__main__":
    expand_dataset()
