import streamlit as st
import plotly.express as px
from db import run_query
from style import inject, eyebrow, kpi_row, themed, live_badge, PLOTLY_CONFIG
from i18n import lang_selector, t

SEASON = 2025

st.set_page_config(layout="wide")
inject()
lang_selector()
st.title(t("page_title_standings"))
live_badge(t("season_caption", season=SEASON))

driver_df = run_query(
    "SELECT Round, DriverName, RunningPoints FROM vw_DriverStandings "
    "WHERE Season = :season ORDER BY Round",
    {"season": SEASON},
)

final_round = driver_df["Round"].max()
final_driver = (
    driver_df.loc[driver_df.groupby("DriverName")["Round"].idxmax()]
    .sort_values("RunningPoints", ascending=False)
    .reset_index(drop=True)
)

leader = final_driver.iloc[0]
gap = leader["RunningPoints"] - (final_driver.iloc[1]["RunningPoints"] if len(final_driver) > 1 else leader["RunningPoints"])
kpi_row(
    [
        {"label": t("kpi_championship_leader"), "value": leader["DriverName"], "accent": "red"},
        {"label": t("kpi_points"), "value": f'{leader["RunningPoints"]:.0f}', "accent": "teal"},
        {"label": t("kpi_gap_2nd"), "value": f"+{gap:.0f}", "accent": "amber"},
        {"label": t("kpi_rounds_completed"), "value": int(final_round), "accent": "purple"},
    ]
)

eyebrow(t("eyebrow_drivers"))
fig = themed(px.line(driver_df, x="Round", y="RunningPoints", color="DriverName", markers=True))
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
st.dataframe(final_driver, use_container_width=True, height=420)

constructor_df = run_query(
    "SELECT Round, ConstructorName, RunningPoints FROM vw_ConstructorStandings "
    "WHERE Season = :season ORDER BY Round",
    {"season": SEASON},
)

eyebrow(t("eyebrow_constructors"))
fig2 = themed(px.line(constructor_df, x="Round", y="RunningPoints", color="ConstructorName", markers=True))
st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

final_constructor = (
    constructor_df.loc[constructor_df.groupby("ConstructorName")["Round"].idxmax()]
    .sort_values("RunningPoints", ascending=False)
    .reset_index(drop=True)
)
st.dataframe(final_constructor, use_container_width=True, height=420)
