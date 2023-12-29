--on recupère le route_I en commun de {from} et {to} (l'id d'un route_i_counts)
--si id_itineraire est null alors il n'y a pas de ligne de bus qui relie from_stop_I vers to_stop_I
--sinon il y a une ligne qui les relie
--{pt}=mode de transport utiliser
--{ville}=ville qu'on a choisit 
WITH ligne (route_I) AS (
    (SELECT route_I FROM steps_{pt}_{ville} AS A, nodes_{ville} AS B WHERE A.from_stop_I=B.stop_I AND B.name={from})
    INTERSECT
    (SELECT route_I FROM steps_{pt}_{ville} AS A, nodes_{ville} AS B WHERE A.to_stop_I=B.stop_I AND B.name={to}))

SELECT DISTINCT B.name, F.route_name, D.name
    FROM steps_{pt}_{ville} AS A, nodes_{ville} AS B, steps_{pt}_{ville} AS C, nodes_{ville} AS D, ligne AS E, route_{ville} AS F
    WHERE B.name={from} AND D.name={to} AND A.route_I=E.route_I AND C.route_I=E.route_I
        AND A.from_stop_I=B.stop_I AND C.to_stop_I=D.stop_I AND E.route_I=F.route_I;