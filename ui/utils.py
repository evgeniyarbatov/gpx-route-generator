import requests
import polyline
import math
import random

from geopy.distance import distance
from geopy.point import Point

import matplotlib.pyplot as plt
import contextily as ctx

from rdp import rdp

NUMBER_OF_PLOTS = 10

def get_center_point(lat, lng, distance_km):    
    bearing = random.uniform(0, 360)
    original_point = Point(lat, lng)
    
    point = distance(kilometers=distance_km).destination(original_point, bearing)
    return (point.latitude, point.longitude)
  
def get_points_on_circle(lat, lng, distance_km):
    points = []

    (lat, lon) = get_center_point(lat, lng, distance_km)
    center_point = Point(lat, lon)
    
    num_points = random.randint(5, 10)
    angle_interval = 360 / num_points
    
    for i in range(num_points):
        angle = angle_interval * i
        point = distance(kilometers=distance_km).destination(point=center_point, bearing=angle)
        points.append((point.latitude, point.longitude))

    return points

def get_points(start_lat, start_lng, distance_km):
    points = get_points_on_circle(start_lat, start_lng, distance_km)
    points = [(start_lat, start_lng)] + points + [(start_lat, start_lng)]
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
 
def create_routes(start_lat, start_lng, distance_km):
    figs = []

    for i in range(NUMBER_OF_PLOTS):
        points = get_points(start_lat, start_lng, distance_km)

        # Get route which connects the points
        osrm_route = get_route(points) 
        while osrm_route is None:
            points = get_points(start_lat, start_lng, distance_km)
            osrm_route = get_route(points)                   

        # Make route more smooth
        rdp_points = rdp(osrm_route, epsilon=0.005)

        # Run OSRM on smooth route
        osrm_route = get_route(rdp_points)
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 30))
        plot_gpx(osrm_route, ax)
        figs.append(fig)
    
    return figs