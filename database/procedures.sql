USE Formula1DW;
GO

SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_DimStatus
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.DimStatus AS tgt
        USING stg.Status AS src
            ON tgt.StatusId = src.StatusId
        WHEN MATCHED THEN
            UPDATE SET tgt.StatusDescription = src.StatusDescription
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (StatusId, StatusDescription) VALUES (src.StatusId, src.StatusDescription);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.DimStatus', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.DimStatus', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_DimDriver
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.DimDriver AS tgt
        USING stg.Driver AS src
            ON tgt.DriverId = src.DriverId
        WHEN MATCHED THEN
            UPDATE SET tgt.DriverRef = src.DriverRef, tgt.Code = src.Code,
                       tgt.PermanentNumber = src.PermanentNumber, tgt.Forename = src.Forename,
                       tgt.Surname = src.Surname, tgt.Nationality = src.Nationality,
                       tgt.DateOfBirth = src.DateOfBirth, tgt.Url = src.Url
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (DriverId, DriverRef, Code, PermanentNumber, Forename, Surname, Nationality, DateOfBirth, Url)
            VALUES (src.DriverId, src.DriverRef, src.Code, src.PermanentNumber, src.Forename, src.Surname, src.Nationality, src.DateOfBirth, src.Url);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.DimDriver', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.DimDriver', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_DimConstructor
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.DimConstructor AS tgt
        USING stg.Constructor AS src
            ON tgt.ConstructorId = src.ConstructorId
        WHEN MATCHED THEN
            UPDATE SET tgt.ConstructorRef = src.ConstructorRef, tgt.Name = src.Name,
                       tgt.Nationality = src.Nationality, tgt.Url = src.Url
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (ConstructorId, ConstructorRef, Name, Nationality, Url)
            VALUES (src.ConstructorId, src.ConstructorRef, src.Name, src.Nationality, src.Url);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.DimConstructor', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.DimConstructor', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_DimCircuit
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.DimCircuit AS tgt
        USING stg.Circuit AS src
            ON tgt.CircuitId = src.CircuitId
        WHEN MATCHED THEN
            UPDATE SET tgt.CircuitRef = src.CircuitRef, tgt.Name = src.Name, tgt.Location = src.Location,
                       tgt.Country = src.Country, tgt.Lat = src.Lat, tgt.Lng = src.Lng,
                       tgt.Alt = src.Alt, tgt.Url = src.Url
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (CircuitId, CircuitRef, Name, Location, Country, Lat, Lng, Alt, Url)
            VALUES (src.CircuitId, src.CircuitRef, src.Name, src.Location, src.Country, src.Lat, src.Lng, src.Alt, src.Url);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.DimCircuit', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.DimCircuit', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_DimRace
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.DimRace AS tgt
        USING (
            SELECT r.RaceId, r.Season, r.Round, r.Name, c.CircuitKey,
                   CONVERT(INT, CONVERT(VARCHAR(8), r.RaceDate, 112)) AS DateKey,
                   r.RaceTime, r.Url
            FROM stg.Race r
            INNER JOIN dw.DimCircuit c ON c.CircuitId = r.CircuitId
        ) AS src
            ON tgt.RaceId = src.RaceId
        WHEN MATCHED THEN
            UPDATE SET tgt.Season = src.Season, tgt.Round = src.Round, tgt.Name = src.Name,
                       tgt.CircuitKey = src.CircuitKey, tgt.DateKey = src.DateKey,
                       tgt.RaceTime = src.RaceTime, tgt.Url = src.Url
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceId, Season, Round, Name, CircuitKey, DateKey, RaceTime, Url)
            VALUES (src.RaceId, src.Season, src.Round, src.Name, src.CircuitKey, src.DateKey, src.RaceTime, src.Url);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.DimRace', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.DimRace', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_FactResults
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.FactResults AS tgt
        USING (
            SELECT ra.RaceKey, dr.DriverKey, co.ConstructorKey, st.StatusKey,
                   s.GridPosition, s.FinishPosition, s.PositionOrder, s.Points, s.Laps,
                   s.TimeMillis, s.FastestLapNumber, s.FastestLapTimeMillis,
                   s.FastestLapSpeedKph, s.FastestLapRank
            FROM stg.Result s
            INNER JOIN dw.DimRace ra ON ra.RaceId = s.RaceId
            INNER JOIN dw.DimDriver dr ON dr.DriverId = s.DriverId
            INNER JOIN dw.DimConstructor co ON co.ConstructorId = s.ConstructorId
            INNER JOIN dw.DimStatus st ON st.StatusId = s.StatusId
        ) AS src
            ON tgt.RaceKey = src.RaceKey AND tgt.DriverKey = src.DriverKey
        WHEN MATCHED THEN
            UPDATE SET tgt.ConstructorKey = src.ConstructorKey, tgt.StatusKey = src.StatusKey,
                       tgt.GridPosition = src.GridPosition, tgt.FinishPosition = src.FinishPosition,
                       tgt.PositionOrder = src.PositionOrder, tgt.Points = src.Points, tgt.Laps = src.Laps,
                       tgt.TimeMillis = src.TimeMillis, tgt.FastestLapNumber = src.FastestLapNumber,
                       tgt.FastestLapTimeMillis = src.FastestLapTimeMillis,
                       tgt.FastestLapSpeedKph = src.FastestLapSpeedKph, tgt.FastestLapRank = src.FastestLapRank
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceKey, DriverKey, ConstructorKey, StatusKey, GridPosition, FinishPosition, PositionOrder,
                    Points, Laps, TimeMillis, FastestLapNumber, FastestLapTimeMillis, FastestLapSpeedKph, FastestLapRank)
            VALUES (src.RaceKey, src.DriverKey, src.ConstructorKey, src.StatusKey, src.GridPosition, src.FinishPosition,
                    src.PositionOrder, src.Points, src.Laps, src.TimeMillis, src.FastestLapNumber,
                    src.FastestLapTimeMillis, src.FastestLapSpeedKph, src.FastestLapRank);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.FactResults', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.FactResults', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_FactQualifying
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.FactQualifying AS tgt
        USING (
            SELECT ra.RaceKey, dr.DriverKey, co.ConstructorKey,
                   q.Position, q.Q1Millis, q.Q2Millis, q.Q3Millis
            FROM stg.Qualifying q
            INNER JOIN dw.DimRace ra ON ra.RaceId = q.RaceId
            INNER JOIN dw.DimDriver dr ON dr.DriverId = q.DriverId
            INNER JOIN dw.DimConstructor co ON co.ConstructorId = q.ConstructorId
        ) AS src
            ON tgt.RaceKey = src.RaceKey AND tgt.DriverKey = src.DriverKey
        WHEN MATCHED THEN
            UPDATE SET tgt.ConstructorKey = src.ConstructorKey, tgt.Position = src.Position,
                       tgt.Q1Millis = src.Q1Millis, tgt.Q2Millis = src.Q2Millis, tgt.Q3Millis = src.Q3Millis
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceKey, DriverKey, ConstructorKey, Position, Q1Millis, Q2Millis, Q3Millis)
            VALUES (src.RaceKey, src.DriverKey, src.ConstructorKey, src.Position, src.Q1Millis, src.Q2Millis, src.Q3Millis);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.FactQualifying', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.FactQualifying', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_FactLapTimes
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.FactLapTimes AS tgt
        USING (
            SELECT ra.RaceKey, dr.DriverKey, l.LapNumber, l.LapTimeMillis, l.Position, l.Compound,
                   l.Stint, l.Sector1Millis, l.Sector2Millis, l.Sector3Millis, l.IsPersonalBest, l.TrackStatus
            FROM stg.LapTime l
            INNER JOIN dw.DimRace ra ON ra.RaceId = l.RaceId
            INNER JOIN dw.DimDriver dr ON dr.DriverId = l.DriverId
        ) AS src
            ON tgt.RaceKey = src.RaceKey AND tgt.DriverKey = src.DriverKey AND tgt.LapNumber = src.LapNumber
        WHEN MATCHED THEN
            UPDATE SET tgt.LapTimeMillis = src.LapTimeMillis, tgt.Position = src.Position, tgt.Compound = src.Compound,
                       tgt.Stint = src.Stint, tgt.Sector1Millis = src.Sector1Millis, tgt.Sector2Millis = src.Sector2Millis,
                       tgt.Sector3Millis = src.Sector3Millis, tgt.IsPersonalBest = src.IsPersonalBest, tgt.TrackStatus = src.TrackStatus
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceKey, DriverKey, LapNumber, LapTimeMillis, Position, Compound, Stint,
                    Sector1Millis, Sector2Millis, Sector3Millis, IsPersonalBest, TrackStatus)
            VALUES (src.RaceKey, src.DriverKey, src.LapNumber, src.LapTimeMillis, src.Position, src.Compound, src.Stint,
                    src.Sector1Millis, src.Sector2Millis, src.Sector3Millis, src.IsPersonalBest, src.TrackStatus);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.FactLapTimes', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.FactLapTimes', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_FactPitStops
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.FactPitStops AS tgt
        USING (
            SELECT ra.RaceKey, dr.DriverKey, p.StopNumber, p.LapNumber, p.DurationMillis, p.TimeOfDay
            FROM stg.PitStop p
            INNER JOIN dw.DimRace ra ON ra.RaceId = p.RaceId
            INNER JOIN dw.DimDriver dr ON dr.DriverId = p.DriverId
        ) AS src
            ON tgt.RaceKey = src.RaceKey AND tgt.DriverKey = src.DriverKey AND tgt.StopNumber = src.StopNumber
        WHEN MATCHED THEN
            UPDATE SET tgt.LapNumber = src.LapNumber, tgt.DurationMillis = src.DurationMillis, tgt.TimeOfDay = src.TimeOfDay
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceKey, DriverKey, StopNumber, LapNumber, DurationMillis, TimeOfDay)
            VALUES (src.RaceKey, src.DriverKey, src.StopNumber, src.LapNumber, src.DurationMillis, src.TimeOfDay);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.FactPitStops', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.FactPitStops', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_Load_FactWeather
    @BatchId UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    DECLARE @Rows INT = 0;

    BEGIN TRY
        MERGE dw.FactWeather AS tgt
        USING (
            SELECT ra.RaceKey, w.SampleTime, w.AirTemp, w.TrackTemp, w.Humidity, w.Pressure,
                   w.WindSpeed, w.WindDirection, w.Rainfall
            FROM stg.Weather w
            INNER JOIN dw.DimRace ra ON ra.RaceId = w.RaceId
        ) AS src
            ON tgt.RaceKey = src.RaceKey AND tgt.SampleTime = src.SampleTime
        WHEN MATCHED THEN
            UPDATE SET tgt.AirTemp = src.AirTemp, tgt.TrackTemp = src.TrackTemp, tgt.Humidity = src.Humidity,
                       tgt.Pressure = src.Pressure, tgt.WindSpeed = src.WindSpeed,
                       tgt.WindDirection = src.WindDirection, tgt.Rainfall = src.Rainfall
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (RaceKey, SampleTime, AirTemp, TrackTemp, Humidity, Pressure, WindSpeed, WindDirection, Rainfall)
            VALUES (src.RaceKey, src.SampleTime, src.AirTemp, src.TrackTemp, src.Humidity, src.Pressure,
                    src.WindSpeed, src.WindDirection, src.Rainfall);

        SET @Rows = @@ROWCOUNT;
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status)
        VALUES (@BatchId, 'dw.FactWeather', @StartTime, SYSDATETIME(), @Rows, 'SUCCESS');
    END TRY
    BEGIN CATCH
        INSERT INTO etl.LoadLog (BatchId, TableName, StartTime, EndTime, RowsAffected, Status, ErrorMessage)
        VALUES (@BatchId, 'dw.FactWeather', @StartTime, SYSDATETIME(), 0, 'FAILED', ERROR_MESSAGE());
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE dw.usp_RunETL_LoadAll
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @BatchId UNIQUEIDENTIFIER = NEWID();

    EXEC dw.usp_Load_DimStatus @BatchId;
    EXEC dw.usp_Load_DimDriver @BatchId;
    EXEC dw.usp_Load_DimConstructor @BatchId;
    EXEC dw.usp_Load_DimCircuit @BatchId;
    EXEC dw.usp_Load_DimRace @BatchId;
    EXEC dw.usp_Load_FactResults @BatchId;
    EXEC dw.usp_Load_FactQualifying @BatchId;
    EXEC dw.usp_Load_FactLapTimes @BatchId;
    EXEC dw.usp_Load_FactPitStops @BatchId;
    EXEC dw.usp_Load_FactWeather @BatchId;

    SELECT @BatchId AS BatchId;

    DECLARE @FailedCount INT;
    SELECT @FailedCount = COUNT(*) FROM etl.LoadLog WHERE BatchId = @BatchId AND Status = 'FAILED';
    IF @FailedCount > 0
    BEGIN
        DECLARE @ErrorMsg NVARCHAR(4000) = CONCAT(@FailedCount, ' table(s) failed to load in batch ', @BatchId, '. Check etl.LoadLog for details.');
        RAISERROR(@ErrorMsg, 16, 1);
    END
END
GO
