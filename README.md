# GPX Route Generator

Create GPX files for a set of destinations defined in KML file.

## Configure

`profiles/foot.lua` is optimised to select ways with 'Park Connector' in them and prefer designated foot paths. Adjust as required.

Update `docker-compose.yaml` with the location and name of your PBF file:

```
services:
  osrm:
    volumes:
      - ~/Documents/osm:/data
    ...
    command: >
      bash -c "
      osrm-extract -p /profiles/foot.lua /data/singapore.osm.pbf && 
      osrm-partition /data/singapore.osrm && 
      osrm-customize /data/singapore.osrm && 
      osrm-routed --algorithm mld /data/singapore.osrm
      "
```

## Launch

```
docker-compose up
```
