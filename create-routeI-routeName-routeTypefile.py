import geojson

with open("paris/routes.geojson") as f:
    gj = geojson.load(f)

print("route_I;route_name;route_type")
for line in gj['features']:
    print(f"{line['properties']['route_I']};{line['properties']['route_name']};{line['properties']['route_type']}")

