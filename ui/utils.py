import requests
import polyline
import math
import random

from geopy.distance import distance
from geopy.point import Point
from geopy.distance import geodesic

import matplotlib.pyplot as plt
import contextily as ctx

import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from rdp import rdp

NUMBER_OF_PLOTS = 20

def get_center_point(lat, lng, distance_km):    
    bearing = random.uniform(0, 360)
    original_point = Point(lat, lng)
    
    point = distance(kilometers=distance_km).destination(original_point, bearing)
    return (point.latitude, point.longitude)
  
def get_points_on_circle(lat, lng, randomness_amount, distance_km):
    points = []

    (lat, lon) = get_center_point(lat, lng, distance_km)
    center_point = Point(lat, lon)
    
    if randomness_amount == 0:
        return points
        
    angle_interval = 360 / randomness_amount
    
    for i in range(num_points):
        angle = angle_interval * i
        point = distance(kilometers=distance_km).destination(point=center_point, bearing=angle)
        points.append((point.latitude, point.longitude))

    return points

def get_points(
    start_lat, 
    start_lng, 
    stop_lat,
    stop_lng,
    randomness_amount,
    distance_km,   
):
    points = get_points_on_circle(start_lat, start_lng, randomness_amount, distance_km)
    points = [(start_lat, start_lng)] + points + [(stop_lat, stop_lng)]
    return points 

def osrm_format(coords):
    lat, lon = coords
    return f"{lon},{lat}"
  
def get_route(points):
    points = ';'.join(map(osrm_format, points))
    params = {
        'geometries': 'polyline6',
    }
    
    response = requests.get(f"http://127.0.0.1:6000/route/v1/foot/{points}", params=params)
    routes = response.json()
    
    if routes['code'] != 'Ok':
        return None
    
    geometry = routes['routes'][0]['geometry']
    return polyline.decode(geometry, 6)
 
def plot_gpx(route, ax):
    latitudes = [point[0] for point in route]
    longitudes = [point[1] for point in route]
    ax.plot(longitudes, latitudes, color='red', label='Route')
    ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)
    ax.legend()
    ax.set_yticks([])
    ax.set_xticks([])
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)

def get_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += geodesic(route[i], route[i + 1]).kilometers
    return round(total_distance, 2)

def create_gpx(route):
    gpx = Element('gpx', {
        'creator': 'StravaGPX',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
        'version': '1.1',
        'xmlns': 'http://www.topografix.com/GPX/1/1'
    })
    trk = SubElement(gpx, "trk")
    trkseg = SubElement(trk, "trkseg")

    for point in route:
        SubElement(trkseg, "trkpt", attrib={"lat": str(point[0]), "lon": str(point[1])})

    gpx_file = xml.dom.minidom.parseString(
        tostring(gpx, encoding="unicode")
    ).toprettyxml()
 
    return gpx_file
 
def create_routes(
    start_lat, 
    start_lng, 
    stop_lat,
    stop_lng,
    randomness_amount,
    distance_km,
):
    figs = []
    gpx_routes = []
    distances = []

    for i in range(NUMBER_OF_PLOTS):
        points = get_points(
            start_lat, 
            start_lng, 
            stop_lat,
            stop_lng,
            randomness_amount,
            distance_km,  
        )

        # Get route which connects the points
        osrm_route = get_route(points) 
        while osrm_route is None:
            points = get_points(
                start_lat, 
                start_lng, 
                stop_lat,
                stop_lng,
                randomness_amount,
                distance_km,  
            )
            osrm_route = get_route(points)                   

        # Make route more smooth
        rdp_points = rdp(osrm_route, epsilon=0.005)

        # Run OSRM on smooth route
        osrm_route = get_route(rdp_points)
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 30))
        plot_gpx(osrm_route, ax)
        figs.append(fig)
        
        gpx_routes.append(
            create_gpx(osrm_route)
        )
        
        distances.append(
            get_distance(osrm_route)
        )
    
    return figs, gpx_routes, distances