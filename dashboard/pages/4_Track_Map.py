import streamlit as st
import plotly.graph_objects as go
from db import run_query
from style import inject, eyebrow, kpi_row, format_millis, COLORS, live_badge, PLOTLY_CONFIG
from i18n import lang_selector, t
from lap_ranking import compute_ranking

SEASON = 2025

st.set_page_config(layout="wide")
inject()
lang_selector()
st.title(t("page_title_trackmap"))
live_badge(t("season_caption", season=SEASON))

rounds = run_query(
    "SELECT DISTINCT Round, RaceName FROM vw_TrackMapFastestSector "
    "WHERE Season = :season ORDER BY Round",
    {"season": SEASON},
)

if rounds.empty:
    st.info(t("info_no_trackmap_season"))
    st.stop()

round_choice = st.selectbox(
    t("label_race"), rounds["Round"],
    format_func=lambda r: rounds.set_index("Round").loc[r, "RaceName"],
)

geometry = run_query(
    "SELECT SectorNumber, Distance, X, Y, FastestDriverName, FastestSectorMillis "
    "FROM vw_TrackMapFastestSector WHERE Season = :season AND Round = :round "
    "ORDER BY SectorNumber, Distance",
    {"season": SEASON, "round": round_choice},
)

if geometry.empty:
    st.info(t("info_no_trackmap_race"))
else:
    sector_accents = ["red", "teal", "amber", "purple"]
    sector_colors = [COLORS["red"], COLORS["teal"], COLORS["amber"], COLORS["purple"]]
    cards = []
    fig = go.Figure()
    for sector in sorted(geometry["SectorNumber"].unique()):
        seg = geometry[geometry["SectorNumber"] == sector]
        driver = seg["FastestDriverName"].iloc[0]
        color = sector_colors[(sector - 1) % len(sector_colors)]
        accent = sector_accents[(sector - 1) % len(sector_accents)]
        cards.append(
            {
                "label": t("kpi_sector", n=sector),
                "value": format_millis(seg["FastestSectorMillis"].iloc[0]),
                "sub": driver,
                "accent": accent,
            }
        )
        fig.add_trace(
            go.Scatter(
                x=seg["X"], y=seg["Y"], mode="lines",
                name=f'{t("kpi_sector", n=sector)} — {driver}',
                line=dict(color=color, width=5),
            )
        )
    kpi_row(cards)
    eyebrow(t("eyebrow_track_geometry"))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family="JetBrains Mono, monospace", color=COLORS["text"], size=13),
        height=680,
        margin=dict(t=20, l=10, r=10, b=10),
        xaxis=dict(title="X", gridcolor=COLORS["border"], visible=False),
        yaxis=dict(title="Y", gridcolor=COLORS["border"], visible=False, scaleanchor="x", scaleratio=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

laps_ranking = run_query(
    "SELECT DriverName, MIN(LapTimeMillis) AS BestLapMillis FROM vw_LapTimesEnriched "
    "WHERE Season = :season AND Round = :round AND LapTimeMillis IS NOT NULL "
    "GROUP BY DriverName ORDER BY BestLapMillis ASC",
    {"season": SEASON, "round": round_choice},
)

eyebrow(t("eyebrow_lap_ranking"))
if laps_ranking.empty:
    st.info(t("info_no_lap_ranking"))
else:
    ranking = compute_ranking(laps_ranking)
    ranking_display = ranking.rename(columns={
        "Rank": t("col_rank"),
        "DriverName": t("col_driver"),
        "BestLap": t("col_best_lap"),
        "Gap": t("col_gap"),
    }).set_index(t("col_rank"))
    st.table(ranking_display)
