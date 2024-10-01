import json
import os

# File to store route data
ROUTES_FILE = 'routes.json'

def load_routes():
    """Load routes from a JSON file."""
    if not os.path.exists(ROUTES_FILE):
        return []  # Return an empty list if the file doesn't exist

    with open(ROUTES_FILE, 'r') as f:
        return json.load(f)

def save_routes(routes):
    """Save routes to a JSON file."""
    with open(ROUTES_FILE, 'w') as f:
        json.dump(routes, f)