--plus proche station par rapport a {lng} et {lat}

SELECT name, (SQRT(POW(({lng}-nodes.lng), 2) + POW(({lat}-nodes.lat), 2))) AS dist 
FROM nodes 
ORDER BY dist ASC;
