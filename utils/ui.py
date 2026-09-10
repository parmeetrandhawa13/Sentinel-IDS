"""Shared visual theme and small rendering helpers for Sentinel IDS.

Streamlit does not give first-class theming hooks, so this module centralises
every bit of custom CSS/HTML in one place. Keeping it out of app.py keeps the
page logic readable and makes the visual language easy to adjust in one spot.
"""

from __future__ import annotations

import streamlit as st

SHIELD_LOGO = """
<svg width="34" height="34" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 2 L36 8 V19 C36 29 29 35.5 20 38 C11 35.5 4 29 4 19 V8 Z"
        fill="url(#sentinelGrad)" stroke="#5eead4" stroke-width="1.1"/>
  <path d="M14 19.5 L18 23.5 L26.5 14.5" stroke="#04121a" stroke-width="2.4"
        stroke-linecap="round" stroke-linejoin="round"/>
  <defs>
    <linearGradient id="sentinelGrad" x1="4" y1="2" x2="36" y2="38" gradientUnits="userSpaceOnUse">
      <stop stop-color="#22d3ee"/>
      <stop offset="1" stop-color="#0891b2"/>
    </linearGradient>
  </defs>
</svg>
"""


def inject_base_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
        .stApp {
            background:
                radial-gradient(1100px 480px at 12% -8%, rgba(34,211,238,0.10), transparent 60%),
                radial-gradient(900px 500px at 100% 0%, rgba(56,189,248,0.06), transparent 55%),
                linear-gradient(180deg, #05070c 0%, #070b13 45%, #05070c 100%);
            color: #dbe4ee;
        }
        .block-container { max-width: 1280px; padding-top: 1.6rem; padding-bottom: 3rem; }
        #MainMenu, footer { visibility: hidden; }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060a11 0%, #050810 100%);
            border-right: 1px solid rgba(94,234,212,0.12);
        }
        section[data-testid="stSidebar"] .stRadio label {
            padding: 6px 4px; border-radius: 8px; font-size: 14.5px;
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(148,163,184,0.15); }

        .brand-row { display:flex; align-items:center; gap:10px; margin-bottom:2px; }
        .brand-title { font-size:19px; font-weight:800; letter-spacing:1.5px; color:#e6fbff; margin:0; }
        .brand-sub { font-size:11px; color:#64748b; letter-spacing:1px; margin:0 0 14px 34px; text-transform:uppercase; }

        .status-line { display:flex; align-items:center; gap:8px; font-size:13px; color:#94a3b8; margin:5px 0; }
        .dot { width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; }
        .dot-green { background:#34d399; box-shadow:0 0 8px 2px rgba(52,211,153,0.65); animation: pulse 2s infinite; }
        .dot-cyan { background:#22d3ee; box-shadow:0 0 8px 2px rgba(34,211,238,0.55); }
        .dot-amber { background:#f59e0b; box-shadow:0 0 8px 2px rgba(245,158,11,0.55); }
        @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.45;} }

        .meta-chip {
            display:inline-block; font-size:11px; font-family:'JetBrains Mono',monospace;
            color:#7dd3fc; background:rgba(34,211,238,0.08); border:1px solid rgba(34,211,238,0.25);
            border-radius:6px; padding:2px 8px; margin:2px 4px 2px 0;
        }

        /* ---------- Hero header ---------- */
        .hero {
            padding: 26px 30px; border-radius: 18px; margin-bottom: 22px;
            background: linear-gradient(135deg, rgba(15,23,36,0.9), rgba(9,14,24,0.9));
            border: 1px solid rgba(94,234,212,0.18);
            box-shadow: 0 0 0 1px rgba(34,211,238,0.03), 0 18px 40px -20px rgba(0,0,0,0.7);
            position: relative; overflow:hidden;
        }
        .hero::before {
            content:""; position:absolute; inset:0;
            background: radial-gradient(420px 160px at 90% -20%, rgba(34,211,238,0.14), transparent 70%);
            pointer-events:none;
        }
        .hero-top { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; }
        .hero h1 { margin:0; font-size:26px; font-weight:800; letter-spacing:0.5px; color:#f1f5f9; }
        .hero .eyebrow { font-size:11.5px; font-weight:700; letter-spacing:2px; color:#22d3ee; text-transform:uppercase; margin-bottom:4px; }
        .hero p.desc { color:#8896a8; font-size:14.5px; margin:10px 0 0 0; max-width:640px; }
        .hero-badges { display:flex; gap:8px; flex-wrap:wrap; }
        .pill {
            font-size:11.5px; font-weight:600; padding:5px 12px; border-radius:999px;
            background:rgba(148,163,184,0.08); border:1px solid rgba(148,163,184,0.22); color:#cbd5e1;
        }
        .pill.online { color:#6ee7b7; border-color:rgba(52,211,153,0.35); background:rgba(52,211,153,0.08); }
        .pill.demo { color:#fbbf24; border-color:rgba(251,191,36,0.35); background:rgba(251,191,36,0.08); }

        /* ---------- KPI cards ---------- */
        .kpi {
            padding:20px 20px 18px; border-radius:16px; height:100%;
            background: linear-gradient(160deg, rgba(17,25,38,0.85), rgba(10,15,24,0.85));
            border:1px solid rgba(148,163,184,0.14);
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }
        .kpi:hover { transform: translateY(-3px); border-color: rgba(34,211,238,0.4); box-shadow: 0 12px 28px -14px rgba(34,211,238,0.35); }
        .kpi .kpi-icon { font-size:20px; opacity:.9; margin-bottom:10px; }
        .kpi .kpi-label { font-size:12.5px; color:#8896a8; letter-spacing:.4px; text-transform:uppercase; }
        .kpi .kpi-value { font-size:30px; font-weight:800; color:#f1f5f9; margin-top:6px; font-family:'JetBrains Mono',monospace; }
        .kpi .kpi-sub { font-size:12px; color:#5f6b7d; margin-top:4px; }

        /* ---------- Section titles ---------- */
        .section-title { font-size:15.5px; font-weight:700; color:#e2e8f0; letter-spacing:.3px; margin:2px 0 12px 0; display:flex; align-items:center; gap:8px;}
        .section-title .tag { font-size:10.5px; font-weight:700; color:#64748b; border:1px solid rgba(148,163,184,0.25); border-radius:5px; padding:1px 6px; letter-spacing:1px;}

        /* Style Streamlit's native bordered container like a glass panel */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border-radius:16px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(148,163,184,0.14) !important;
            background: linear-gradient(160deg, rgba(15,21,32,0.65), rgba(8,12,20,0.65));
            border-radius:16px !important;
        }

        /* ---------- Pipeline flow ---------- */
        .pipeline { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px; padding:6px 0; }
        .pipe-step {
            flex:1; min-width:120px; text-align:center; padding:14px 8px; border-radius:12px;
            background:rgba(255,255,255,0.02); border:1px solid rgba(148,163,184,0.16); font-size:12.5px; font-weight:600; color:#cbd5e1;
        }
        .pipe-step .n { display:block; font-size:10.5px; color:#22d3ee; font-family:'JetBrains Mono',monospace; margin-bottom:4px; }
        .pipe-arrow { color:#334155; font-size:18px; padding:0 2px; }

        /* ---------- Threat result panel ---------- */
        .result-panel { padding:30px; border-radius:18px; text-align:center; position:relative; overflow:hidden; }
        .result-normal { background:linear-gradient(160deg, rgba(6,40,28,0.85), rgba(6,20,16,0.9)); border:1px solid rgba(52,211,153,0.4); box-shadow:0 0 40px -18px rgba(52,211,153,0.5);}
        .result-attack { background:linear-gradient(160deg, rgba(45,10,15,0.9), rgba(20,6,9,0.92)); border:1px solid rgba(248,113,113,0.45); box-shadow:0 0 40px -16px rgba(248,113,113,0.55); animation: glow-red 2.2s ease-in-out infinite; }
        @keyframes glow-red { 0%,100%{box-shadow:0 0 40px -16px rgba(248,113,113,0.55);} 50%{box-shadow:0 0 55px -12px rgba(248,113,113,0.8);} }
        .result-eyebrow { font-size:12px; letter-spacing:2px; color:#94a3b8; text-transform:uppercase; margin-bottom:8px;}
        .result-title { font-size:28px; font-weight:800; letter-spacing:.5px; }
        .result-normal .result-title { color:#6ee7b7; }
        .result-attack .result-title { color:#fca5a5; }
        .result-meta { display:flex; justify-content:center; gap:34px; margin-top:20px; flex-wrap:wrap; }
        .result-meta .m-label { font-size:11px; color:#8896a8; text-transform:uppercase; letter-spacing:1px; }
        .result-meta .m-value { font-size:19px; font-weight:700; color:#f1f5f9; font-family:'JetBrains Mono',monospace; margin-top:2px;}

        .risk-badge { display:inline-block; padding:3px 12px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.5px; }
        .risk-HIGH { background:rgba(248,113,113,0.15); color:#fca5a5; border:1px solid rgba(248,113,113,0.4); }
        .risk-MEDIUM { background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid rgba(251,191,36,0.4); }
        .risk-LOW { background:rgba(148,163,184,0.15); color:#cbd5e1; border:1px solid rgba(148,163,184,0.4); }
        .risk-NONE { background:rgba(52,211,153,0.15); color:#6ee7b7; border:1px solid rgba(52,211,153,0.4); }

        /* ---------- Confidence bars ---------- */
        .conf-row { display:flex; align-items:center; gap:12px; margin:8px 0; }
        .conf-label { width:74px; font-size:12.5px; font-weight:700; color:#94a3b8; font-family:'JetBrains Mono',monospace; }
        .conf-track { flex:1; height:11px; border-radius:6px; background:rgba(148,163,184,0.12); overflow:hidden; }
        .conf-fill-normal { height:100%; border-radius:6px; background:linear-gradient(90deg,#059669,#34d399); }
        .conf-fill-attack { height:100%; border-radius:6px; background:linear-gradient(90deg,#b91c1c,#f87171); }
        .conf-pct { width:52px; text-align:right; font-size:12.5px; font-family:'JetBrains Mono',monospace; color:#cbd5e1; }

        /* ---------- Indicator list ---------- */
        .indicator-item { display:flex; gap:10px; align-items:flex-start; padding:9px 0; border-bottom:1px dashed rgba(148,163,184,0.12); font-size:13.5px; color:#cbd5e1; }
        .indicator-item:last-child { border-bottom:none; }
        .indicator-dot { color:#f87171; margin-top:1px; }

        /* ---------- Tree votes ---------- */
        .tree-grid { display:flex; gap:8px; flex-wrap:wrap; margin:10px 0; }
        .tree-box { width:64px; padding:10px 4px; text-align:center; border-radius:10px; font-size:11px; font-weight:700; }
        .tree-box .t-n { display:block; font-size:9.5px; color:#94a3b8; margin-bottom:5px; font-family:'JetBrains Mono',monospace;}
        .tree-normal { background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.35); color:#6ee7b7; }
        .tree-attack { background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.35); color:#fca5a5; }

        /* ---------- Misc ---------- */
        .muted { color:#64748b; font-size:13px; }
        .demo-banner {
            padding:10px 16px; border-radius:10px; font-size:12.5px; font-weight:600;
            background:rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.3); color:#fbbf24; margin-bottom:16px;
        }
        div[data-baseweb="tab-list"] { gap: 4px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(eyebrow: str, title: str, description: str, system_online: bool = True) -> None:
    status_pill = (
        '<span class="pill online">● SYSTEM ONLINE</span>' if system_online
        else '<span class="pill">● SYSTEM OFFLINE</span>'
    )
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-top">
                <div class="brand-row">
                    {SHIELD_LOGO}
                    <div>
                        <p class="brand-title" style="margin-bottom:0;">SENTINEL IDS</p>
                    </div>
                </div>
                <div class="hero-badges">
                    {status_pill}
                    <span class="pill">MODEL: RANDOM FOREST</span>
                    <span class="pill demo">MODE: DEMONSTRATION</span>
                </div>
            </div>
            <div class="eyebrow" style="margin-top:16px;">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="desc">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    st.markdown(
        f"""
        <div class="brand-row">{SHIELD_LOGO}<p class="brand-title">SENTINEL IDS</p></div>
        <p class="brand-sub">AI-Powered Network Security</p>
        """,
        unsafe_allow_html=True,
    )


def sidebar_status(model_ok: bool, data_ok: bool) -> None:
    m_dot = "dot-green" if model_ok else "dot-amber"
    d_dot = "dot-green" if data_ok else "dot-amber"
    e_dot = "dot-green" if (model_ok and data_ok) else "dot-amber"
    st.markdown(
        f"""
        <div class="status-line"><span class="dot {m_dot}"></span> Model {'Loaded' if model_ok else 'Unavailable'}</div>
        <div class="status-line"><span class="dot {d_dot}"></span> Dataset {'Loaded' if data_ok else 'Unavailable'}</div>
        <div class="status-line"><span class="dot {e_dot}"></span> Prediction Engine {'Ready' if (model_ok and data_ok) else 'Not Ready'}</div>
        """,
        unsafe_allow_html=True,
    )


def stack_chip(*labels: str) -> None:
    chips = "".join(f'<span class="meta-chip">{l}</span>' for l in labels)
    st.markdown(chips, unsafe_allow_html=True)


def section_title(icon: str, text: str, tag: str | None = None) -> None:
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    st.markdown(f'<div class="section-title">{icon} {text} {tag_html}</div>', unsafe_allow_html=True)


def kpi_card(icon: str, label: str, value: str, sub: str = "") -> str:
    return (
        f'<div class="kpi"><div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div></div>'
    )


def pipeline_flow(steps: list[str]) -> None:
    parts = []
    for i, step in enumerate(steps, start=1):
        parts.append(f'<div class="pipe-step"><span class="n">STEP {i:02d}</span>{step}</div>')
        if i != len(steps):
            parts.append('<div class="pipe-arrow">›</div>')
    st.markdown(f'<div class="pipeline">{"".join(parts)}</div>', unsafe_allow_html=True)


def result_panel(is_attack: bool, confidence: float, risk: str, model_name: str = "Random Forest") -> None:
    cls = "result-attack" if is_attack else "result-normal"
    title = "🔴 INTRUSION DETECTED" if is_attack else "🟢 NORMAL TRAFFIC"
    eyebrow = "THREAT STATUS" if is_attack else "TRAFFIC STATUS"
    st.markdown(
        f"""
        <div class="result-panel {cls}">
            <div class="result-eyebrow">{eyebrow}</div>
            <div class="result-title">{title}</div>
            <div class="result-meta">
                <div><div class="m-label">Confidence</div><div class="m-value">{confidence*100:.1f}%</div></div>
                <div><div class="m-label">Risk Level</div><div class="m-value"><span class="risk-badge risk-{risk}">{risk}</span></div></div>
                <div><div class="m-label">Model</div><div class="m-value" style="font-size:15px;">{model_name}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confidence_bars(prob_normal: float, prob_attack: float) -> None:
    def bar(label, pct, fill_class):
        blocks_filled = round(pct * 10)
        return (
            f'<div class="conf-row"><div class="conf-label">{label}</div>'
            f'<div class="conf-track"><div class="{fill_class}" style="width:{pct*100:.1f}%"></div></div>'
            f'<div class="conf-pct">{pct*100:.1f}%</div></div>'
        )

    st.markdown(
        bar("NORMAL", prob_normal, "conf-fill-normal") + bar("ATTACK", prob_attack, "conf-fill-attack"),
        unsafe_allow_html=True,
    )


def indicator_list(indicators: list[str]) -> None:
    if not indicators:
        st.markdown('<p class="muted">No specific feature-level indicators were flagged for this record.</p>', unsafe_allow_html=True)
        return
    items = "".join(f'<div class="indicator-item"><span class="indicator-dot">●</span>{i}</div>' for i in indicators)
    st.markdown(items, unsafe_allow_html=True)


def tree_vote_grid(votes: list[int]) -> None:
    boxes = "".join(
        f'<div class="tree-box {"tree-attack" if v == 1 else "tree-normal"}">'
        f'<span class="t-n">TREE {i+1}</span>{"ATTACK" if v == 1 else "NORMAL"}</div>'
        for i, v in enumerate(votes)
    )
    st.markdown(f'<div class="tree-grid">{boxes}</div>', unsafe_allow_html=True)


def demo_banner(text: str) -> None:
    st.markdown(f'<div class="demo-banner">⚠ {text}</div>', unsafe_allow_html=True)
