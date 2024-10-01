import streamlit as st
import numpy as np
from routes.file_operations import load_routes, save_routes
from routes.gpx_processing import process_gpx_files
from routes.map_rendering import render_map

# Initialize routes data
routes_data = load_routes()

def main():
    # Set page configuration
    st.set_page_config(page_title="Hiking Route Tracker", layout="wide")
    st.title("Hiking Route Tracker")

    # Sidebar for file uploads and route display
    st.sidebar.header("Upload GPX Files")
    uploaded_files = st.sidebar.file_uploader("Choose GPX files", accept_multiple_files=True, type=["gpx"])

    # Placeholders for messages
    upload_message = st.sidebar.empty()
    delete_message = st.sidebar.empty()
    clear_message = st.sidebar.empty()

    # Initialize session states for map view if not already set
    if 'map_center' not in st.session_state:
        st.session_state.map_center = [39.8283, -98.5795]  # Default to center of the continental US
    if 'map_zoom' not in st.session_state:
        st.session_state.map_zoom = 4  # Default zoom level
    if 'show_routes' not in st.session_state:
        st.session_state.show_routes = False  # Initialize visibility state

    # Process uploaded files when files are selected
    if uploaded_files:
        success_routes, failed_routes = process_gpx_files(uploaded_files, routes_data)

        # Save routes to the JSON file after processing
        save_routes(routes_data)

        # Construct confirmation message
        if success_routes:
            upload_message.success(f"Successfully uploaded: {', '.join(success_routes)}.")
        if failed_routes:
            upload_message.warning(f"Failed to upload: {', '.join(failed_routes)}.")

    col1, col2, col3 = st.sidebar.columns([1, 1, 1])  # Create three columns for buttons

    # Uploaded Routes button
    if col1.button("Show/Hide Routes"):
        st.session_state.show_routes = not st.session_state.show_routes  # Toggle visibility

    # Clear All Routes button
    if col2.button("Clear All Routes"):
        if routes_data:  # Only show clear message if there are routes to clear
            routes_data.clear()
            save_routes(routes_data)
            clear_message.success("All routes have been cleared.")
            st.session_state.show_routes = False  # Hide the route list after clearing

            # Reset map view after clearing routes
            st.session_state.map_center = [39.8283, -98.5795]  # Reset to default
            st.session_state.map_zoom = 4  # Reset zoom level

    # Reset View button
    if col3.button("Reset View"):
        if routes_data:
            all_coords = np.array([coord for route in routes_data for coord in route['coordinates']])
            min_lat, min_lon = np.min(all_coords, axis=0)
            max_lat, max_lon = np.max(all_coords, axis=0)
            # Set map view to encompass all routes
            st.session_state.map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
            # Dynamic zoom based on the spread of the routes
            spread = max(max_lat - min_lat, max_lon - min_lon)
            st.session_state.map_zoom = 10 - int(spread * 0.2)  # Adjust as needed
        else:
            # Reset to default values if no routes
            st.session_state.map_center = [39.8283, -98.5795]  # Center of the continental US
            st.session_state.map_zoom = 4  # Default zoom level

    # Display routes if toggle state is True
    if st.session_state.show_routes:
        for route in routes_data:
            cols = st.sidebar.columns([1, 1])
            with cols[0]:
                st.sidebar.write(f"**Route Name:** {route['name']}")
                st.sidebar.write(f"- **Distance:** {route['distance']:.2f} meters")
                st.sidebar.write(f"- **Elevation Gain:** {route['elevation']:.2f} meters")
            with cols[1]:
                # Ensure the delete button has a unique key by using the route's name
                if st.sidebar.button(f"Delete {route['name']}", key=f"delete_{route['id']}_{route['name']}"):
                    # Remove the route immediately after the button is pressed
                    routes_data.remove(route)
                    save_routes(routes_data)  # Save the updated routes
                    delete_message.success(f"{route['name']} has been deleted.")

                    # Refresh the route display by updating the session state
                    st.session_state.show_routes = True  # Ensure routes are shown after deletion
                    break  # Exit loop to re-display routes after deletion

    # Always display the map
    render_map(routes_data, st.session_state.map_center, st.session_state.map_zoom)

if __name__ == "__main__":
    main()
