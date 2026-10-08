# 🖥️ Streamlit Dashboard

Interactive web dashboard for visualizing Adaptive LLM Routing experiment results.

---

## 🚀 Quick Start

### From `adaptive-llm-routing/` directory:

```bash
# Make sure you're in the adaptive-llm-routing directory
cd adaptive-llm-routing

# Run the dashboard
streamlit run dashboard/app.py
```

### From project root (`EPICS-Project/`):

```bash
cd adaptive-llm-routing
streamlit run dashboard/app.py
```

---

## 📋 Prerequisites

### 1. Run Experiments First

The dashboard needs experiment results to display. Run at least one experiment:

```bash
# Quick validation (15 tasks, ~5 minutes)
python run.py quick

# Or full benchmark (150 tasks, ~2 hours)
python run.py full
```

This will generate result files in `data/results/`:
- `exp1_single_llm.json`
- `exp2_multi_agent.json`
- `exp3_adaptive.json`
- `experiment_comparison.json`

### 2. Install Dependencies

```bash
pip install streamlit pandas
```

(Should already be in `requirements.txt`)

---

## 📊 Dashboard Features

### Tab 1: 📊 Comparison
- Side-by-side metrics for all 3 systems
- Cost, latency, and token savings
- Key insights and improvements

### Tab 2: 🔍 Per-Task Analysis
- Routing distribution pie chart
- Complexity vs quality scatter plot
- Filterable task results table

### Tab 3: 🔄 Feedback Loop
- Threshold adaptation over rounds
- Per-round statistics
- Routing accuracy tracking

### Tab 4: 📈 Charts
- All generated matplotlib figures
- Accuracy comparisons
- Cost analysis
- Efficiency visualizations

### Tab 5: 📋 Raw Data
- JSON result explorer
- All experiment data
- Export capabilities

---

## 🔧 Troubleshooting

### Error: "No module named 'src'"

**Solution:** Make sure you're running from the correct directory:

```bash
# Check your current directory
pwd  # Should show: .../adaptive-llm-routing

# If not, navigate to it
cd adaptive-llm-routing

# Then run dashboard
streamlit run dashboard/app.py
```

### Error: "No experiment results found"

**Solution:** Run experiments first:

```bash
python run.py quick
```

### Warning: "Running in fallback mode"

This is okay! The dashboard will still work, it just couldn't import `src.config` but uses fallback paths.

**To fix (optional):**
1. Make sure `.env` file exists in project root
2. Run from `adaptive-llm-routing/` directory

---

## 📁 Expected Directory Structure

```
adaptive-llm-routing/
├── dashboard/
│   ├── app.py              ← Main Streamlit app
│   └── README.md           ← This file
├── data/
│   └── results/
│       ├── exp1_single_llm.json
│       ├── exp2_multi_agent.json
│       ├── exp3_adaptive.json
│       ├── experiment_comparison.json
│       └── figures/        ← Generated charts
└── src/
    └── config.py
```

---

## 🌐 Accessing the Dashboard

After running `streamlit run dashboard/app.py`, you'll see:

```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

- **Local URL:** Open in browser on same machine
- **Network URL:** Share with others on same network

---

## ⌨️ Keyboard Shortcuts

- **R** - Rerun the app
- **C** - Clear cache
- **Ctrl+C** (in terminal) - Stop the server

---

## 🎨 Customization

### Change Port

```bash
streamlit run dashboard/app.py --server.port 8502
```

### Disable Auto-reload

```bash
streamlit run dashboard/app.py --server.fileWatcherType none
```

### Run in Headless Mode

```bash
streamlit run dashboard/app.py --server.headless true
```

---

## 📝 Development

### Live Reload

Streamlit automatically reloads when you save `app.py`. Great for development!

### Debug Mode

Add this to see more details:

```python
st.write("Debug:", st.session_state)
```

---

## ✅ Success Checklist

Before running the dashboard:

- [ ] In `adaptive-llm-routing/` directory
- [ ] Experiments completed (at least `quick`)
- [ ] Results exist in `data/results/`
- [ ] Streamlit installed (`pip install streamlit`)
- [ ] Port 8501 not in use

---

## 🚀 Quick Commands Reference

```bash
# Navigate to project
cd adaptive-llm-routing

# Run quick experiment (if needed)
python run.py quick

# Launch dashboard
streamlit run dashboard/app.py

# Open in browser (if doesn't open automatically)
# Visit: http://localhost:8501
```

---

**Enjoy exploring your results! 📊✨**
