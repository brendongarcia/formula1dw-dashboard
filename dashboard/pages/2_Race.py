import streamlit as st
import plotly.express as px
from db import run_query
from style import inject, eyebrow, kpi_row, themed, format_millis, live_badge, PLOTLY_CONFIG
from i18n import lang_selector, t

SEASON = 2025

st.set_page_config(layout="wide")
inject()
lang_selector()
st.title(t("page_title_race"))
live_badge(t("season_caption", season=SEASON))

rounds = run_query(
    "SELECT DISTINCT Round, RaceName FROM vw_RaceResults "
    "WHERE Season = :season ORDER BY Round",
    {"season": SEASON},
)
round_choice = st.selectbox(
    t("label_race"), rounds["Round"],
    format_func=lambda r: rounds.set_index("Round").loc[r, "RaceName"],
)

results = run_query(
    "SELECT DriverName, ConstructorName, GridPosition, FinishPosition, Points, Laps, StatusDescription "
    "FROM vw_RaceResults WHERE Season = :season AND Round = :round ORDER BY PositionOrder",
    {"season": SEASON, "round": round_choice},
)

winner = results.iloc[0]
finishers = int((results["StatusDescription"].isin(["Finished", "Lapped", "+1 Lap", "+2 Laps"])).sum())
dnfs = len(results) - finishers
qualifying_preview = run_query(
    "SELECT DriverName FROM vw_QualifyingResults "
    "WHERE Season = :season AND Round = :round AND Position = 1",
    {"season": SEASON, "round": round_choice},
)
pole = qualifying_preview["DriverName"].iloc[0] if not qualifying_preview.empty else "—"

kpi_row(
    [
        {"label": t("kpi_winner"), "value": winner["DriverName"], "accent": "red"},
        {"label": t("kpi_pole"), "value": pole, "accent": "purple"},
        {"label": t("kpi_finishers"), "value": finishers, "accent": "teal"},
        {"label": t("kpi_dnfs"), "value": dnfs, "accent": "amber"},
    ]
)

eyebrow(t("eyebrow_race_results"))
st.dataframe(results, use_container_width=True, height=420)

qualifying = run_query(
    "SELECT DriverName, ConstructorName, Position, Q1Millis, Q2Millis, Q3Millis "
    "FROM vw_QualifyingResults WHERE Season = :season AND Round = :round ORDER BY Position",
    {"season": SEASON, "round": round_choice},
)
qualifying_display = qualifying.copy()
for col in ("Q1Millis", "Q2Millis", "Q3Millis"):
    qualifying_display[col.replace("Millis", "")] = qualifying_display[col].apply(format_millis)
qualifying_display = qualifying_display.drop(columns=["Q1Millis", "Q2Millis", "Q3Millis"])

eyebrow(t("eyebrow_qualifying"))
st.dataframe(qualifying_display, use_container_width=True, height=420)

pit_stops = run_query(
    "SELECT DriverName, StopNumber, LapNumber, DurationMillis, TimeOfDay "
    "FROM vw_PitStops WHERE Season = :season AND Round = :round ORDER BY DriverName, StopNumber",
    {"season": SEASON, "round": round_choice},
)
eyebrow(t("eyebrow_pit_stops"))
if pit_stops.empty:
    st.info(t("info_no_pit_stops"))
else:
    pit_stops_display = pit_stops.copy()
    pit_stops_display["Duration"] = pit_stops_display["DurationMillis"].apply(format_millis)
    pit_stops_display = pit_stops_display.drop(columns=["DurationMillis"])
    st.dataframe(pit_stops_display, use_container_width=True, height=360)

weather = run_query(
    "SELECT SampleTime, AirTemp, TrackTemp, Humidity, Pressure, WindSpeed, WindDirection, Rainfall "
    "FROM vw_Weather WHERE Season = :season AND Round = :round ORDER BY SampleTime",
    {"season": SEASON, "round": round_choice},
)
eyebrow(t("eyebrow_weather"))
if weather.empty:
    st.info(t("info_no_weather"))
else:
    fig = themed(px.line(weather, x="SampleTime", y=["AirTemp", "TrackTemp"]), height=420)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
