--plus proche station par rapport a {lng} et {lat}

SELECT name, (sqrt(pow(({lng}-nodes.lng), 2) + pow(({lat}-nodes.lat), 2))) AS dist 
FROM nodes 
ORDER BY dist ASC;