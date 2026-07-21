import pandas as pd
import streamlit as st

COLORS = {
    "bg": "#0B0B10",
    "surface": "#15151E",
    "border": "#2A2A38",
    "text": "#F2F2F5",
    "text_muted": "#9494A0",
    "red": "#E10600",
    "teal": "#00D2BE",
    "amber": "#FF8700",
    "purple": "#9B59B6",
}

# Plotly's default touch handling treats a scroll/drag over the chart as a
# zoom gesture, which hijacks page scrolling on mobile mid-swipe.
PLOTLY_CONFIG = {"scrollZoom": False}

COMPOUND_COLORS = {
    "SOFT": "#DA291C",
    "MEDIUM": "#FFD100",
    "HARD": "#E8E8E8",
    "INTERMEDIATE": "#43B02A",
    "WET": "#0067AD",
}

_CSS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] { font-family: 'Titillium Web', 'Segoe UI', sans-serif; font-size: 17px; }
* { border-radius: 0 !important; }

h1 {
  position: relative; font-family: 'Titillium Web', sans-serif; font-weight: 900;
  letter-spacing: -0.01em; font-size: 2.6rem !important; text-transform: uppercase;
  padding-bottom: 0.5rem; margin-bottom: 1.3rem !important; border-bottom: 3px solid #2A2A38;
}
h1::after {
  content: ""; position: absolute; left: 0; bottom: -3px; height: 3px; width: 100%;
  background: #E10600; transform-origin: left; animation: sweep-in 0.6s cubic-bezier(.16,1,.3,1) both;
}
@keyframes sweep-in { from { transform: scaleX(0); } to { transform: scaleX(1); } }
h2, h3 { font-family: 'Titillium Web', sans-serif; font-weight: 700; }

.live-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; letter-spacing: 0.04em;
  color: #9494A0; margin-bottom: 1rem;
}
.live-dot {
  width: 8px; height: 8px; background: #43B02A; box-shadow: 0 0 6px #43B02A;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }

.eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: #9494A0;
  border-top: 1px solid #2A2A38; padding-top: 0.6rem; margin: 1.8rem 0 0.6rem 0;
}

.kpi-row { display: flex; gap: 0.9rem; margin-bottom: 1.6rem; flex-wrap: wrap; }
.kpi-card {
  flex: 1 1 200px; background: #15151E; border: 1px solid #2A2A38;
  border-left: 4px solid var(--accent, #E10600); border-radius: 6px;
  padding: 1.1rem 1.3rem; opacity: 0;
  animation: kpi-in 0.4s cubic-bezier(.16,1,.3,1) both;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px -12px var(--accent, #E10600);
  border-color: var(--accent, #E10600);
}
.kpi-row .kpi-card:nth-child(1) { animation-delay: 0.00s; }
.kpi-row .kpi-card:nth-child(2) { animation-delay: 0.05s; }
.kpi-row .kpi-card:nth-child(3) { animation-delay: 0.10s; }
.kpi-row .kpi-card:nth-child(4) { animation-delay: 0.15s; }
.kpi-row .kpi-card:nth-child(5) { animation-delay: 0.20s; }
.kpi-row .kpi-card:nth-child(6) { animation-delay: 0.25s; }
.kpi-row .kpi-card:nth-child(n+7) { animation-delay: 0.30s; }
@keyframes kpi-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.kpi-label {
  font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: #9494A0; margin-bottom: 0.35rem;
}
.kpi-value {
  font-family: 'JetBrains Mono', monospace; font-size: 2.6rem; font-weight: 700;
  color: #F2F2F5; line-height: 1.1; font-variant-numeric: tabular-nums;
}
.kpi-sub { font-size: 0.95rem; color: #9494A0; margin-top: 0.25rem; }

[data-testid="stDataFrame"] *, [data-testid="stTable"] * {
  font-family: 'JetBrains Mono', monospace; font-size: 1rem !important;
}
[data-testid="stTable"] th, [data-testid="stTable"] td { padding: 0.5rem 0.8rem !important; }
[data-testid="stTable"] tbody tr { transition: background 0.15s ease; }
[data-testid="stTable"] tbody tr:hover { background: #1B1B26 !important; }

[data-testid="stSidebarNav"] a {
  transition: transform 0.15s ease, color 0.15s ease; display: block;
}
[data-testid="stSidebarNav"] a:hover { transform: translateX(4px); color: #E10600; }

:focus-visible { outline: 2px solid #E10600 !important; outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  .kpi-card, h1::after, .live-dot { animation: none !important; opacity: 1 !important; transform: none !important; }
  .kpi-card:hover, [data-testid="stSidebarNav"] a:hover { transform: none !important; }
}
</style>"""


def inject():
    st.html(_CSS)


def eyebrow(text: str):
    st.html(f'<div class="eyebrow">{text}</div>')


def live_badge(text: str):
    st.html(f'<div class="live-badge"><span class="live-dot"></span>{text}</div>')


def kpi_row(cards: list[dict]):
    """cards: [{label, value, sub="", accent="red"}]"""
    html = '<div class="kpi-row">'
    for c in cards:
        accent = COLORS.get(c.get("accent", "red"), COLORS["red"])
        html += (
            f'<div class="kpi-card" style="--accent:{accent}">'
            f'<div class="kpi-label">{c["label"]}</div>'
            f'<div class="kpi-value">{c["value"]}</div>'
        )
        if c.get("sub"):
            html += f'<div class="kpi-sub">{c["sub"]}</div>'
        html += "</div>"
    html += "</div>"
    st.html(html)


def format_millis(ms) -> str:
    if ms is None or (isinstance(ms, float) and pd.isna(ms)):
        return "—"
    ms = int(ms)
    minutes, rem = divmod(ms, 60000)
    seconds, millis = divmod(rem, 1000)
    if minutes:
        return f"{minutes}:{seconds:02d}.{millis:03d}"
    return f"{seconds}.{millis:03d}"


def themed(fig, height: int = 560):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family="JetBrains Mono, monospace", color=COLORS["text"], size=13),
        colorway=[COLORS["red"], COLORS["teal"], COLORS["amber"], COLORS["purple"], "#0090FF", "#B6BABD"],
        height=height,
        margin=dict(t=40, l=10, r=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"]),
    )
    return fig
