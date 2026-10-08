# Resilient Experiment Mode

## Overview

The resilient mode provides **fault-tolerant experiment execution** with automatic recovery from failures, rate limits, and interruptions.

## Key Features

### 1. **Checkpoint System**
- Saves progress after every 5 tasks
- Resume from exact point of failure
- No re-running completed tasks

### 2. **Auto-Retry with Backoff**
- Up to 5 retries per task
- Exponential backoff (5s, 10s, 20s, 40s, 80s)
- Special handling for rate limits (60s wait)

### 3. **Provider Fallback Chain**
- Automatically switches providers on failure
- Order: Groq → Mistral → HuggingFace → Gemini
- Tracks failures per provider

### 4. **Error Logging**
- Detailed error logs in `checkpoints/` directory
- Tracks retry counts and provider failures
- JSONL format for easy analysis

### 5. **Progress Tracking**
- Real-time progress display
- Time elapsed tracking
- Percentage completion

## Usage

### Start New Resilient Run
```bash
cd adaptive-llm-routing
python run.py resilient
```

### Resume from Checkpoint
If experiment crashes or is interrupted:
```bash
python run.py resilient --resume
```

### Monitor Progress
Check real-time progress:
```bash
# View checkpoint status
cat data/results/run2_result/checkpoints/exp1_single_llm_progress.json

# View errors
cat data/results/run2_result/checkpoints/exp1_single_llm_errors.jsonl
```

## File Structure

```
data/results/run2_result/
├── checkpoints/
│   ├── exp1_single_llm_checkpoint.json      # Full checkpoint data
│   ├── exp1_single_llm_progress.json        # Progress summary
│   ├── exp1_single_llm_errors.jsonl         # Error log
│   ├── exp2_multi_agent_checkpoint.json
│   ├── exp2_multi_agent_progress.json
│   ├── exp2_multi_agent_errors.jsonl
│   ├── exp3_adaptive_checkpoint.json
│   ├── exp3_adaptive_progress.json
│   └── exp3_adaptive_errors.jsonl
├── exp1_single_llm.json                     # Final results
├── exp2_multi_agent.json
├── exp3_adaptive.json
├── experiment_comparison.json
└── figures/
    └── *.png
```

## Checkpoint Format

### Progress File (`*_progress.json`)
```json
{
  "experiment": "exp1_single_llm",
  "completed": 45,
  "total": 150,
  "percentage": 30.0,
  "remaining": 105,
  "timestamp": "2026-03-25T14:30:00"
}
```

### Checkpoint File (`*_checkpoint.json`)
```json
{
  "experiment_name": "exp1_single_llm",
  "timestamp": "2026-03-25T14:30:00",
  "completed_count": 45,
  "total_tasks": 150,
  "completed_indices": [0, 1, 2, ..., 44],
  "results": [
    {
      "task_id": "math_001",
      "response": "...",
      "accuracy_score": 0.85,
      ...
    },
    ...
  ],
  "metadata": {}
}
```

### Error Log (`*_errors.jsonl`)
Each line is a JSON object:
```json
{"timestamp": "2026-03-25T14:25:00", "experiment": "exp1_single_llm", "task_id": "code_042", "task_index": 42, "error": "RateLimitError: 429", "provider": "groq", "retry_count": 5}
```

## Error Handling

### Rate Limit Errors
- **Detection**: Automatic detection of rate limit patterns
- **Response**: 60s wait, then retry
- **Fallback**: Switch to next provider if repeated

### Network Errors
- **Retries**: Up to 5 attempts with exponential backoff
- **Wait times**: 5s, 10s, 20s, 40s, 80s
- **Fallback**: Provider switching after exhausting retries

### Permanent Failures
- **Behavior**: Task marked as failed after all retries
- **Logging**: Full error details in error log
- **Continue**: Experiment continues with remaining tasks
- **Result**: Failed tasks get `{"failed": true, "error": "..."}` in results

## Recovery Scenarios

### Scenario 1: Rate Limit Hit
```
Task 42/150: Rate limit hit on Groq
  → Wait 60s
  → Retry with Groq
  → If fails again, switch to Mistral
  → Continue from Task 43
```

### Scenario 2: Network Failure
```
Task 78/150: Network error
  → Retry 1/5 in 5s
  → Retry 2/5 in 10s
  → ...
  → Success on retry 3
  → Continue from Task 79
```

### Scenario 3: Crash/Interrupt
```
Completed: 105/150 tasks
  → User presses Ctrl+C
  → Checkpoint saved
  → Resume with: python run.py resilient --resume
  → Starts from Task 106
```

### Scenario 4: Provider Outage
```
Task 30/150: Groq unavailable
  → Try Mistral
  → Success
  → Continue with Mistral
  → Auto-switch back to Groq when available
```

## Best Practices

### 1. Use Resilient Mode for Production Runs
- For 150-task experiments (3+ hours)
- When using free-tier APIs
- For overnight/unattended runs

### 2. Monitor Progress
```bash
# Watch progress in real-time (Linux/Mac)
watch -n 5 'cat data/results/run2_result/checkpoints/exp1_single_llm_progress.json'

# Windows PowerShell
while($true) {
  Clear-Host
  Get-Content data/results/run2_result/checkpoints/exp1_single_llm_progress.json
  Start-Sleep -Seconds 5
}
```

### 3. Check Error Logs
```bash
# View errors
cat data/results/run2_result/checkpoints/exp1_single_llm_errors.jsonl

# Count errors by provider
grep -o '"provider":"[^"]*"' exp1_single_llm_errors.jsonl | sort | uniq -c
```

### 4. Resume After Fixing Issues
```bash
# Example: Fixed API key issue
python run.py resilient --resume
```

## Performance Impact

### Overhead
- **Checkpoint write**: ~50ms every 5 tasks
- **Progress tracking**: ~10ms per task
- **Error logging**: ~5ms on error

### Total Impact
- ~0.3% overhead on 150-task run (~20 seconds total)
- Negligible compared to 3-hour runtime

## Comparison: Regular vs Resilient

| Feature | Regular Mode | Resilient Mode |
|---------|-------------|----------------|
| Resume on crash | ❌ No | ✅ Yes |
| Rate limit handling | Basic retry | Smart backoff + fallback |
| Error logging | Console only | Persistent JSONL |
| Progress tracking | None | Real-time files |
| Provider fallback | Manual | Automatic |
| Overhead | 0% | <0.3% |
| Recovery time | Hours (restart) | Seconds (resume) |

## Troubleshooting

### "No checkpoint found"
- Normal if first run
- Check `checkpoints/` directory exists

### "Failed to load checkpoint"
- Checkpoint file corrupted
- Delete checkpoint and restart:
  ```bash
  rm data/results/run2_result/checkpoints/exp*_checkpoint.json
  python run.py resilient
  ```

### Resume not working
- Verify you're in correct directory
- Check checkpoint files exist:
  ```bash
  ls -la data/results/run2_result/checkpoints/
  ```

### All providers failing
- Check API keys in `.env`
- Verify rate limits not exceeded:
  - Groq: 14,400 req/day per account
  - Mistral: 1M tokens/month
  - HuggingFace: 1,000 req/hour

## Implementation Details

### Checkpoint Manager
- **Class**: `CheckpointManager` in `src/experiments/checkpoint_manager.py`
- **Methods**:
  - `save_checkpoint()` - Save progress
  - `load_checkpoint()` - Resume from save
  - `log_error()` - Record failures
  - `get_remaining_indices()` - Calculate what's left

### Provider Fallback Chain
- **Class**: `ProviderFallbackChain`
- **Order**: Groq → Mistral → HuggingFace → Gemini
- **Detection**: Pattern matching on error messages
- **Reset**: Automatic on success

### Resilient Runner
- **Class**: `ResilientExperimentRunner` in `src/experiments/run_full_resilient.py`
- **Retry logic**: Exponential backoff
- **Max retries**: 5 attempts per task
- **Checkpointing**: Every 5 tasks + final

## Future Enhancements

Potential improvements (not yet implemented):
- [ ] Parallel task execution with checkpointing
- [ ] Automatic cost estimation before resume
- [ ] Email/webhook notifications on failures
- [ ] Dashboard for monitoring multiple runs
- [ ] Checkpoint compression for large datasets
- [ ] Provider health checks before retry

## Summary

**Use resilient mode for:**
- ✅ Long-running experiments (>1 hour)
- ✅ Free-tier API usage
- ✅ Unattended/overnight runs
- ✅ Production research runs

**Use regular mode for:**
- ✅ Quick validation (<15 tasks)
- ✅ Development/debugging
- ✅ Paid API tiers (reliable)
- ✅ Fast feedback loops

---

**Start your resilient run now:**
```bash
cd adaptive-llm-routing
python run.py resilient
```
