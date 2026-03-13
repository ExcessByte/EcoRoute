import math
from itertools import permutations

import requests


class RoadAwareOptimizer:
    def __init__(self):
        self.depot = {"lat": 10.374640, "lon": 76.307205}
        self.osrm_base_url = "http://router.project-osrm.org/route/v1/driving/"

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1['lat'] - p2['lat'])**2 + (p1['lon'] - p2['lon'])**2)

    def get_total_path_distance(self, sequence):
        """Calculates total air-distance for a specific sequence"""
        dist = 0
        for i in range(len(sequence) - 1):
            dist += self.calculate_distance(sequence[i], sequence[i+1])
        return dist

    def get_road_path(self, coords):
        coord_string = ";".join([f"{c['lon']},{c['lat']}" for c in coords])
        url = f"{self.osrm_base_url}{coord_string}?overview=full&geometries=geojson"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('code') == 'Ok':
                raw_coords = data['routes'][0]['geometry']['coordinates']
                path = [[c[1], c[0]] for c in raw_coords]
                distance = data['routes'][0]['distance'] / 1000
                return path, distance
        except Exception as e:
            print(f"Routing error: {e}")
            return [[c['lat'], c['lon']] for c in coords], 0

    def optimize(self, bins):
        targets = [b for b in bins if b['current_fill'] > 45]
        if not targets: return []

        best_sequence = None
        min_dist = float('inf')

        for p in permutations(targets):
            current_sequence = [self.depot] + list(p) + [self.depot]
            d = self.get_total_path_distance(current_sequence)
            if d < min_dist:
                min_dist = d
                best_sequence = list(p)

        final_coords = [self.depot] + best_sequence + [self.depot]
        path_coords, road_dist = self.get_road_path(final_coords)

        return [{
            'route_id': "KOD-OPTIMAL-TOTAL",
            'path_coordinates': path_coords,
            'distance_km': round(road_dist, 2),
            'bins_collected': len(best_sequence),
            'bins': best_sequence
        }]
