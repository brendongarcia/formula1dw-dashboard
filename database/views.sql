USE Formula1DW;
GO

CREATE OR ALTER VIEW mart.vw_RaceResults AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName, ci.Name AS CircuitName, ci.Country,
    d.FullName AS DriverName, c.Name AS ConstructorName,
    fr.GridPosition, fr.FinishPosition, fr.PositionOrder, fr.Points, fr.Laps,
    st.StatusDescription
FROM dw.FactResults fr
INNER JOIN dw.DimRace ra ON ra.RaceKey = fr.RaceKey
INNER JOIN dw.DimCircuit ci ON ci.CircuitKey = ra.CircuitKey
INNER JOIN dw.DimDriver d ON d.DriverKey = fr.DriverKey
INNER JOIN dw.DimConstructor c ON c.ConstructorKey = fr.ConstructorKey
INNER JOIN dw.DimStatus st ON st.StatusKey = fr.StatusKey;
GO

CREATE OR ALTER VIEW mart.vw_DriverStandings AS
SELECT
    ra.Season, d.DriverKey, d.FullName AS DriverName,
    fr.RaceKey, ra.Round, fr.Points,
    SUM(fr.Points) OVER (PARTITION BY ra.Season, d.DriverKey ORDER BY ra.Round
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningPoints
FROM dw.FactResults fr
INNER JOIN dw.DimRace ra ON ra.RaceKey = fr.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = fr.DriverKey;
GO

CREATE OR ALTER VIEW mart.vw_ConstructorStandings AS
-- FactResults grain is (Race, Driver); a constructor fields 2 drivers per race,
-- so summing per round BEFORE the running-total window avoids two tied rows
-- per (Season, ConstructorKey, Round) that a ROWS-framed window would give
-- inconsistent partial sums (ties broken by physical row order, not value).
WITH RoundPoints AS (
    SELECT
        ra.Season, c.ConstructorKey, c.Name AS ConstructorName, ra.Round,
        SUM(fr.Points) AS RoundPoints
    FROM dw.FactResults fr
    INNER JOIN dw.DimRace ra ON ra.RaceKey = fr.RaceKey
    INNER JOIN dw.DimConstructor c ON c.ConstructorKey = fr.ConstructorKey
    GROUP BY ra.Season, c.ConstructorKey, c.Name, ra.Round
)
SELECT
    Season, ConstructorKey, ConstructorName, Round,
    SUM(RoundPoints) OVER (PARTITION BY Season, ConstructorKey ORDER BY Round
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningPoints
FROM RoundPoints;
GO

CREATE OR ALTER VIEW mart.vw_LapTimesEnriched AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    d.FullName AS DriverName,
    lt.LapNumber, lt.LapTimeMillis, lt.Position, lt.Compound, lt.Stint,
    lt.Sector1Millis, lt.Sector2Millis, lt.Sector3Millis
FROM dw.FactLapTimes lt
INNER JOIN dw.DimRace ra ON ra.RaceKey = lt.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = lt.DriverKey;
GO

CREATE OR ALTER VIEW mart.vw_QualifyingResults AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    d.FullName AS DriverName, c.Name AS ConstructorName,
    fq.Position, fq.Q1Millis, fq.Q2Millis, fq.Q3Millis
FROM dw.FactQualifying fq
INNER JOIN dw.DimRace ra ON ra.RaceKey = fq.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = fq.DriverKey
INNER JOIN dw.DimConstructor c ON c.ConstructorKey = fq.ConstructorKey;
GO

CREATE OR ALTER VIEW mart.vw_PitStops AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    d.FullName AS DriverName,
    fp.StopNumber, fp.LapNumber, fp.DurationMillis, fp.TimeOfDay
FROM dw.FactPitStops fp
INNER JOIN dw.DimRace ra ON ra.RaceKey = fp.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = fp.DriverKey;
GO

CREATE OR ALTER VIEW mart.vw_Weather AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    fw.SampleTime, fw.AirTemp, fw.TrackTemp, fw.Humidity, fw.Pressure,
    fw.WindSpeed, fw.WindDirection, fw.Rainfall
FROM dw.FactWeather fw
INNER JOIN dw.DimRace ra ON ra.RaceKey = fw.RaceKey;
GO

CREATE OR ALTER VIEW mart.vw_Telemetry AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    d.FullName AS DriverName,
    ft.LapNumber, ft.Distance, ft.SessionTime, ft.Speed, ft.RPM, ft.Gear,
    ft.Throttle, ft.Brake, ft.DRS, ft.X, ft.Y, ft.Z
FROM dw.FactTelemetry ft
INNER JOIN dw.DimRace ra ON ra.RaceKey = ft.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = ft.DriverKey;
GO

CREATE OR ALTER VIEW mart.vw_FastestSectorByDriver AS
WITH SectorTimes AS (
    SELECT RaceKey, DriverKey, 1 AS SectorNumber, Sector1Millis AS SectorMillis FROM dw.FactLapTimes WHERE Sector1Millis IS NOT NULL
    UNION ALL
    SELECT RaceKey, DriverKey, 2, Sector2Millis FROM dw.FactLapTimes WHERE Sector2Millis IS NOT NULL
    UNION ALL
    SELECT RaceKey, DriverKey, 3, Sector3Millis FROM dw.FactLapTimes WHERE Sector3Millis IS NOT NULL
),
Fastest AS (
    SELECT RaceKey, SectorNumber, MIN(SectorMillis) AS FastestSectorMillis
    FROM SectorTimes GROUP BY RaceKey, SectorNumber
),
FastestTiebroken AS (
    SELECT st.RaceKey, st.SectorNumber, st.SectorMillis, st.DriverKey,
           ROW_NUMBER() OVER (PARTITION BY st.RaceKey, st.SectorNumber ORDER BY st.SectorMillis, st.DriverKey) AS rn
    FROM SectorTimes st
    INNER JOIN Fastest f ON f.RaceKey = st.RaceKey AND f.SectorNumber = st.SectorNumber AND f.FastestSectorMillis = st.SectorMillis
)
SELECT ft.RaceKey, ra.Season, ra.Round, ra.Name AS RaceName,
       ft.SectorNumber, ft.SectorMillis AS FastestSectorMillis, d.FullName AS FastestDriverName
FROM FastestTiebroken ft
INNER JOIN dw.DimRace ra ON ra.RaceKey = ft.RaceKey
INNER JOIN dw.DimDriver d ON d.DriverKey = ft.DriverKey
WHERE ft.rn = 1;
GO

CREATE OR ALTER VIEW mart.vw_TrackMapFastestSector AS
SELECT
    ra.Season, ra.Round, ra.Name AS RaceName,
    ts.SectorNumber, ts.Distance, ts.X, ts.Y,
    fs.FastestDriverName, fs.FastestSectorMillis
FROM dw.FactTrackSegment ts
INNER JOIN dw.DimRace ra ON ra.RaceKey = ts.RaceKey
INNER JOIN mart.vw_FastestSectorByDriver fs ON fs.RaceKey = ts.RaceKey AND fs.SectorNumber = ts.SectorNumber;
GO
