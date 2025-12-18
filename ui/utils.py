import requests
import polyline
import os

import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import contextily as ctx

import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring


def get_host():
    is_in_docker = os.path.exists("/.dockerenv")
    return "osrm:5000" if is_in_docker else "localhost:6000"


def get_points(
    start_lat,
    start_lng,
    stop_lat,
    stop_lng,
):
    points = [(start_lat, start_lng)] + [(stop_lat, stop_lng)]
    return points


def osrm_format(coords):
    lat, lon = coords
    return f"{lon},{lat}"


def get_route(points):
    host = get_host()
    points = ";".join(map(osrm_format, points))
    params = {
        "geometries": "polyline6",
    }

    response = requests.get(f"http://{host}/route/v1/foot/{points}", params=params)
    routes = response.json()

    if routes["code"] != "Ok":
        return None

    geometry = routes["routes"][0]["geometry"]
    return polyline.decode(geometry, 6)


def plot_gpx(route, ax):
    latitudes = [point[0] for point in route]
    longitudes = [point[1] for point in route]
    ax.plot(longitudes, latitudes, color="red", label="Route")
    ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)
    ax.legend()
    ax.set_yticks([])
    ax.set_xticks([])
    ax.tick_params(
        axis="both", which="both", bottom=False, top=False, left=False, right=False
    )


def create_gpx(route):
    gpx = Element(
        "gpx",
        {
            "creator": "StravaGPX",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd",
            "version": "1.1",
            "xmlns": "http://www.topografix.com/GPX/1/1",
        },
    )
    trk = SubElement(gpx, "trk")
    trkseg = SubElement(trk, "trkseg")

    for point in route:
        SubElement(trkseg, "trkpt", attrib={"lat": str(point[0]), "lon": str(point[1])})

    gpx_file = xml.dom.minidom.parseString(
        tostring(gpx, encoding="unicode")
    ).toprettyxml()

    return gpx_file


def get_kml_destinations(file_path):
    destinations = []

    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = root.findall(".//kml:Placemark", ns)

    for placemark in placemarks:
        name = placemark.find("kml:name", ns)
        if name is None:
            continue

        coords = placemark.find(".//kml:coordinates", ns)
        if coords is None:
            continue

        points = coords.text.strip().split()
        for point in points:
            coordinates = point.split(",")

            latitude = float(coordinates[1])
            longitude = float(coordinates[0])

            destinations.append([name.text, latitude, longitude])

    return destinations


def create_routes(
    start_lat,
    start_lng,
    destinations,
):
    routes = []

    for destination in destinations:
        name, stop_lat, stop_lng = destination

        points = get_points(
            start_lat,
            start_lng,
            stop_lat,
            stop_lng,
        )

        osrm_route = get_route(points)

        gpx = create_gpx(osrm_route)

        fig, ax = plt.subplots(1, 1, figsize=(12, 30))
        plot_gpx(osrm_route, ax)

        routes.append((name, fig, gpx))

    return routes
