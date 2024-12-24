import os
import folium
from folium.plugins import HeatMap
from typing import Optional

from .nextbike import Country, Organization, City


def bikemap(obj: Country | Organization | City, folder: Optional[str] = None, filename: Optional[str] = None):
    if folder is None:
        folder = "bikemaps"
        os.makedirs(folder, exist_ok=True)
    if filename is None:
        filename = "bikemap.html"
    save_path = os.path.join(folder, filename)

    d_lat = max(obj.stations.values(), key=lambda x: x.lat).lat - min(obj.stations.values(), key=lambda x: x.lat).lat
    d_lng = max(obj.stations.values(), key=lambda x: x.lng).lng - min(obj.stations.values(), key=lambda x: x.lng).lng
    scale = max(d_lat, d_lng)

    zoom_start = 13 - int(scale)  # approximate scale
    map = folium.Map(location=[obj.lat, obj.lng], zoom_start=zoom_start)

    for s in obj.stations.values():
        if "bike" in s.name.lower():  # Single bikes (not stations)
            color = "blue"
        elif s.bikes_available_to_rent == 0:  # Normal station without bikes
            color = "red"
        else:  # Normal station with bikes
            color = "green"

        marker = folium.Marker(
            location=[s.lat, s.lng],
            icon=folium.Icon(icon="bicycle", prefix="fa", color=color),
            popup=f"{s.name}: {s.bikes_available_to_rent}"
        )
        marker.add_to(map)
    map.save(save_path)


def heatmap(obj: Country | Organization | City, radius: int = 20,
            folder: Optional[str] = None, filename: Optional[str] = None):
    if folder is None:
        folder = "heatmaps"
        os.makedirs(folder, exist_ok=True)
    if filename is None:
        filename = f"heatmap_{obj.name}.html"
    save_path = os.path.join(folder, filename)

    # Data and scale params
    data = [(s.lat, s.lng, s.bikes_available_to_rent) for s in obj.stations.values()]
    d_lat = max(data, key=lambda x: x[0])[0] - min(data, key=lambda x: x[0])[0]
    d_lng = max(data, key=lambda x: x[1])[0] - min(data, key=lambda x: x[1])[0]
    scale = max(d_lat, d_lng)

    zoom_start = 13 - int(scale)  # approximate scale
    map = folium.Map(location=[obj.lat, obj.lng], zoom_start=zoom_start)
    HeatMap(data, radius=radius).add_to(map)
    map.save(save_path)
