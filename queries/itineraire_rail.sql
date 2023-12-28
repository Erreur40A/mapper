SELECT from_stop_i, to_stop_i, route_i, route_name, route_index 
FROM rail 
	 INNER JOIN 
	 steps_rail
	 	USING(from_stop_i, to_stop_i)
	 INNER JOIN route
	 	USING(route_i)
	 
WHERE from_stop_i = 43
      AND to_stop_i = 244

ORDER BY route_index
;
