CREATE TABLE temporal_week_paris(
    from_stop_I INTEGER,
    to_stop_I INTEGER,
    dep_time_ut NUMERIC(20,5),
    arr_time_ut NUMERIC(20,5),
    route_type INTEGER,
    trip_I INTEGER,
    seq INTEGER,
    route_I INTEGER,
    PRIMARY KEY (from_stop_I, to_stop_I, dep_time_ut, arr_time_ut, trip_I)
);
