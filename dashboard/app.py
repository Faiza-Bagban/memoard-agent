import sys
import os
import csv
import html as html_lib
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore

st.set_page_config(page_title="MemoardAgent — Memory Inspector", layout="wide", page_icon="🧠")

# ---------- Fonts + theme ----------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
    --bg-deep: #0A0C14;
    --bg-panel: #12151F;
    --bg-panel-2: #171B29;
    --ink: #E4E7F1;
    --ink-dim: #8A90A6;
    --episodic: #7DA6FF;
    --semantic: #52E3C2;
    --procedural: #C9A6FF;
    --amber: #FFB454;
}
.stApp { background: var(--bg-deep); color: var(--ink); font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }
[data-testid="stSidebar"] { background: var(--bg-panel); border-right: 1px solid #1F2333; }
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; }
.stTextInput input {
    background: var(--bg-panel-2) !important;
    color: var(--ink) !important;
    border: 1px solid #262B3D !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stButton button {
    background: var(--amber) !important;
    color: #1A1200 !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
}
.stButton button:hover { filter: brightness(1.08); }
button[role="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--ink-dim) !important;
    background: transparent !important;
}
button[role="tab"][aria-selected="true"] {
    color: var(--ink) !important;
    border-bottom-color: var(--amber) !important;
}
.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-dim);
    margin-bottom: 0.2rem;
}
.stat-block { padding: 0.4rem 0; }
.stat-num { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; line-height: 1; }
.stat-label { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--ink-dim); margin-top: 0.3rem; }
.mem-card {
    background: var(--bg-panel);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 3px solid var(--card-color, var(--episodic));
}
.mem-content { font-size: 0.92rem; line-height: 1.5; color: var(--ink); margin-bottom: 8px; }
.mem-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.mem-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    color: var(--ink-dim);
}
.mem-chip.consolidated { color: var(--amber); }
.wave-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--ink-dim);
    margin-top: -6px;
}
@media (prefers-reduced-motion: reduce) { .pulse-line { animation: none !important; } }
</style>
""", unsafe_allow_html=True)


def _load_session_rates(csv_path: str):
    """Compute pass rate per session from a benchmark results CSV.

    Args:
        csv_path: Path to the results CSV file.

    Returns:
        A list of (session_number, pass_rate_percent) tuples sorted by session.
    """
    if not os.path.exists(csv_path):
        return []
    by_session = defaultdict(list)
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            by_session[int(row["session"])].append(row["passed"] == "True")
    sessions = sorted(by_session.keys())
    return [(s, sum(by_session[s]) / len(by_session[s]) * 100) for s in sessions]


def render_sleep_wave(csv_path: str = "benchmark/results_sleep.csv") -> str:
    """Build an EEG-style SVG trace of convention recall across sessions.

    Args:
        csv_path: Path to the sleep-cycle benchmark results CSV.

    Returns:
        An HTML string containing the SVG wave, or a placeholder message.
    """
    data = _load_session_rates(csv_path)
    if not data:
        return '<p style="color:#8A90A6; font-family:JetBrains Mono, monospace; font-size:0.85rem;">No benchmark run found at this path yet — run the benchmark to see the recall wave.</p>'

    width, height = 900, 180
    pad_l, pad_r, pad_t, pad_b = 30, 30, 20, 30
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    n = len(data)
    step = plot_w / max(n - 1, 1)

    points = []
    for i, (session, rate) in enumerate(data):
        x = pad_l + i * step
        y = pad_t + (100 - rate) / 100 * plot_h
        points.append((x, y, session, rate))

    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in points)

    circles = ""
    labels = ""
    for x, y, session, rate in points:
        circles += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#FFB454" />'
        labels += (
            f'<text x="{x:.1f}" y="{y-12:.1f}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="11" fill="#FFB454" font-weight="600">{rate:.0f}%</text>'
        )
        labels += (
            f'<text x="{x:.1f}" y="{height-8}" text-anchor="middle" '
            f'font-family="JetBrains Mono, monospace" font-size="10" fill="#8A90A6">S{session}</text>'
        )

    svg = f'''
    <svg viewBox="0 0 {width} {height}" style="width:100%; height:auto;">
        <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                </feMerge>
            </filter>
        </defs>
        <line x1="{pad_l}" y1="{pad_t}" x2="{width-pad_r}" y2="{pad_t}" stroke="#1F2333" stroke-width="1" />
        <line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{width-pad_r}" y2="{pad_t + plot_h}" stroke="#1F2333" stroke-width="1" />
        <polyline points="{polyline}" fill="none" stroke="#FFB454" stroke-width="2.5" filter="url(#glow)" class="pulse-line" />
        {circles}
        {labels}
    </svg>
    '''
    return svg


CARD_META = {
    "episodic": {"color": "var(--episodic)", "icon": "📖"},
    "semantic": {"color": "var(--semantic)", "icon": "💡"},
    "procedural": {"color": "var(--procedural)", "icon": "🛠️"},
}


def render_card(content: str, metadata: dict, kind: str) -> str:
    """Render a single memory item as a styled HTML card.

    Args:
        content: The memory item's text content.
        metadata: The stored metadata dict for the item.
        kind: One of "episodic", "semantic", "procedural" - controls card color.

    Returns:
        An HTML string for the card.
    """
    color = CARD_META[kind]["color"]
    safe_content = html_lib.escape(content).replace("\n", "<br>")
    importance = metadata.get("importance", "-")
    tag = metadata.get("convention_tag", "") or "untagged"
    consolidated = metadata.get("consolidated", False)
    timestamp = str(metadata.get("timestamp", ""))[:19]

    chips = f'<span class="mem-chip">tag: {html_lib.escape(str(tag))}</span>'
    chips += f'<span class="mem-chip">importance: {importance}</span>'
    if timestamp:
        chips += f'<span class="mem-chip">{timestamp}</span>'
    if kind == "episodic":
        badge_class = "mem-chip consolidated" if consolidated else "mem-chip"
        badge_text = "consolidated" if consolidated else "raw"
        chips += f'<span class="{badge_class}">{badge_text}</span>'

    return f'''
    <div class="mem-card" style="--card-color:{color};">
        <div class="mem-content">{safe_content}</div>
        <div class="mem-meta">{chips}</div>
    </div>
    '''


# ---------- Header ----------
st.markdown('<div class="eyebrow">Memory Architecture Portfolio Project</div>', unsafe_allow_html=True)
st.markdown("# 🧠 MemoardAgent")
st.markdown(
    '<p style="color:#8A90A6; font-size:1rem; margin-top:-8px;">'
    'A long-horizon coding agent with typed memory, sleep-cycle consolidation, and forgetting.</p>',
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
st.sidebar.markdown('<div class="eyebrow">Session Control</div>', unsafe_allow_html=True)
persist_path = st.sidebar.text_input("ChromaDB path", value="./chroma_db_sleep", label_visibility="collapsed")
load_clicked = st.sidebar.button("Load memory")

if load_clicked:
    st.session_state["persist_path"] = persist_path

if "persist_path" in st.session_state:
    path = st.session_state["persist_path"]

    # ---------- Signature: sleep wave ----------
    st.markdown('<div class="eyebrow" style="margin-top: 1.5rem;">Convention Recall — Session by Session</div>', unsafe_allow_html=True)
    csv_candidate = "benchmark/results_sleep.csv" if os.path.exists("benchmark/results_sleep.csv") else "benchmark/results.csv"
    st.markdown(render_sleep_wave(csv_candidate), unsafe_allow_html=True)
    st.markdown('<p class="wave-caption">Teach once. Retained across every session after.</p>', unsafe_allow_html=True)

    st.markdown("---")

    episodic = EpisodicStore(path)
    semantic = SemanticStore(path)
    procedural = ProceduralStore(path)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-block"><div class="stat-num" style="color:var(--episodic)">{len(episodic.all())}</div><div class="stat-label">EPISODIC MEMORIES</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-block"><div class="stat-num" style="color:var(--semantic)">{len(semantic.all())}</div><div class="stat-label">SEMANTIC FACTS</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-block"><div class="stat-num" style="color:var(--procedural)">{len(procedural.all())}</div><div class="stat-label">PROCEDURAL SKILLS</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📖  Episodic", "💡  Semantic", "🛠️  Procedural"])

    with tab1:
        for item in episodic.all():
            st.markdown(render_card(item["content"], item["metadata"], "episodic"), unsafe_allow_html=True)

    with tab2:
        for item in semantic.all():
            st.markdown(render_card(item["content"], item["metadata"], "semantic"), unsafe_allow_html=True)

    with tab3:
        for item in procedural.all():
            st.markdown(render_card(item["content"], item["metadata"], "procedural"), unsafe_allow_html=True)
else:
    st.info("Enter a ChromaDB path in the sidebar and click **Load memory** to inspect a store.")