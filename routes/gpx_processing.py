import gpxpy
from .file_operations import load_routes, save_routes
from .map_rendering import render_map
from haversine import haversine

def process_gpx_files(uploaded_files, routes_data):
    """Process uploaded GPX files and update routes data."""
    success_routes = []
    failed_routes = []

    for file in uploaded_files:
        if file.name.endswith('.gpx'):
            try:
                gpx = gpxpy.parse(file.read())
                coordinates, points = [], []

                # Process GPX data
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            coordinates.append([point.latitude, point.longitude])
                            points.append(point)

                route_name = file.name[:-4]
                distance, elevation = calculate_distance_and_elevation(points)

                # Check for duplicate routes
                if not any(route['name'] == route_name for route in routes_data):
                    routes_data.append({
                        'id': len(routes_data) + 1,
                        'name': route_name,
                        'coordinates': coordinates,
                        'distance': distance,
                        'elevation': elevation
                    })
                    success_routes.append(route_name)
                else:
                    failed_routes.append(f"{route_name} (duplicate route)")
            except gpxpy.gpx.GPXException as e:
                failed_routes.append(f"{file.name} (error: {str(e)})")

    return success_routes, failed_routes

# Calculate distance and elevation gain from GPX data
def calculate_distance_and_elevation(points):
    distance = 0
    elevation_gain = 0
    prev_point = None

    for point in points:
        if prev_point:
            # Calculate the distance in meters using tuples
            d = haversine((prev_point.latitude, prev_point.longitude), (point.latitude, point.longitude))
            distance += d

            # Calculate elevation gain
            elevation_change = point.elevation - prev_point.elevation
            if elevation_change > 0:
                elevation_gain += elevation_change

        prev_point = point

    return distance, elevation_gain

