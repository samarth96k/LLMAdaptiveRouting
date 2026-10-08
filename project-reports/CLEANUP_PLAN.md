# GitHub Organization Cleanup Plan

## Current Issues
1. Multiple redundant run scripts (run_full.py, run_full_resilient.py, run_quick.py)
2. Temporary utility files (convert_to_word.py)
3. Old/redundant documentation files
4. Disorganized root directory

## Actions to Take

### 1. REMOVE Files
- ❌ `/convert_to_word.py` - Temporary utility, not needed
- ❌ `/docs/research_report.md` - Redundant with papers/
- ❌ `/adaptive-llm-routing/EPICS_Report_Phase1.md` - Old phase 1 report

### 2. CONSOLIDATE Run Scripts
**Problem:** 4 different run scripts with overlapping functionality
- run_experiments.py (main orchestrator)
- run_full.py (full benchmark)
- run_full_resilient.py (resilient full benchmark)
- run_quick.py (quick validation)

**Solution:** Create unified `run.py` entry point with modes:
```bash
python run.py quick          # Quick validation (15 tasks)
python run.py full           # Full benchmark (150 tasks)
python run.py full --resilient  # Full with checkpointing
python run.py single         # Run single task
```

**Implementation:**
- Keep `run_experiments.py` as the core engine
- Update `/adaptive-llm-routing/run.py` to be the CLI dispatcher
- Remove `run_full.py` and `run_full_resilient.py`
- Keep `run_quick.py` but integrate into run.py

### 3. MOVE Files to Archive
- `/FINAL_STRUCTURE.md` → `/docs/archive/FINAL_STRUCTURE.md`
- `/docs/SPRINT_EXECUTION_PLAN.md` → `/docs/archive/SPRINT_EXECUTION_PLAN.md`

### 4. FINAL CLEAN STRUCTURE

```
EPICS-Project/
├── README.md                          # Main project overview
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── .env.example                       # API key template
│
├── PROJECT_REPORT.md                  # Academic report (Markdown)
├── PROJECT_REPORT.docx                # Academic report (Word)
├── INDIVIDUAL_CONTRIBUTIONS.md        # Team contributions (Markdown)
├── INDIVIDUAL_CONTRIBUTIONS.docx      # Team contributions (Word)
│
├── papers/                            # Research papers
│   ├── RESEARCH_PAPER.md              # Main research paper
│   ├── RESEARCH_PAPER.tex             # LaTeX version
│   └── SUPPLEMENTARY_MATERIALS.md     # Supplementary materials
│
├── docs/                              # Documentation
│   └── archive/                       # Archived planning docs
│       ├── FINAL_STRUCTURE.md
│       ├── SPRINT_EXECUTION_PLAN.md
│       ├── REALISTIC_RESEARCH_PLAN.md
│       ├── RESEARCH_IMPROVEMENT_PLAN.md
│       └── planning/
│           ├── dataset_strategy.md
│           ├── evaluation_metrics.md
│           ├── experiment_design.md
│           ├── implementation_plan.md
│           ├── product_Demo_notes.md
│           ├── research_plan.md
│           └── system_architecture.md
│
└── adaptive-llm-routing/              # Main codebase
    ├── README.md                      # Project-specific README
    ├── RESILIENT_MODE.md              # Fault tolerance docs
    ├── run.py                         # CLI entry point (UPDATED)
    ├── monitor_progress.py            # Progress monitoring tool
    │
    ├── src/                           # Source code
    │   ├── main.py                    # Programmatic entry point
    │   ├── config.py                  # Configuration
    │   ├── llm_provider.py            # Multi-provider interface
    │   │
    │   ├── agents/                    # Execution agents
    │   │   ├── single_llm.py
    │   │   └── multi_agent.py
    │   │
    │   ├── graph/                     # LangGraph workflow
    │   │   ├── state.py
    │   │   ├── builder.py
    │   │   └── nodes.py
    │   │
    │   ├── utils/                     # Utilities
    │   │   └── complexity.py
    │   │
    │   ├── evaluation/                # Evaluation framework
    │   │   ├── metrics.py
    │   │   ├── statistics.py
    │   │   └── feedback.py
    │   │
    │   └── experiments/               # Experiment infrastructure
    │       ├── dataset_generator.py
    │       ├── run_experiments.py     # Core orchestrator (KEEP)
    │       ├── checkpoint_manager.py
    │       ├── generate_visuals.py
    │       └── expand_dataset.py
    │
    ├── tests/                         # Test suite
    │   ├── test_graph.py
    │   └── test_providers.py
    │
    ├── examples/                      # Example scripts
    │   └── analyze_results.py
    │
    ├── dashboard/                     # Streamlit dashboard
    │   └── app.py
    │
    └── data/                          # Data directory
        ├── tasks/
        │   └── benchmark_tasks.json
        └── results/
            └── figures/
```

## Files Status Summary

### Keep (Essential)
✅ README.md (root)
✅ LICENSE
✅ requirements.txt
✅ .gitignore
✅ .env.example
✅ PROJECT_REPORT.md/docx
✅ INDIVIDUAL_CONTRIBUTIONS.md/docx
✅ papers/ (all files)
✅ adaptive-llm-routing/src/ (all source code)
✅ adaptive-llm-routing/tests/
✅ adaptive-llm-routing/examples/
✅ adaptive-llm-routing/dashboard/
✅ adaptive-llm-routing/run.py (update)
✅ adaptive-llm-routing/monitor_progress.py
✅ adaptive-llm-routing/README.md
✅ adaptive-llm-routing/RESILIENT_MODE.md

### Remove
❌ convert_to_word.py
❌ docs/research_report.md
❌ adaptive-llm-routing/EPICS_Report_Phase1.md
❌ adaptive-llm-routing/src/experiments/run_full.py (consolidate)
❌ adaptive-llm-routing/src/experiments/run_full_resilient.py (consolidate)
❌ adaptive-llm-routing/src/experiments/run_quick.py (consolidate)

### Move to Archive
📦 FINAL_STRUCTURE.md → docs/archive/
📦 docs/SPRINT_EXECUTION_PLAN.md → docs/archive/

## Implementation Steps

1. Update `/adaptive-llm-routing/run.py` with unified CLI
2. Remove redundant files
3. Move files to archive
4. Update README if needed
5. Verify all imports still work
6. Test quick run to ensure nothing broke
7. Update .gitignore if needed
8. Create final verification checklist

## Verification Checklist

After cleanup:
- [ ] `python adaptive-llm-routing/run.py quick` works
- [ ] `python adaptive-llm-routing/run.py full` works
- [ ] Dashboard launches: `streamlit run adaptive-llm-routing/dashboard/app.py`
- [ ] Tests pass: `pytest adaptive-llm-routing/tests/`
- [ ] All imports resolve correctly
- [ ] README instructions are up-to-date
- [ ] No broken file references in code
- [ ] .gitignore covers all necessary files
