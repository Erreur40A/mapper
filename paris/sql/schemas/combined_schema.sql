CREATE TABLE combined(
    from_stop_I INTEGER,
    to_stop_I INTEGER,
    d INTEGER,
    duartion_avg NUMERIC(20,5),
    n_vehicles INTEGER,
    route_I_counts TEXT,
    route_type INTEGER,
    PRIMARY KEY (from_stop_I, to_stop_I, route_type)
);
