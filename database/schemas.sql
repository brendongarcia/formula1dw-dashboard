USE Formula1DW;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'raw')
    EXEC('CREATE SCHEMA raw');
GO
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');
GO
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');
GO
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'mart')
    EXEC('CREATE SCHEMA mart');
GO
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'etl')
    EXEC('CREATE SCHEMA etl');
GO

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE schema_id = SCHEMA_ID('etl') AND name = 'LoadLog')
BEGIN
    CREATE TABLE etl.LoadLog (
        LoadLogKey INT IDENTITY(1,1) PRIMARY KEY,
        BatchId UNIQUEIDENTIFIER NOT NULL,
        TableName VARCHAR(128) NOT NULL,
        StartTime DATETIME2 NOT NULL,
        EndTime DATETIME2 NULL,
        RowsAffected INT NULL,
        Status VARCHAR(10) NOT NULL,
        ErrorMessage NVARCHAR(4000) NULL
    );
END
GO
