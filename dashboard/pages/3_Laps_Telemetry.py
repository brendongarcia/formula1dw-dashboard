import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from db import run_query
from style import inject, eyebrow, kpi_row, themed, format_millis, COMPOUND_COLORS, COLORS, live_badge
from i18n import lang_selector, t

SEASON = 2025

st.set_page_config(layout="wide")
inject()
lang_selector()
st.title(t("page_title_laps"))
live_badge(t("season_caption", season=SEASON))

rounds = run_query(
    "SELECT DISTINCT Round, RaceName FROM vw_LapTimesEnriched "
    "WHERE Season = :season ORDER BY Round",
    {"season": SEASON},
)
round_choice = st.selectbox(
    t("label_race"), rounds["Round"],
    format_func=lambda r: rounds.set_index("Round").loc[r, "RaceName"],
)

drivers = run_query(
    "SELECT DISTINCT DriverName FROM vw_LapTimesEnriched "
    "WHERE Season = :season AND Round = :round ORDER BY DriverName",
    {"season": SEASON, "round": round_choice},
)["DriverName"].tolist()
driver = st.selectbox(t("label_driver"), drivers)

laps = run_query(
    "SELECT LapNumber, LapTimeMillis, Compound, Stint FROM vw_LapTimesEnriched "
    "WHERE Season = :season AND Round = :round AND DriverName = :driver ORDER BY LapNumber",
    {"season": SEASON, "round": round_choice, "driver": driver},
)

eyebrow(t("eyebrow_lap_times"))
if laps.empty:
    st.info(t("info_no_laps"))
else:
    best_ms = laps["LapTimeMillis"].min()
    avg_ms = laps["LapTimeMillis"].mean()
    kpi_row(
        [
            {"label": t("kpi_best_lap"), "value": format_millis(best_ms), "accent": "red"},
            {"label": t("kpi_average_lap"), "value": format_millis(avg_ms), "accent": "teal"},
            {"label": t("kpi_laps_completed"), "value": len(laps), "accent": "amber"},
        ]
    )
    fig = px.line(
        laps, x="LapNumber", y="LapTimeMillis", color="Compound", markers=True,
        color_discrete_map=COMPOUND_COLORS,
    )
    st.plotly_chart(themed(fig), use_container_width=True)
    laps_display = laps.copy()
    laps_display["LapTime"] = laps_display["LapTimeMillis"].apply(format_millis)
    laps_display["Stint"] = laps_display["Stint"].astype("Int64")
    laps_display = laps_display.drop(columns=["LapTimeMillis"]).set_index("LapNumber")
    st.table(laps_display)

telemetry = run_query(
    "SELECT LapNumber, Distance, Speed, Throttle, Brake, Gear FROM vw_Telemetry "
    "WHERE Season = :season AND Round = :round AND DriverName = :driver ORDER BY LapNumber, Distance",
    {"season": SEASON, "round": round_choice, "driver": driver},
)
if not telemetry.empty:
    # When a car parks (retirement/DSQ), Distance stops advancing but the
    # sensor keeps sampling, stacking hundreds of rows on the same Distance.
    # Keep only the first sample per (LapNumber, Distance) to collapse those
    # piles into a single point instead of dropping the lap's real data.
    telemetry = telemetry.drop_duplicates(subset=["LapNumber", "Distance"], keep="first")
eyebrow(t("eyebrow_telemetry"))
if telemetry.empty:
    st.info(t("info_no_telemetry"))
else:
    lap_options = sorted(telemetry["LapNumber"].unique())
    lap_choice = st.selectbox(t("label_lap"), lap_options)
    lap_tel = telemetry[telemetry["LapNumber"] == lap_choice]
    kpi_row(
        [
            {"label": t("kpi_top_speed"), "value": f'{lap_tel["Speed"].max():.0f} km/h', "accent": "red"},
        ]
    )
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=lap_tel["Distance"], y=lap_tel["Gear"] / 8 * 100, name="Gear",
        line=dict(color=COLORS["amber"], width=2, shape="hv"),
        customdata=lap_tel["Gear"], hovertemplate="Gear %{customdata}<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=lap_tel["Distance"], y=lap_tel["Throttle"], name="Throttle",
        line=dict(color=COLORS["teal"], width=2),
        hovertemplate="Throttle %{y:.0f}%<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=lap_tel["Distance"], y=lap_tel["Speed"] / 350 * 100, name="Speed",
        line=dict(color=COLORS["red"], width=3),
        customdata=lap_tel["Speed"], hovertemplate="Speed %{customdata:.0f} km/h<extra></extra>",
    ))
    fig2 = themed(fig2)
    fig2.update_yaxes(visible=False)
    st.plotly_chart(fig2, use_container_width=True)
