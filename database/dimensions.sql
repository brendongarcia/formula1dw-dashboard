USE Formula1DW;
GO

SET QUOTED_IDENTIFIER ON;
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimDate')
CREATE TABLE dw.DimDate (
    DateKey INT NOT NULL PRIMARY KEY,
    FullDate DATE NOT NULL,
    [Day] TINYINT NOT NULL,
    [Month] TINYINT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    Quarter TINYINT NOT NULL,
    [Year] SMALLINT NOT NULL,
    DayOfWeek TINYINT NOT NULL,
    DayName VARCHAR(20) NOT NULL,
    WeekOfYear TINYINT NOT NULL
);
GO

CREATE OR ALTER PROCEDURE dw.usp_Seed_DimDate
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (SELECT 1 FROM dw.DimDate)
        RETURN;

    DECLARE @StartDate DATE = '1950-01-01';
    DECLARE @EndDate DATE = '2030-12-31';

    ;WITH Tally AS (
        SELECT TOP (DATEDIFF(DAY, @StartDate, @EndDate) + 1)
            ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS n
        FROM sys.all_objects a CROSS JOIN sys.all_objects b
    ),
    Dates AS (
        SELECT DATEADD(DAY, n, @StartDate) AS FullDate FROM Tally
    )
    INSERT INTO dw.DimDate (DateKey, FullDate, [Day], [Month], MonthName, Quarter, [Year], DayOfWeek, DayName, WeekOfYear)
    SELECT
        CONVERT(INT, CONVERT(VARCHAR(8), FullDate, 112)),
        FullDate,
        DAY(FullDate),
        MONTH(FullDate),
        DATENAME(MONTH, FullDate),
        DATEPART(QUARTER, FullDate),
        YEAR(FullDate),
        DATEPART(WEEKDAY, FullDate),
        DATENAME(WEEKDAY, FullDate),
        DATEPART(ISO_WEEK, FullDate)
    FROM Dates;
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimStatus')
CREATE TABLE dw.DimStatus (
    StatusKey INT IDENTITY(1,1) PRIMARY KEY,
    StatusId INT NOT NULL,
    StatusDescription VARCHAR(100) NULL,
    CONSTRAINT UQ_DimStatus_StatusId UNIQUE (StatusId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimDriver')
CREATE TABLE dw.DimDriver (
    DriverKey INT IDENTITY(1,1) PRIMARY KEY,
    DriverId VARCHAR(50) NOT NULL,
    DriverRef VARCHAR(100) NULL,
    Code VARCHAR(10) NULL,
    PermanentNumber INT NULL,
    Forename VARCHAR(100) NULL,
    Surname VARCHAR(100) NULL,
    FullName AS (CONCAT(Forename, ' ', Surname)) PERSISTED,
    Nationality VARCHAR(100) NULL,
    DateOfBirth DATE NULL,
    Url VARCHAR(500) NULL,
    CONSTRAINT UQ_DimDriver_DriverId UNIQUE (DriverId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimConstructor')
CREATE TABLE dw.DimConstructor (
    ConstructorKey INT IDENTITY(1,1) PRIMARY KEY,
    ConstructorId VARCHAR(50) NOT NULL,
    ConstructorRef VARCHAR(100) NULL,
    Name VARCHAR(100) NULL,
    Nationality VARCHAR(100) NULL,
    Url VARCHAR(500) NULL,
    CONSTRAINT UQ_DimConstructor_ConstructorId UNIQUE (ConstructorId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimCircuit')
CREATE TABLE dw.DimCircuit (
    CircuitKey INT IDENTITY(1,1) PRIMARY KEY,
    CircuitId VARCHAR(50) NOT NULL,
    CircuitRef VARCHAR(100) NULL,
    Name VARCHAR(200) NULL,
    Location VARCHAR(100) NULL,
    Country VARCHAR(100) NULL,
    Lat DECIMAL(9,6) NULL,
    Lng DECIMAL(9,6) NULL,
    Alt INT NULL,
    Url VARCHAR(500) NULL,
    CONSTRAINT UQ_DimCircuit_CircuitId UNIQUE (CircuitId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'DimRace')
CREATE TABLE dw.DimRace (
    RaceKey INT IDENTITY(1,1) PRIMARY KEY,
    RaceId VARCHAR(50) NOT NULL,
    Season SMALLINT NOT NULL,
    Round TINYINT NOT NULL,
    Name VARCHAR(200) NULL,
    CircuitKey INT NOT NULL REFERENCES dw.DimCircuit(CircuitKey),
    DateKey INT NOT NULL REFERENCES dw.DimDate(DateKey),
    RaceTime TIME NULL,
    Url VARCHAR(500) NULL,
    CONSTRAINT UQ_DimRace_RaceId UNIQUE (RaceId)
);
GO
