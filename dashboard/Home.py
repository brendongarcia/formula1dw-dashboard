import streamlit as st
import plotly.express as px
from db import get_engine, run_query
from style import inject, eyebrow, kpi_row, themed, format_millis, live_badge, PLOTLY_CONFIG
from i18n import lang_selector, t

SEASON = 2025

st.set_page_config(page_title="Formula1DW Dashboard", layout="wide")
inject()
lang_selector()

st.title("Formula1DW")
st.markdown(t("home_subtitle", season=SEASON))
live_badge(t("season_caption", season=SEASON))

try:
    get_engine().connect().close()

    stats = run_query(
        "SELECT COUNT(DISTINCT Round) AS Races FROM vw_RaceResults WHERE Season = :season",
        {"season": SEASON},
    ).iloc[0]

    driver_leader = run_query(
        "SELECT DriverName, RunningPoints FROM vw_DriverStandings "
        "WHERE Season = :season ORDER BY Round DESC, RunningPoints DESC LIMIT 1",
        {"season": SEASON},
    )
    constructor_leader = run_query(
        "SELECT ConstructorName, RunningPoints FROM vw_ConstructorStandings "
        "WHERE Season = :season ORDER BY Round DESC, RunningPoints DESC LIMIT 1",
        {"season": SEASON},
    )
    most_wins = run_query(
        "SELECT DriverName, COUNT(*) AS Wins FROM vw_RaceResults "
        "WHERE Season = :season AND PositionOrder = 1 GROUP BY DriverName ORDER BY Wins DESC LIMIT 1",
        {"season": SEASON},
    )
    most_poles = run_query(
        "SELECT DriverName, COUNT(*) AS Poles FROM vw_QualifyingResults "
        "WHERE Season = :season AND Position = 1 GROUP BY DriverName ORDER BY Poles DESC LIMIT 1",
        {"season": SEASON},
    )
    fastest_lap = run_query(
        "SELECT DriverName, RaceName, LapTimeMillis FROM vw_LapTimesEnriched "
        "WHERE Season = :season ORDER BY LapTimeMillis ASC LIMIT 1",
        {"season": SEASON},
    )

    kpi_row(
        [
            {"label": t("kpi_season"), "value": SEASON, "accent": "amber"},
            {"label": t("kpi_races_completed"), "value": int(stats["Races"]), "accent": "teal"},
            {
                "label": t("kpi_leader_driver"),
                "value": driver_leader.iloc[0]["DriverName"] if not driver_leader.empty else "—",
                "sub": f'{driver_leader.iloc[0]["RunningPoints"]:.0f} {t("unit_pts")}' if not driver_leader.empty else "",
                "accent": "red",
            },
            {
                "label": t("kpi_leader_constructor"),
                "value": constructor_leader.iloc[0]["ConstructorName"] if not constructor_leader.empty else "—",
                "sub": f'{constructor_leader.iloc[0]["RunningPoints"]:.0f} {t("unit_pts")}' if not constructor_leader.empty else "",
                "accent": "purple",
            },
            {
                "label": t("kpi_most_wins"),
                "value": most_wins.iloc[0]["DriverName"] if not most_wins.empty else "—",
                "sub": f'{int(most_wins.iloc[0]["Wins"])} {t("unit_wins")}' if not most_wins.empty else "",
                "accent": "red",
            },
            {
                "label": t("kpi_most_poles"),
                "value": most_poles.iloc[0]["DriverName"] if not most_poles.empty else "—",
                "sub": f'{int(most_poles.iloc[0]["Poles"])} {t("unit_poles")}' if not most_poles.empty else "",
                "accent": "amber",
            },
            {
                "label": t("kpi_season_fastest_lap"),
                "value": fastest_lap.iloc[0]["DriverName"] if not fastest_lap.empty else "—",
                "sub": f'{format_millis(fastest_lap.iloc[0]["LapTimeMillis"])}s · {fastest_lap.iloc[0]["RaceName"]}' if not fastest_lap.empty else "",
                "accent": "teal",
            },
        ]
    )

    driver_points = run_query(
        "SELECT DriverName, RunningPoints FROM vw_DriverStandings "
        "WHERE Season = :season AND Round = (SELECT MAX(Round) FROM vw_DriverStandings WHERE Season = :season) "
        "ORDER BY RunningPoints DESC LIMIT 5",
        {"season": SEASON},
    )
    constructor_points = run_query(
        "SELECT ConstructorName, RunningPoints FROM vw_ConstructorStandings "
        "WHERE Season = :season AND Round = (SELECT MAX(Round) FROM vw_ConstructorStandings WHERE Season = :season) "
        "ORDER BY RunningPoints DESC",
        {"season": SEASON},
    )

    col1, col2 = st.columns(2)
    with col1:
        eyebrow(t("eyebrow_top_drivers"))
        fig = px.bar(
            driver_points.sort_values("RunningPoints"),
            x="RunningPoints", y="DriverName", orientation="h", text="RunningPoints",
        )
        st.plotly_chart(themed(fig, height=420), use_container_width=True, config=PLOTLY_CONFIG)
    with col2:
        eyebrow(t("eyebrow_top_constructors"))
        fig2 = px.bar(
            constructor_points.sort_values("RunningPoints"),
            x="RunningPoints", y="ConstructorName", orientation="h", text="RunningPoints",
        )
        st.plotly_chart(themed(fig2, height=420), use_container_width=True, config=PLOTLY_CONFIG)

    st.success(t("connected"))
except Exception as e:
    st.error(t("connect_error", error=e))

st.markdown(
    f"""
- {t("nav_standings")}
- {t("nav_corrida")}
- {t("nav_laps")}
- {t("nav_trackmap")}
"""
)
