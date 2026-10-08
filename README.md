# Adaptive LLM Routing: Cost-Efficient Complexity Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **A graph-based approach to dynamic model selection that achieves 62% cost reduction and 64% latency improvement while preserving 96% quality.**

This repository contains the complete implementation and research materials for an adaptive LLM routing system that intelligently selects between single-LLM execution and multi-agent pipelines based on real-time complexity analysis.

## Key Results

| Metric | Single-LLM | Multi-Agent | **Adaptive Router** | Improvement |
|--------|-----------|-------------|---------------------|-------------|
| Quality | 0.821 | 0.877 | **0.838** | 95.6% of multi-agent |
| Cost | $0.008 | $0.171 | **$0.065** | **62% reduction** |
| Latency | 2.07s | 21.21s | **7.60s** | **64% faster** |
| Efficiency | 13,026 QPD | 651 QPD | **1,642 QPD** | **2.5× better** |

**Main Achievement**: The adaptive router achieves 96% of multi-agent quality at only 38% of the cost.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Experimental Results](#experimental-results)
- [Research Papers](#research-papers)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

---

## Features

- **Intelligent Routing**: 14-feature heuristic analyzer for complexity estimation
- **Cost Optimization**: 62% cost reduction compared to uniform multi-agent approach
- **Quality Preservation**: Maintains 96% of multi-agent quality
- **No Training Required**: Works out-of-the-box with heuristic-based analysis
- **Fault Tolerant**: Automatic checkpointing, retry logic, and provider fallback
- **Production Ready**: Zero-failure execution on 381 tasks
- **Model Agnostic**: Works with any LLM provider (Groq, OpenAI, Anthropic, etc.)

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/adaptive-llm-routing.git
cd adaptive-llm-routing
```

### 2. Install Dependencies

```bash
cd adaptive-llm-routing
pip install -r requirements.txt
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```bash
# Groq API (primary provider)
GROQ_API_1=your_groq_api_key_1
GROQ_API_2=your_groq_api_key_2

# Additional providers
MISTRAL_API=your_mistral_api_key
HUGGINGFACE_API=your_huggingface_api_key
GOOGLE_API=your_google_api_key
```

### 4. Run Quick Test

```bash
cd adaptive-llm-routing
python run.py quick
```

This runs 15 tasks to validate the setup (~5-8 minutes).

### 5. Run Full Experiment

```bash
python run.py resilient
```

This runs all 127 tasks with full fault tolerance (~90 minutes).

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Task Input                           │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            Complexity Analyzer                           │
│  • 14 linguistic features                                │
│  • Domain signal detection (code, math, reasoning)       │
│  • No training required                                  │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Router Decision                             │
│  • Task-specific thresholds                              │
│  • 75.6% → Single-LLM (cost-efficient)                   │
│  • 24.4% → Multi-Agent (quality-critical)                │
└─────┬───────────────────────────────────────────┬────────┘
      │                                           │
      ▼ (Simple Tasks)                            ▼ (Complex Tasks)
┌──────────────────┐                    ┌──────────────────┐
│  Single-LLM      │                    │  Multi-Agent     │
│  Executor        │                    │  Pipeline        │
│                  │                    │                  │
│ • Llama-3.1-8B   │                    │ • Planner        │
│ • 2.07s latency  │                    │ • Executor       │
│ • $0.00006/task  │                    │ • Verifier       │
└────────┬─────────┘                    └─────────┬────────┘
         │                                        │
         └────────────┬───────────────────────────┘
                      ▼
            ┌──────────────────┐
            │   Evaluation     │
            │  • Accuracy      │
            │  • Quality       │
            │  • Cost/Latency  │
            └──────────────────┘
```

### Complexity Analyzer Features

1. **Lexical Complexity**: Word count, character count, lexical diversity
2. **Semantic Richness**: Information entropy, TF-IDF richness
3. **Syntactic Structure**: Nested clauses, subordinating conjunctions
4. **Domain Signals**: Code patterns, math notation, reasoning indicators
5. **Question Characteristics**: Multi-part questions, comparatives, abstraction level

---

## Installation

### Requirements

- Python 3.8+
- pip

### Dependencies

```bash
pip install langgraph langchain langchain-groq langchain-mistralai langchain-google-genai langchain-huggingface
pip install python-dotenv rich matplotlib seaborn pandas numpy scikit-learn scipy
```

Or use the provided `requirements.txt`:

```bash
cd adaptive-llm-routing
pip install -r requirements.txt
```

---

## Usage

### Running Experiments

**Quick Test (15 tasks, ~8 minutes)**:
```bash
python run.py quick
```

**Full Experiment (127 tasks, ~90 minutes)**:
```bash
python run.py full
```

**Resilient Mode with Checkpointing (recommended)**:
```bash
python run.py resilient
```

**Resume from Checkpoint**:
```bash
python run.py resilient --resume
```

### Monitoring Progress

In another terminal:
```bash
python monitor_progress.py --watch
```

### Analyzing Results

```bash
# View statistical analysis
python examples/analyze_results.py

# Generate visualizations
python -m src.experiments.generate_visuals
```

### Using the System Programmatically

```python
from src.graph.builder import build_adaptive_graph

# Build the routing graph
graph = build_adaptive_graph()

# Run a task
task = {
    "task_id": "example_001",
    "prompt": "Explain the difference between supervised and unsupervised learning.",
    "task_type": "general"
}

result = graph.invoke(task)

print(f"Route: {result['route']}")
print(f"Response: {result['response']}")
print(f"Quality: {result['quality_score']:.3f}")
print(f"Latency: {result['latency_seconds']:.2f}s")
print(f"Cost: ${result['estimated_cost']:.6f}")
```

---

## Experimental Results

### Overall Performance (127 Tasks)

Our adaptive router was evaluated on 127 diverse NLP tasks across 5 domains:

- **Mathematics**: 38 tasks (29.9%)
- **Code Generation**: 29 tasks (22.8%)
- **Logical Reasoning**: 40 tasks (31.5%)
- **General Knowledge**: 15 tasks (11.8%)
- **Creative Writing**: 5 tasks (3.9%)

### Performance by Domain

| Domain | Quality | Latency (s) | Cost (USD) |
|--------|---------|-------------|------------|
| **Mathematics** | **0.945** | 3.49 | 0.000089 |
| **Code** | 0.745 | 15.37 | 0.000512 |
| **Reasoning** | 0.809 | 7.80 | 0.000423 |
| **General** | 0.867 | 4.27 | 0.000234 |
| **Creative** | 0.720 | 2.07 | 0.000067 |

### Routing Distribution

- **75.6%** of tasks routed to single-LLM (cost-efficient)
- **24.4%** of tasks routed to multi-agent (quality-critical)

This distribution demonstrates effective complexity identification.

### Statistical Significance

All improvements are statistically significant (Wilcoxon signed-rank test):

- Adaptive vs Single-LLM quality: p < 0.01
- Adaptive vs Multi-Agent cost: p < 0.001
- Adaptive vs Multi-Agent latency: p < 0.001

---

## Research Papers

### Main Paper

**Title**: Cost-Efficient LLM Routing with Adaptive Complexity Analysis: A Graph-Based Approach to Dynamic Model Selection

**Abstract**: Large Language Models exhibit varying performance-cost tradeoffs across different task complexities. We present an adaptive routing framework that dynamically selects between single-LLM execution and multi-agent pipelines based on real-time complexity analysis. Our system achieves 92% of multi-agent quality while reducing costs by 62% and latency by 73%.

**Full Paper**: See [papers/RESEARCH_PAPER.md](papers/RESEARCH_PAPER.md) or [papers/RESEARCH_PAPER.tex](papers/RESEARCH_PAPER.tex)

**Supplementary Materials**: See [papers/SUPPLEMENTARY_MATERIALS.md](papers/SUPPLEMENTARY_MATERIALS.md)

### Key Contributions

1. **Novel 14-feature complexity analyzer** (no training required)
2. **Task-specific threshold calibration** for optimal routing
3. **LangGraph-based architecture** for stateful workflow management
4. **Comprehensive evaluation** on 127 tasks with rigorous statistical testing

---

## Project Structure

```
adaptive-llm-routing/
├── README.md                        # This file
├── LICENSE                          # MIT License
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
│
├── papers/                          # Research papers
│   ├── RESEARCH_PAPER.md           # Main paper (Markdown)
│   ├── RESEARCH_PAPER.tex          # Main paper (LaTeX)
│   └── SUPPLEMENTARY_MATERIALS.md  # Supplementary materials
│
├── adaptive-llm-routing/            # Main codebase
│   ├── run.py                      # Main entry point
│   ├── monitor_progress.py         # Progress monitoring tool
│   ├── START_EXPERIMENTS.sh        # Quick start script (Unix)
│   ├── START_EXPERIMENTS.bat       # Quick start script (Windows)
│   │
│   ├── src/                        # Source code
│   │   ├── config.py               # Configuration
│   │   ├── llm_provider.py         # LLM provider abstraction
│   │   │
│   │   ├── agents/                 # Execution strategies
│   │   │   ├── single_llm.py      # Single-LLM executor
│   │   │   └── multi_agent.py     # Multi-agent pipeline
│   │   │
│   │   ├── graph/                  # LangGraph workflow
│   │   │   ├── builder.py         # Workflow builder
│   │   │   ├── nodes.py           # Graph nodes
│   │   │   └── state.py           # State definitions
│   │   │
│   │   ├── utils/                  # Utilities
│   │   │   └── complexity.py      # Complexity analyzer
│   │   │
│   │   ├── evaluation/             # Evaluation framework
│   │   │   ├── metrics.py         # Metrics computation
│   │   │   ├── feedback.py        # Feedback logging
│   │   │   └── statistics.py      # Statistical tests
│   │   │
│   │   └── experiments/            # Experiment runners
│   │       ├── run_full.py        # Full experiment
│   │       ├── run_full_resilient.py  # Resilient mode
│   │       ├── run_quick.py       # Quick test
│   │       ├── checkpoint_manager.py  # Checkpointing
│   │       └── generate_visuals.py    # Visualization
│   │
│   ├── data/                       # Data and results
│   │   ├── tasks/
│   │   │   └── benchmark_tasks.json   # 127-task benchmark
│   │   └── results/
│   │       ├── exp1_single_llm.json   # Baseline results
│   │       ├── exp2_multi_agent.json  # Upper bound results
│   │       ├── exp3_adaptive.json     # Adaptive results
│   │       └── figures/               # Visualizations (10 charts)
│   │
│   ├── tests/                      # Unit tests
│   │   ├── test_graph.py
│   │   └── test_providers.py
│   │
│   ├── examples/                   # Usage examples
│   │   └── analyze_results.py     # Result analysis script
│   │
│   └── dashboard/                  # Interactive dashboard (optional)
│       └── app.py
│
└── docs/                           # Additional documentation
    ├── RESILIENT_MODE.md          # Fault tolerance documentation
    └── archive/                    # Archived planning docs
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run tests: `pytest tests/`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/adaptive-llm-routing.git
cd adaptive-llm-routing

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
cd adaptive-llm-routing
pytest tests/

# Format code
black src/ tests/
```

---

## Citation

If you use this work in your research, please cite:

```bibtex
@article{epics2026adaptive,
  title={Cost-Efficient LLM Routing with Adaptive Complexity Analysis: A Graph-Based Approach to Dynamic Model Selection},
  author={EPICS Research Team},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **LangGraph** for stateful workflow orchestration
- **Groq**, **Mistral**, **Google**, and **HuggingFace** for API access
- Open-source LLM community for models and tools

---

## Contact

For questions, suggestions, or collaboration:

- **Email**: research@epics.edu
- **GitHub Issues**: [Submit an issue](https://github.com/yourusername/adaptive-llm-routing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/adaptive-llm-routing/discussions)

---

## Roadmap

### Current (v1.0)
- [x] Heuristic-based complexity analysis
- [x] Single-LLM and multi-agent execution
- [x] Fault-tolerant experiment runner
- [x] Comprehensive evaluation on 127 tasks
- [x] Research paper and supplementary materials

### Planned (v2.0)
- [ ] Learned routing (neural classifier)
- [ ] Cross-model evaluation (GPT-4, Claude, PaLM)
- [ ] Multi-objective optimization (quality/cost/latency tradeoffs)
- [ ] Hierarchical routing (single → two-agent → three-agent)
- [ ] Real-time dashboard with WebSocket updates
- [ ] Docker containerization
- [ ] REST API for production deployment

### Future
- [ ] Domain-specific fine-tuning
- [ ] User preference learning
- [ ] Automated threshold adaptation
- [ ] Integration with LangSmith/LangChain Hub
- [ ] Multilingual support

---

**Last Updated**: March 25, 2026
**Version**: 1.0.0
**Status**: Production-Ready

---

**Made with care by the EPICS Research Team**
