WITH tab1(stop_I, lat, lng) AS (
    SELECT stop_I, lat, lng
    FROM nodes_{ville}
    WHERE name={name})

SELECT DISTINCT B.lat, B.lng
FROM (walk_{ville} AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I))
