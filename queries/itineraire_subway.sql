SELECT from_stop_i, to_stop_i, route_i, route_name, route_index 
FROM subway	 
	 INNER JOIN 
	 steps_subway
	 	USING(from_stop_i, to_stop_i)
	 INNER JOIN route
	 	USING(route_i)
	 
WHERE from_stop_i = 84
      AND to_stop_i = 61

ORDER BY route_index
;
