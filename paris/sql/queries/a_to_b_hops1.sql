--on recupère le route_I en commun de {from} et {to} (l'id d'un route_i_counts)
--si id_itineraire est null alors il n'y a pas de ligne de bus qui relie from_stop_I vers to_stop_I
--sinon il y a une ligne qui les relie 
WITH ligne (route_I) AS (
    (SELECT route_I FROM steps_bus, nodes WHERE steps_bus.from_stop_I=nodes.stop_I AND nodes.name={from})
    INTERSECT
    (SELECT route_I FROM steps_bus, nodes WHERE steps_bus.to_stop_I=nodes.stop_I AND nodes.name={to}))

SELECT DISTINCT B.name, F.route_name, D.name
    FROM steps_bus AS A, nodes AS B, steps_bus AS C, nodes AS D, ligne AS E, route AS F
    WHERE B.name={from} AND D.name={to} AND A.route_I=E.route_I AND C.route_I=E.route_I
        AND A.from_stop_I=B.stop_I AND C.to_stop_I=D.stop_I AND E.route_I=F.route_I;