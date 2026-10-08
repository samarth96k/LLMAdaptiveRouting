# Dataset Strategy

## Sources

1. GSM8K (math reasoning)
2. Logical reasoning benchmarks
3. Code generation datasets
4. Custom curated prompts
5. Research paper abstracts

---

## Custom Dataset Creation

Create balanced dataset:

- 100 simple tasks
- 100 medium tasks
- 100 complex tasks

Annotate:
- True answer
- Complexity label
- Reasoning depth

---

## Data Storage

Store in structured JSON:

{
  "task_id": "",
  "prompt": "",
  "task_type": "",
  "difficulty": "",
  "ground_truth": ""
}
