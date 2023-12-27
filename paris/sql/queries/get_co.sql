--recupère les coordonnées d'un arret {name} avec l'identifiant sa ligne {n}
WITH tab1(stop_I, lat, lng) AS (
    SELECT stop_I, lat, lng
    FROM nodes
    WHERE name={name})

SELECT DISTINCT B.lat, B.lng
FROM steps_bus AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I)
WHERE A.route_I={n};