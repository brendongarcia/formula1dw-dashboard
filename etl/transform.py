import pandas as pd


def _timedelta_to_millis(td):
    if pd.isna(td):
        return None
    return int(td.total_seconds() * 1000)


def transform_drivers(df):
    out = pd.DataFrame({
        "DriverId": df["driverId"],
        "DriverRef": df["driverId"],
        "Code": df["driverCode"],
        "PermanentNumber": df["driverNumber"].astype("Int64"),
        "Forename": df["givenName"],
        "Surname": df["familyName"],
        "Nationality": df["driverNationality"],
        "DateOfBirth": pd.to_datetime(df["dateOfBirth"]).dt.date,
        "Url": df["driverUrl"],
    })
    return out.dropna(subset=["DriverId"]).drop_duplicates(subset=["DriverId"])


def transform_constructors(df):
    out = pd.DataFrame({
        "ConstructorId": df["constructorId"],
        "ConstructorRef": df["constructorId"],
        "Name": df["constructorName"],
        "Nationality": df["constructorNationality"],
        "Url": df["constructorUrl"],
    })
    return out.dropna(subset=["ConstructorId"]).drop_duplicates(subset=["ConstructorId"])


def transform_circuits(df):
    out = pd.DataFrame({
        "CircuitId": df["circuitId"],
        "CircuitRef": df["circuitId"],
        "Name": df["circuitName"],
        "Location": df["locality"],
        "Country": df["country"],
        "Lat": df["lat"],
        "Lng": df["long"],
        "Alt": pd.array([None] * len(df), dtype="Int64"),
        "Url": df["circuitUrl"],
    })
    return out.dropna(subset=["CircuitId"]).drop_duplicates(subset=["CircuitId"])


def transform_races(df):
    out = pd.DataFrame({
        "RaceId": df["season"].astype(str) + "-" + df["round"].astype(str),
        "Season": df["season"].astype("Int64"),
        "Round": df["round"].astype("Int64"),
        "Name": df["raceName"],
        "CircuitId": df["circuitId"],
        "RaceDate": pd.to_datetime(df["raceDate"]).dt.date,
        "RaceTime": df["raceTime"].apply(lambda t: t.replace(tzinfo=None) if pd.notna(t) else None),
        "Url": df["raceUrl"],
    })
    return out.dropna(subset=["RaceId"]).drop_duplicates(subset=["RaceId"])


def transform_status(df):
    out = pd.DataFrame({
        "StatusId": df["statusId"].astype("Int64"),
        "StatusDescription": df["status"],
    })
    return out.dropna(subset=["StatusId"]).drop_duplicates(subset=["StatusId"])


def transform_results(results_df, status_df, race_id):
    status_map = dict(zip(status_df["status"], status_df["statusId"]))

    out = pd.DataFrame({
        "RaceId": race_id,
        "DriverId": results_df["driverId"],
        "ConstructorId": results_df["constructorId"],
        "StatusId": results_df["status"].map(status_map).astype("Int64"),
        "GridPosition": results_df["grid"].astype("Int64"),
        "FinishPosition": pd.to_numeric(results_df["position"], errors="coerce").astype("Int64"),
        "PositionOrder": range(1, len(results_df) + 1),
        "Points": results_df["points"].astype(float),
        "Laps": results_df["laps"].astype("Int64"),
        "TimeMillis": pd.to_numeric(results_df["totalRaceTimeMillis"], errors="coerce").astype("Int64"),
        "FastestLapNumber": pd.to_numeric(results_df["fastestLapNumber"], errors="coerce").astype("Int64"),
        "FastestLapTimeMillis": results_df["fastestLapTime"].apply(_timedelta_to_millis),
        "FastestLapSpeedKph": pd.to_numeric(results_df["fastestLapAvgSpeed"], errors="coerce"),
        "FastestLapRank": pd.to_numeric(results_df["fastestLapRank"], errors="coerce").astype("Int64"),
    })
    return out.dropna(subset=["DriverId", "StatusId"])


def transform_qualifying(df, race_id):
    out = pd.DataFrame({
        "RaceId": race_id,
        "DriverId": df["driverId"],
        "ConstructorId": df["constructorId"],
        "Position": df["position"].astype("Int64"),
        "Q1Millis": df["Q1"].apply(_timedelta_to_millis),
        "Q2Millis": df["Q2"].apply(_timedelta_to_millis),
        "Q3Millis": df["Q3"].apply(_timedelta_to_millis),
    })
    return out.dropna(subset=["DriverId"])


def transform_pit_stops(df, race_id):
    out = pd.DataFrame({
        "RaceId": race_id,
        "DriverId": df["driverId"],
        "StopNumber": df["stop"].astype("Int64"),
        "LapNumber": df["lap"].astype("Int64"),
        "DurationMillis": df["duration"].apply(_timedelta_to_millis),
        "TimeOfDay": pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.time,
    })
    return out.dropna(subset=["DriverId"])


def transform_lap_times(laps_df, results_df, race_id):
    number_to_driver_id = dict(zip(results_df["driverNumber"].astype(str), results_df["driverId"]))
    driver_ids = laps_df["DriverNumber"].astype(str).map(number_to_driver_id)

    out = pd.DataFrame({
        "RaceId": race_id,
        "DriverId": driver_ids,
        "LapNumber": laps_df["LapNumber"].astype("Int64"),
        "LapTimeMillis": laps_df["LapTime"].apply(_timedelta_to_millis),
        "Position": pd.to_numeric(laps_df["Position"], errors="coerce").astype("Int64"),
        "Compound": laps_df["Compound"],
        "Stint": laps_df["Stint"].astype("Int64"),
        "Sector1Millis": laps_df["Sector1Time"].apply(_timedelta_to_millis),
        "Sector2Millis": laps_df["Sector2Time"].apply(_timedelta_to_millis),
        "Sector3Millis": laps_df["Sector3Time"].apply(_timedelta_to_millis),
        "IsPersonalBest": laps_df["IsPersonalBest"].astype(bool),
        "TrackStatus": laps_df["TrackStatus"].astype(str),
    })
    return out.dropna(subset=["DriverId"]).drop_duplicates(subset=["RaceId", "DriverId", "LapNumber"])


def transform_weather(weather_df, session_date, race_id):
    out = pd.DataFrame({
        "RaceId": race_id,
        "SampleTime": weather_df["Time"].apply(lambda td: session_date + td),
        "AirTemp": weather_df["AirTemp"],
        "TrackTemp": weather_df["TrackTemp"],
        "Humidity": weather_df["Humidity"],
        "Pressure": weather_df["Pressure"],
        "WindSpeed": weather_df["WindSpeed"],
        "WindDirection": weather_df["WindDirection"].astype("Int64"),
        "Rainfall": weather_df["Rainfall"].astype(bool),
    })
    return out.drop_duplicates(subset=["RaceId", "SampleTime"])
