USE Formula1DW;
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactResults')
CREATE TABLE dw.FactResults (
    FactResultsKey INT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    ConstructorKey INT NOT NULL REFERENCES dw.DimConstructor(ConstructorKey),
    StatusKey INT NOT NULL REFERENCES dw.DimStatus(StatusKey),
    GridPosition INT NULL,
    FinishPosition INT NULL,
    PositionOrder INT NULL,
    Points DECIMAL(6,2) NULL,
    Laps INT NULL,
    TimeMillis BIGINT NULL,
    FastestLapNumber INT NULL,
    FastestLapTimeMillis BIGINT NULL,
    FastestLapSpeedKph DECIMAL(7,3) NULL,
    FastestLapRank INT NULL,
    CONSTRAINT UQ_FactResults_Race_Driver UNIQUE (RaceKey, DriverKey)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactQualifying')
CREATE TABLE dw.FactQualifying (
    FactQualifyingKey INT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    ConstructorKey INT NOT NULL REFERENCES dw.DimConstructor(ConstructorKey),
    Position INT NULL,
    Q1Millis BIGINT NULL,
    Q2Millis BIGINT NULL,
    Q3Millis BIGINT NULL,
    CONSTRAINT UQ_FactQualifying_Race_Driver UNIQUE (RaceKey, DriverKey)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactLapTimes')
CREATE TABLE dw.FactLapTimes (
    FactLapTimesKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    LapNumber INT NOT NULL,
    LapTimeMillis BIGINT NULL,
    Position INT NULL,
    Compound VARCHAR(20) NULL,
    Stint INT NULL,
    Sector1Millis BIGINT NULL,
    Sector2Millis BIGINT NULL,
    Sector3Millis BIGINT NULL,
    IsPersonalBest BIT NULL,
    TrackStatus VARCHAR(10) NULL,
    CONSTRAINT UQ_FactLapTimes_Race_Driver_Lap UNIQUE (RaceKey, DriverKey, LapNumber)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactPitStops')
CREATE TABLE dw.FactPitStops (
    FactPitStopsKey INT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    StopNumber INT NOT NULL,
    LapNumber INT NULL,
    DurationMillis INT NULL,
    TimeOfDay TIME NULL,
    CONSTRAINT UQ_FactPitStops_Race_Driver_Stop UNIQUE (RaceKey, DriverKey, StopNumber)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactWeather')
CREATE TABLE dw.FactWeather (
    FactWeatherKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    SampleTime DATETIME2 NOT NULL,
    AirTemp DECIMAL(5,2) NULL,
    TrackTemp DECIMAL(5,2) NULL,
    Humidity DECIMAL(5,2) NULL,
    Pressure DECIMAL(7,2) NULL,
    WindSpeed DECIMAL(5,2) NULL,
    WindDirection INT NULL,
    Rainfall BIT NULL,
    CONSTRAINT UQ_FactWeather_Race_Sample UNIQUE (RaceKey, SampleTime)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactTelemetry')
CREATE TABLE dw.FactTelemetry (
    FactTelemetryKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    LapNumber INT NOT NULL,
    Distance DECIMAL(9,2) NOT NULL,
    SessionTime DECIMAL(12,3) NULL,
    Speed DECIMAL(6,2) NULL,
    RPM INT NULL,
    Gear TINYINT NULL,
    Throttle DECIMAL(5,2) NULL,
    Brake BIT NULL,
    DRS INT NULL,
    X DECIMAL(9,2) NULL,
    Y DECIMAL(9,2) NULL,
    Z DECIMAL(9,2) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('dw') AND name = 'FactTrackSegment')
CREATE TABLE dw.FactTrackSegment (
    FactTrackSegmentKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    RaceKey INT NOT NULL REFERENCES dw.DimRace(RaceKey),
    DriverKey INT NOT NULL REFERENCES dw.DimDriver(DriverKey),
    LapNumber INT NOT NULL,
    Distance DECIMAL(9,2) NOT NULL,
    X DECIMAL(9,2) NULL,
    Y DECIMAL(9,2) NULL,
    SectorNumber TINYINT NOT NULL
);
GO
