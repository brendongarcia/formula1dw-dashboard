USE Formula1DW;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'CCI_FactResults' AND object_id = OBJECT_ID('dw.FactResults'))
CREATE NONCLUSTERED COLUMNSTORE INDEX CCI_FactResults
ON dw.FactResults (RaceKey, DriverKey, ConstructorKey, StatusKey, Points, GridPosition, FinishPosition, Laps);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'CCI_FactLapTimes' AND object_id = OBJECT_ID('dw.FactLapTimes'))
CREATE NONCLUSTERED COLUMNSTORE INDEX CCI_FactLapTimes
ON dw.FactLapTimes (RaceKey, DriverKey, LapNumber, LapTimeMillis, Position, Sector1Millis, Sector2Millis, Sector3Millis);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FactTelemetry_Race_Driver_Lap' AND object_id = OBJECT_ID('dw.FactTelemetry'))
CREATE NONCLUSTERED INDEX IX_FactTelemetry_Race_Driver_Lap ON dw.FactTelemetry (RaceKey, DriverKey, LapNumber);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FactTrackSegment_Race_Sector' AND object_id = OBJECT_ID('dw.FactTrackSegment'))
CREATE NONCLUSTERED INDEX IX_FactTrackSegment_Race_Sector ON dw.FactTrackSegment (RaceKey, SectorNumber);
GO
