--plus proche station par rapport a {lng} et {lat} 
--en fonction du mode de transport chosit {pt}
--et de la ville choisit

SELECT DISTINCT name, (SQRT(POW(({lng}-A.lng), 2) + POW(({lat}-A.lat), 2))) AS dist 
FROM nodes_{ville} AS A, steps_{pt}_{ville} AS B
WHERE A.stop_I=B.from_stop_I OR A.stop_I=B.to_stop_I
ORDER BY dist ASC;