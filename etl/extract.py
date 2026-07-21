import fastf1
import pandas as pd
from fastf1.ergast import Ergast

from etl.utils import retry

_ergast = Ergast(result_type="pandas", auto_cast=True)

_RACE_RESULTS_COLUMNS = [
    "number", "position", "positionText", "points", "grid", "laps", "status",
    "driverId", "driverNumber", "driverCode", "driverUrl", "givenName", "familyName",
    "dateOfBirth", "driverNationality", "constructorId", "constructorUrl", "constructorName",
    "constructorNationality", "totalRaceTimeMillis", "totalRaceTime", "fastestLapRank",
    "fastestLapNumber", "fastestLapTime", "fastestLapAvgSpeedUnits", "fastestLapAvgSpeed",
]
_QUALIFYING_RESULTS_COLUMNS = [
    "number", "position", "Q1", "Q2", "Q3", "driverId", "driverNumber", "driverCode",
    "driverUrl", "givenName", "familyName", "dateOfBirth", "driverNationality",
    "constructorId", "constructorUrl", "constructorName", "constructorNationality",
]
_PIT_STOPS_COLUMNS = ["driverId", "stop", "lap", "time", "duration"]


def _first_or_empty(response, columns):
    # ponytail: some races (e.g. red-flagged ones) have no data for a given
    # endpoint -- Jolpica returns an empty content list rather than an error.
    # Jolpica also drops columns that are null for every row in a race (e.g.
    # fastestLapAvgSpeed), so reindex to the expected columns either way.
    df = response.content[0] if response.content else pd.DataFrame(columns=columns)
    return df.reindex(columns=columns)


@retry()
def extract_drivers(season):
    return _ergast.get_driver_info(season=season)


@retry()
def extract_constructors(season):
    return _ergast.get_constructor_info(season=season)


@retry()
def extract_circuits(season):
    return _ergast.get_circuits(season=season)


@retry()
def extract_race_schedule(season):
    return _ergast.get_race_schedule(season=season)


@retry()
def extract_finishing_status(season, round_):
    return _ergast.get_finishing_status(season=season, round=round_)


@retry()
def extract_race_results(season, round_):
    response = _ergast.get_race_results(season=season, round=round_)
    return _first_or_empty(response, _RACE_RESULTS_COLUMNS)


@retry()
def extract_qualifying_results(season, round_):
    response = _ergast.get_qualifying_results(season=season, round=round_)
    return _first_or_empty(response, _QUALIFYING_RESULTS_COLUMNS)


@retry()
def extract_pit_stops(season, round_):
    response = _ergast.get_pit_stops(season=season, round=round_)
    return _first_or_empty(response, _PIT_STOPS_COLUMNS)


@retry()
def extract_session(season, round_):
    session = fastf1.get_session(season, round_, "R")
    session.load(laps=True, weather=True, telemetry=False)
    return session


def get_lap_times(session):
    return session.laps


def get_weather(session):
    return session.weather_data, session.date
