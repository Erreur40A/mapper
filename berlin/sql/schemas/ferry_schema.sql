CREATE TABLE ferry_berlin(
    from_stop_I INTEGER,
    to_stop_I INTEGER,
    d INTEGER,
    duration_avg NUMERIC(20,5),
    n_vehicles INTEGER,
    route_I_counts TEXT,
    PRIMARY KEY (from_stop_I, to_stop_I)
);
