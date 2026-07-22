USE Formula1DW;
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Driver')
CREATE TABLE stg.Driver (
    DriverId VARCHAR(50) NOT NULL PRIMARY KEY,
    DriverRef VARCHAR(100) NULL,
    Code VARCHAR(10) NULL,
    PermanentNumber INT NULL,
    Forename VARCHAR(100) NULL,
    Surname VARCHAR(100) NULL,
    Nationality VARCHAR(100) NULL,
    DateOfBirth DATE NULL,
    Url VARCHAR(500) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Constructor')
CREATE TABLE stg.Constructor (
    ConstructorId VARCHAR(50) NOT NULL PRIMARY KEY,
    ConstructorRef VARCHAR(100) NULL,
    Name VARCHAR(100) NULL,
    Nationality VARCHAR(100) NULL,
    Url VARCHAR(500) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Circuit')
CREATE TABLE stg.Circuit (
    CircuitId VARCHAR(50) NOT NULL PRIMARY KEY,
    CircuitRef VARCHAR(100) NULL,
    Name VARCHAR(200) NULL,
    Location VARCHAR(100) NULL,
    Country VARCHAR(100) NULL,
    Lat DECIMAL(9,6) NULL,
    Lng DECIMAL(9,6) NULL,
    Alt INT NULL,
    Url VARCHAR(500) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Race')
CREATE TABLE stg.Race (
    RaceId VARCHAR(50) NOT NULL PRIMARY KEY,
    Season SMALLINT NOT NULL,
    Round TINYINT NOT NULL,
    Name VARCHAR(200) NULL,
    CircuitId VARCHAR(50) NOT NULL,
    RaceDate DATE NOT NULL,
    RaceTime TIME NULL,
    Url VARCHAR(500) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Status')
CREATE TABLE stg.Status (
    StatusId INT NOT NULL PRIMARY KEY,
    StatusDescription VARCHAR(100) NULL
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Result')
CREATE TABLE stg.Result (
    RaceId VARCHAR(50) NOT NULL,
    DriverId VARCHAR(50) NOT NULL,
    ConstructorId VARCHAR(50) NOT NULL,
    StatusId INT NOT NULL,
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
    PRIMARY KEY (RaceId, DriverId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'SprintResult')
CREATE TABLE stg.SprintResult (
    RaceId VARCHAR(50) NOT NULL,
    DriverId VARCHAR(50) NOT NULL,
    ConstructorId VARCHAR(50) NOT NULL,
    StatusId INT NOT NULL,
    GridPosition INT NULL,
    FinishPosition INT NULL,
    PositionOrder INT NULL,
    Points DECIMAL(6,2) NULL,
    Laps INT NULL,
    PRIMARY KEY (RaceId, DriverId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Qualifying')
CREATE TABLE stg.Qualifying (
    RaceId VARCHAR(50) NOT NULL,
    DriverId VARCHAR(50) NOT NULL,
    ConstructorId VARCHAR(50) NOT NULL,
    Position INT NULL,
    Q1Millis BIGINT NULL,
    Q2Millis BIGINT NULL,
    Q3Millis BIGINT NULL,
    PRIMARY KEY (RaceId, DriverId)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'LapTime')
CREATE TABLE stg.LapTime (
    RaceId VARCHAR(50) NOT NULL,
    DriverId VARCHAR(50) NOT NULL,
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
    PRIMARY KEY (RaceId, DriverId, LapNumber)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'PitStop')
CREATE TABLE stg.PitStop (
    RaceId VARCHAR(50) NOT NULL,
    DriverId VARCHAR(50) NOT NULL,
    StopNumber INT NOT NULL,
    LapNumber INT NULL,
    DurationMillis INT NULL,
    TimeOfDay TIME NULL,
    PRIMARY KEY (RaceId, DriverId, StopNumber)
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('stg') AND name = 'Weather')
CREATE TABLE stg.Weather (
    RaceId VARCHAR(50) NOT NULL,
    SampleTime DATETIME2 NOT NULL,
    AirTemp DECIMAL(5,2) NULL,
    TrackTemp DECIMAL(5,2) NULL,
    Humidity DECIMAL(5,2) NULL,
    Pressure DECIMAL(7,2) NULL,
    WindSpeed DECIMAL(5,2) NULL,
    WindDirection INT NULL,
    Rainfall BIT NULL,
    PRIMARY KEY (RaceId, SampleTime)
);
GO
