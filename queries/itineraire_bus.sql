SELECT from_stop_i, to_stop_i, route_i, route_name, route_index 
FROM bus 
	 INNER JOIN 
	 steps_bus
	 	USING(from_stop_i, to_stop_i)
	 INNER JOIN route
	 	USING(route_i)
	 
WHERE from_stop_i = 16558
      AND to_stop_i = 14956

ORDER BY route_index
;
