import streamlit as st

_STRINGS = {
    "lang_label": {"pt": "Idioma", "en": "Language"},
    "home_subtitle": {
        "pt": "Uma visão geral da temporada {season}: classificação de "
        "pilotos e equipes, fins de semana de corrida, ritmo volta a volta e "
        "geometria de pista por setor.",
        "en": "A pit-wall view of the {season} season: driver and constructor "
        "standings, race weekends, lap-by-lap pace, and per-sector track geometry.",
    },
    "kpi_season": {"pt": "Temporada", "en": "Season"},
    "kpi_races_completed": {"pt": "Corridas Realizadas", "en": "Races Completed"},
    "kpi_championship_leader": {"pt": "Líder do Campeonato", "en": "Championship Leader"},
    "kpi_leader_driver": {"pt": "Líder Piloto", "en": "Leader Driver"},
    "kpi_leader_constructor": {"pt": "Líder Construtor", "en": "Leader Constructor"},
    "kpi_most_wins": {"pt": "Mais Vitórias", "en": "Most Wins"},
    "kpi_most_poles": {"pt": "Mais Poles", "en": "Most Poles"},
    "kpi_season_fastest_lap": {"pt": "Volta Rápida", "en": "Fastest Lap"},
    "unit_pts": {"pt": "pts", "en": "pts"},
    "unit_wins": {"pt": "vitórias", "en": "wins"},
    "unit_poles": {"pt": "poles", "en": "poles"},
    "eyebrow_top_drivers": {"pt": "Pilotos — Pontos (Top 5)", "en": "Drivers — Points (Top 5)"},
    "eyebrow_top_constructors": {"pt": "Construtores — Pontos", "en": "Constructors — Points"},
    "connected": {"pt": "Conectado ao Formula1DW", "en": "Connected to Formula1DW"},
    "connect_error": {
        "pt": "Não foi possível conectar ao Formula1DW: {error}",
        "en": "Could not connect to Formula1DW: {error}",
    },
    "nav_standings": {
        "pt": "**Classificação** — evolução de pontos de pilotos e equipes",
        "en": "**Standings** — driver/constructor points progression",
    },
    "nav_corrida": {
        "pt": "**Corrida** — resultado, classificação de largada, pit stops e clima de uma corrida",
        "en": "**Corrida** — race results, qualifying, pit stops, weather for one race",
    },
    "nav_laps": {
        "pt": "**Voltas & Telemetria** — tempos de volta e telemetria do carro de um piloto/corrida",
        "en": "**Laps & Telemetry** — lap times and car telemetry for one driver/race",
    },
    "nav_trackmap": {
        "pt": "**Mapa da Pista** — geometria da pista pelo setor mais rápido de cada corrida",
        "en": "**Track Map** — fastest-sector track geometry per race",
    },
    "season_caption": {"pt": "temporada {season}", "en": "{season} season"},
    "page_title_standings": {"pt": "Classificação", "en": "Standings"},
    "kpi_points": {"pt": "Pontos", "en": "Points"},
    "kpi_gap_2nd": {"pt": "Diferença para o 2º", "en": "Gap to 2nd"},
    "kpi_rounds_completed": {"pt": "Etapas Realizadas", "en": "Rounds Completed"},
    "eyebrow_drivers": {"pt": "Pilotos", "en": "Drivers"},
    "eyebrow_constructors": {"pt": "Equipes", "en": "Constructors"},
    "page_title_race": {"pt": "Corrida", "en": "Race"},
    "label_race": {"pt": "Corrida", "en": "Race"},
    "kpi_winner": {"pt": "Vencedor", "en": "Winner"},
    "kpi_pole": {"pt": "Pole Position", "en": "Pole Position"},
    "kpi_finishers": {"pt": "Terminaram a Prova", "en": "Finishers"},
    "kpi_dnfs": {"pt": "Abandonos", "en": "DNFs"},
    "eyebrow_race_results": {"pt": "Resultado da Corrida", "en": "Race Results"},
    "eyebrow_qualifying": {"pt": "Classificação de Largada", "en": "Qualifying"},
    "eyebrow_pit_stops": {"pt": "Pit Stops", "en": "Pit Stops"},
    "eyebrow_weather": {"pt": "Clima", "en": "Weather"},
    "info_no_pit_stops": {
        "pt": "Sem dados de pit stop para esta corrida",
        "en": "No pit stop data loaded for this race",
    },
    "info_no_weather": {
        "pt": "Sem dados de clima para esta corrida",
        "en": "No weather data loaded for this race",
    },
    "page_title_laps": {"pt": "Voltas & Telemetria", "en": "Laps & Telemetry"},
    "label_driver": {"pt": "Piloto", "en": "Driver"},
    "label_lap": {"pt": "Volta", "en": "Lap"},
    "eyebrow_lap_times": {"pt": "Tempos de Volta", "en": "Lap Times"},
    "eyebrow_telemetry": {"pt": "Telemetria", "en": "Telemetry"},
    "info_no_laps": {
        "pt": "Sem dados de volta para este piloto/corrida",
        "en": "No lap data for this driver/race",
    },
    "kpi_best_lap": {"pt": "Melhor Volta", "en": "Best Lap"},
    "kpi_average_lap": {"pt": "Volta Média", "en": "Average Lap"},
    "kpi_laps_completed": {"pt": "Voltas Completadas", "en": "Laps Completed"},
    "info_no_telemetry": {
        "pt": "Telemetria ainda não carregada para este piloto/corrida",
        "en": "No telemetry loaded for this driver/race yet",
    },
    "kpi_top_speed": {"pt": "Velocidade Máxima", "en": "Top Speed"},
    "page_title_trackmap": {"pt": "Mapa da Pista", "en": "Track Map"},
    "info_no_trackmap_season": {
        "pt": "Mapa da pista ainda não calculado para esta temporada — rode "
        "etl/track_map.py para uma corrida primeiro",
        "en": "No track map data loaded yet for this season — run "
        "etl/track_map.py for a race first",
    },
    "info_no_trackmap_race": {
        "pt": "Mapa da pista ainda não calculado para esta corrida",
        "en": "Track map not computed for this race yet",
    },
    "kpi_sector": {"pt": "Setor {n}", "en": "Sector {n}"},
    "eyebrow_track_geometry": {
        "pt": "Geometria do Setor Mais Rápido",
        "en": "Fastest Sector Geometry",
    },
    "eyebrow_lap_ranking": {"pt": "Ranking de Volta", "en": "Lap Ranking"},
    "col_rank": {"pt": "Pos", "en": "Pos"},
    "col_driver": {"pt": "Piloto", "en": "Driver"},
    "col_best_lap": {"pt": "Melhor Volta", "en": "Best Lap"},
    "col_gap": {"pt": "Gap", "en": "Gap"},
    "info_no_lap_ranking": {
        "pt": "Sem dados de volta para esta corrida",
        "en": "No lap data for this race",
    },
}


def lang_selector():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "pt"
    current = st.session_state["lang"]
    options = ["pt", "en"]
    choice = st.sidebar.selectbox(
        _STRINGS["lang_label"][current],
        options=options,
        format_func=lambda l: "Português" if l == "pt" else "English",
        index=options.index(current),
        key="lang_widget",
    )
    st.session_state["lang"] = choice


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "pt")
    text = _STRINGS[key][lang]
    return text.format(**kwargs) if kwargs else text
