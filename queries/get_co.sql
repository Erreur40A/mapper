--recupère les coordonnées d'un arret {name} avec le nom de sa ligne {n} et le 
--mode de transport utiliser {pt}
--ville choisit {ville}
WITH tab1(stop_I, lat, lng) AS (
    SELECT stop_I, lat, lng
    FROM nodes_{ville}
    WHERE name={name}),
   
    tmp (route_I) AS
    (SELECT route_I
    FROM route_{ville}
    WHERE route_name={n})

SELECT DISTINCT B.lat, B.lng
FROM (steps_{pt}_{ville} AS A INNER JOIN tab1 AS B ON (A.from_stop_I=B.stop_I)) INNER JOIN tmp AS C ON (A.route_I=C.route_I);