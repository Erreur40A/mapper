--plus proche station par rapport a {lng} et {lat} en fonction du mode de transport chosit {pt}

SELECT DISTINCT name, (SQRT(POW(({lng}-nodes.lng), 2) + POW(({lat}-nodes.lat), 2))) AS dist 
FROM nodes, {pt}
WHERE nodes.stop_I={pt}.from_stop_I OR nodes.stop_I={pt}.to_stop_I
ORDER BY dist ASC;