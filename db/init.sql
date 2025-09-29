/* 
Initialization script to create the base table needed for the dashboard.
*/

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS public.gmc_readings (
  "datetime"            TIMESTAMP NOT NULL,
  "count"               INTEGER   NOT NULL,
  "unit"                TEXT,
  "mode"                TEXT,
  "reference_datetime"  TIMESTAMP,
  "notes"               TEXT
);

-- Helpful index for time range queries:
CREATE INDEX IF NOT EXISTS idx_gmc_readings_datetime ON public.gmc_readings ("datetime");

CREATE INDEX IF NOT EXISTS idx_gmc_readings_notes     ON public.gmc_readings ("notes");
