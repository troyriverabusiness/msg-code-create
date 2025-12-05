-- Schema for Travel Assistant SQLite DB

-- Stations (from stops.txt)
CREATE TABLE IF NOT EXISTS stations (
    stop_id TEXT PRIMARY KEY,
    stop_name TEXT,
    stop_lat REAL,
    stop_lon REAL,
    wheelchair_boarding INTEGER, -- 0=Unknown, 1=Yes, 2=No
    parent_station TEXT
);

-- Routes (from routes.txt)
CREATE TABLE IF NOT EXISTS routes (
    route_id TEXT PRIMARY KEY,
    route_short_name TEXT, -- e.g. "RB82"
    route_long_name TEXT,
    route_type INTEGER -- 100=Rail, 101=High Speed, etc.
);

-- Trips (from trips.txt)
CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    route_id TEXT,
    service_id TEXT,
    trip_headsign TEXT,
    trip_short_name TEXT, -- Train Number (e.g. "25169")
    direction_id INTEGER,
    FOREIGN KEY(route_id) REFERENCES routes(route_id)
);

-- Stop Times (from stop_times.txt)
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id TEXT,
    stop_id TEXT,
    stop_sequence INTEGER,
    arrival_time TEXT, -- HH:MM:SS
    departure_time TEXT, -- HH:MM:SS
    stop_headsign TEXT,
    pickup_type INTEGER,
    drop_off_type INTEGER,
    FOREIGN KEY(trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY(stop_id) REFERENCES stations(stop_id)
);

-- Transfers (from transfers.txt)
CREATE TABLE IF NOT EXISTS transfers (
    from_stop_id TEXT,
    to_stop_id TEXT,
    transfer_type INTEGER, -- 0=Rec, 1=Timed, 2=Min Time, 3=No Transfer
    min_transfer_time INTEGER, -- Seconds
    FOREIGN KEY(from_stop_id) REFERENCES stations(stop_id),
    FOREIGN KEY(to_stop_id) REFERENCES stations(stop_id)
);

-- Pathways (from pathways.txt)
-- Detailed navigation graph within stations
CREATE TABLE IF NOT EXISTS pathways (
    pathway_id TEXT PRIMARY KEY,
    from_stop_id TEXT,
    to_stop_id TEXT,
    pathway_mode INTEGER, -- 1=Walk, 2=Stairs, 4=Escalator, 5=Elevator
    is_bidirectional INTEGER,
    traversal_time INTEGER, -- Seconds
    FOREIGN KEY(from_stop_id) REFERENCES stations(stop_id),
    FOREIGN KEY(to_stop_id) REFERENCES stations(stop_id)
);

-- Platforms (Enriched from NeTEx)
CREATE TABLE IF NOT EXISTS platforms (
    global_id TEXT PRIMARY KEY, -- Matches stop_id (DHID)
    name TEXT, -- "Gleis 4"
    height REAL,
    length REAL,
    parent_station_id TEXT,
    FOREIGN KEY(parent_station_id) REFERENCES stations(stop_id)
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times(trip_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times(stop_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_time ON stop_times(departure_time);
CREATE INDEX IF NOT EXISTS idx_trips_route_id ON trips(route_id);
CREATE INDEX IF NOT EXISTS idx_stations_name ON stations(stop_name);
