import numpy as np
import pydeck as pdk
import streamlit as st

def render_map(routes_data, map_center, map_zoom):
    """Render the map with the provided routes data and specified view state."""
    if routes_data:
        route_paths = []
        markers = []

        # Collect route paths and markers from the routes_data
        for route in routes_data:
            path = [[lon, lat] for lat, lon in route['coordinates']]
            route_paths.append({"path": path})

            # Add markers for start and endpoints
            start_point = route['coordinates'][0]
            end_point = route['coordinates'][-1]
            markers.append({
                "start": [start_point[1], start_point[0]],  # [lon, lat]
                "end": [end_point[1], end_point[0]]  # [lon, lat]
            })

        all_coords = np.array([coord for route in routes_data for coord in route['coordinates']])
        min_lat, min_lon = np.min(all_coords, axis=0)
        max_lat, max_lon = np.max(all_coords, axis=0)

        # Calculate the view state based on the route coordinates
        view_state = pdk.ViewState(
            latitude=(min_lat + max_lat) / 2,
            longitude=(min_lon + max_lon) / 2,
            zoom=map_zoom,  # Use the zoom level passed in
            pitch=0
        )

        # Create the Pydeck deck
        deck = pdk.Deck(
            layers=[
                pdk.Layer(
                    'PathLayer',
                    data=route_paths,
                    get_path='path',
                    get_color='[0, 0, 255, 255]',  # Blue color for routes
                    width_min_pixels=2,
                    width_max_pixels=10,
                    width_scale=3,
                    pickable=True
                ),
                # Markers for start and endpoints
                pdk.Layer(
                    'ScatterplotLayer',
                    data=markers,
                    get_position='start',  # For start points
                    get_color='[255, 0, 0]',  # Red color for start points
                    get_radius=100,
                    pickable=True
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=markers,
                    get_position='end',  # For end points
                    get_color='[0, 255, 0]',  # Green color for end points
                    get_radius=100,
                    pickable=True
                )
            ],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/outdoors-v11"
        )

        # Render the map with routes and markers
        st.pydeck_chart(deck)
    else:
        # Default view state when no routes are available
        default_view_state = pdk.ViewState(
            latitude=map_center[0],  # Use the map center passed in
            longitude=map_center[1],
            zoom=map_zoom,  # Use the zoom level passed in
            pitch=0
        )

        # Create a default Pydeck deck
        default_deck = pdk.Deck(
            initial_view_state=default_view_state,
            map_style="mapbox://styles/mapbox/outdoors-v11"
        )

        # Render the map with default view
        st.pydeck_chart(default_deck)
