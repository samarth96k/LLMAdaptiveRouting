"""
Streamlit Dashboard — Adaptive LLM Routing Results Viewer.

Run: streamlit run dashboard/app.py
"""

import json
import sys
import warnings
from pathlib import Path
import streamlit as st
import pandas as pd

# Suppress Streamlit warnings about missing ScriptRunContext
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Fix path to make src/ importable
DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DASHBOARD_DIR.parent  # adaptive-llm-routing/
sys.path.insert(0, str(PROJECT_DIR))

try:
    from src.config import RESULTS_DIR
except ImportError:
    # Fallback: define RESULTS_DIR manually if import fails
    RESULTS_DIR = PROJECT_DIR / "data" / "results"
    st.sidebar.warning("⚠️ Running in fallback mode (couldn't import config)")


st.set_page_config(
    page_title="Adaptive LLM Routing Dashboard",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════

@st.cache_data
def load_results(run_dir: Path):
    """Load all experiment results from a run directory."""
    data = {}
    for f in run_dir.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data[f.stem] = json.load(fp)
    return data


def get_run_dirs():
    """Get all versioned run directories."""
    if not RESULTS_DIR.exists():
        return []
    dirs = sorted(
        [d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.endswith("_result")],
        key=lambda d: d.name, reverse=True
    )
    return dirs


def results_to_df(results_list: list) -> pd.DataFrame:
    """Convert a list of result dicts to a DataFrame."""
    rows = []
    for r in results_list:
        if "error" in r:
            continue
        rows.append({
            "task_id": r.get("task_id", ""),
            "route": r.get("route", ""),
            "model": r.get("model_used", ""),
            "accuracy": r.get("accuracy_score", 0),
            "quality": r.get("quality_score", 0),
            "latency": r.get("latency_seconds", 0),
            "tokens": r.get("token_usage", {}).get("total", 0) if isinstance(r.get("token_usage"), dict) else 0,
            "cost": r.get("estimated_cost", 0),
            "complexity": r.get("complexity_score", 0),
            "semantic_sim": r.get("semantic_similarity_score", 0),
            "response_preview": str(r.get("response", ""))[:200],
        })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

st.sidebar.markdown("# 🔀 Adaptive LLM Router")
st.sidebar.markdown("---")

run_dirs = get_run_dirs()

# Check if main results dir has JSON files too
has_main_results = RESULTS_DIR.exists() and any(RESULTS_DIR.glob("exp*.json"))

if not run_dirs and not has_main_results:
    st.error("❌ No experiment results found!")
    st.info("📝 Run experiments first:")
    st.code("cd adaptive-llm-routing\npython run.py quick", language="bash")
    st.markdown("---")
    st.markdown("**Expected results location:**")
    st.code(str(RESULTS_DIR), language="text")
    st.stop()

run_options = {}
if has_main_results:
    run_options["Latest (main)"] = RESULTS_DIR
for d in run_dirs:
    run_options[d.name] = d

selected_run = st.sidebar.selectbox("📁 Select Run", list(run_options.keys()))
run_path = run_options[selected_run]

data = load_results(run_path)
st.sidebar.markdown(f"**Files loaded:** {len(data)}")
st.sidebar.markdown(f"**Path:** `{run_path.name}`")


# ═══════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═══════════════════════════════════════════════════════════════════

st.title("🔀 Adaptive LLM Routing — Research Dashboard")
st.markdown("Comparing **Single LLM**, **Multi-Agent**, and **Adaptive Routing** systems.")
st.markdown("---")


# ── Tab Layout ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Comparison", "🔍 Per-Task Analysis", "🔄 Feedback Loop",
    "📈 Charts", "📋 Raw Data"
])


# ═══════════════════════════════════════════════════════════════════
# TAB 1: COMPARISON
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.header("📊 System Comparison")

    comparison = data.get("experiment_comparison", [])
    if comparison:
        comp = comparison[0] if isinstance(comparison, list) else comparison

        cols = st.columns(3)
        systems = [
            ("Single LLM", comp.get("single_llm", {}), "🟦"),
            ("Multi-Agent", comp.get("multi_agent", {}), "🟨"),
            ("Adaptive", comp.get("adaptive", {}), "🟩"),
        ]

        for col, (name, stats, emoji) in zip(cols, systems):
            with col:
                st.subheader(f"{emoji} {name}")
                if stats:
                    st.metric("Accuracy", f"{stats.get('avg_accuracy', 0):.3f}")
                    st.metric("Quality", f"{stats.get('avg_quality', 0):.3f}")
                    st.metric("Latency", f"{stats.get('avg_latency', 0):.2f}s")
                    st.metric("Total Tokens", f"{stats.get('total_tokens', 0):,}")
                    st.metric("Total Cost", f"${stats.get('total_cost', 0):.5f}")
                    st.metric("Efficiency", f"{stats.get('avg_efficiency', 0):,.0f}")
                else:
                    st.warning("No data")

        # Summary insights
        st.markdown("---")
        st.subheader("💡 Key Insights")

        s = comp.get("single_llm", {})
        m = comp.get("multi_agent", {})
        a = comp.get("adaptive", {})

        if s and m and a:
            token_savings = (1 - a.get("total_tokens", 0) / max(m.get("total_tokens", 1), 1)) * 100
            cost_savings = (1 - a.get("total_cost", 0) / max(m.get("total_cost", 0.0001), 0.0001)) * 100
            latency_speedup = m.get("avg_latency", 1) / max(a.get("avg_latency", 1), 0.001)

            col1, col2, col3 = st.columns(3)
            col1.metric("Token Savings vs Multi-Agent", f"{token_savings:.0f}%",
                        delta=f"{int(m.get('total_tokens', 0) - a.get('total_tokens', 0)):,} tokens saved")
            col2.metric("Cost Savings vs Multi-Agent", f"{cost_savings:.0f}%",
                        delta=f"${m.get('total_cost', 0) - a.get('total_cost', 0):.5f} saved")
            col3.metric("Speed vs Multi-Agent", f"{latency_speedup:.1f}x faster",
                        delta=f"{m.get('avg_latency', 0) - a.get('avg_latency', 0):.1f}s faster")
    else:
        st.info("No comparison data found. Run all experiments first.")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: PER-TASK ANALYSIS
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.header("🔍 Per-Task Analysis")

    # load adaptive results for detailed view
    adaptive_data = data.get("exp3_adaptive", [])
    if adaptive_data:
        df = results_to_df(adaptive_data)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Routing Distribution")
            route_counts = df["route"].value_counts()
            st.bar_chart(route_counts)

        with col2:
            st.subheader("Complexity vs Quality")
            chart_df = df[["complexity", "quality", "route"]].copy()
            st.scatter_chart(chart_df, x="complexity", y="quality", color="route")

        st.markdown("---")
        st.subheader("All Task Results")

        # Filter options
        route_filter = st.multiselect("Filter by Route", df["route"].unique(), default=df["route"].unique())
        filtered_df = df[df["route"].isin(route_filter)]

        st.dataframe(
            filtered_df[["task_id", "route", "accuracy", "quality", "semantic_sim", "latency", "tokens", "complexity"]],
            width='stretch', height=400,
        )
    else:
        st.info("No adaptive results. Run experiment 3 first.")


# ═══════════════════════════════════════════════════════════════════
# TAB 3: FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.header("🔄 Feedback Loop Analysis")

    fb_data = data.get("exp4_feedback_loop", [])
    if fb_data:
        fb = fb_data[0] if isinstance(fb_data, list) else fb_data

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Threshold History")
            thresholds = fb.get("threshold_history", [])
            if thresholds:
                th_df = pd.DataFrame({
                    "Round": list(range(len(thresholds))),
                    "Threshold": thresholds,
                })
                st.line_chart(th_df.set_index("Round"))

        with col2:
            st.subheader("Final Statistics")
            stats = fb.get("final_stats", {})
            if stats:
                st.metric("Total Runs", stats.get("total_runs", 0))
                st.metric("Routing Accuracy", f"{stats.get('routing_accuracy', 0):.1%}")
                st.metric("Avg Accuracy", f"{stats.get('avg_accuracy', 0):.3f}")
                st.metric("Total Cost", f"${stats.get('total_cost', 0):.5f}")

        # Per-round comparison
        st.markdown("---")
        st.subheader("Per-Round Results")
        for round_key in sorted([k for k in data if k.startswith("exp4_round_")]):
            round_num = round_key.replace("exp4_round_", "")
            round_data = data[round_key]
            rf = results_to_df(round_data)
            if not rf.empty:
                with st.expander(f"Round {round_num} — {len(rf)} tasks"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Avg Accuracy", f"{rf['accuracy'].mean():.3f}")
                    col2.metric("Avg Quality", f"{rf['quality'].mean():.3f}")
                    col3.metric("Avg Latency", f"{rf['latency'].mean():.2f}s")
                    st.dataframe(rf[["task_id", "route", "accuracy", "quality", "latency"]], height=200)
    else:
        st.info("No feedback loop data. Run experiment 4 first.")


# ═══════════════════════════════════════════════════════════════════
# TAB 4: CHARTS
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.header("📈 Generated Charts")

    figures_dir = run_path / "figures" if (run_path / "figures").exists() else RESULTS_DIR / "figures"

    if figures_dir.exists():
        png_files = sorted(figures_dir.glob("*.png"))
        if png_files:
            cols = st.columns(2)
            for i, fig_path in enumerate(png_files):
                with cols[i % 2]:
                    caption = fig_path.stem.replace("_", " ").title()
                    st.image(str(fig_path), caption=caption, width='stretch')
        else:
            st.info("No charts generated yet.")
    else:
        st.info("No figures directory found.")


# ═══════════════════════════════════════════════════════════════════
# TAB 5: RAW DATA
# ═══════════════════════════════════════════════════════════════════

with tab5:
    st.header("📋 Raw Data Explorer")

    file_list = [k for k in sorted(data.keys())]
    selected_file = st.selectbox("Select result file", file_list)

    if selected_file:
        st.json(data[selected_file])


# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Quick Actions")
st.sidebar.code("python run.py quick", language="bash")
st.sidebar.code("python run.py full", language="bash")
st.sidebar.code("streamlit run dashboard/app.py", language="bash")
