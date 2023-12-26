SELECT from_stop_i, to_stop_i, route_i, route_name, route_index 
FROM tram 
	 INNER JOIN 
	 steps_tram
	 	USING(from_stop_i, to_stop_i)
	 INNER JOIN route
	 	USING(route_i)
	 
WHERE from_stop_i = 18806
      AND to_stop_i = 18808

ORDER BY route_index
;
