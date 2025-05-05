import streamlit as st
import folium
from streamlit_folium import st_folium

# TODO: This is a teaser sample
def school_map_view():
    locations = [
        {"name": "Primary school 1", "lat": 51.5007, "lon": -0.1246, "school": True, "info": "Primary school 1 in Fincheley, state, outstanding ⭐"},
        {"name": "Property 2", "lat": 51.5081, "lon": -0.0759, "school": False, "info": "£700000, 4 bedrooms"},
        {"name": "Primary school 2", "lat": 51.5971, "lon": -0.1981, "school": True, "info": "Primary school 2, independent"},
        {"name": "Primary school 3", "lat": 52.0020, "lon": -0.36, "school": True, "info": "Primary school 3, state, good"},
        {"name": "Property 2", "lat": 51.5101, "lon": -0.0259, "school": False, "info": "£700000, 4 bedrooms"},
        {"name": "Primary school 4", "lat": 51.4973, "lon": 0.1295, "school": True, "info": "Primary school 4, state, good"},
        {"name": "Primary school 5", "lat": 51.5007, "lon": -0.1246, "school": True,
         "info": "Primary school 1, state, outstanding ⭐"},
        {"name": "Property 2", "lat": 51.5571, "lon": 0.2860, "school": False, "info": "£700000, 4 bedrooms"},
        {"name": "Primary school 6", "lat": 51.4282, "lon": 0.1669, "school": True, "info": "Primary school 5, independent"},
        {"name": "Primary school 7", "lat": 51.4876, "lon": -0.2672, "school": True,
         "info": "Primary school 1, state, outstanding ⭐"},
        {"name": "Property 1", "lat": 51.5377, "lon": 0.0761, "school": True, "info": "Primary school 6, state, outstanding ⭐"},
        {"name": "Property 2", "lat": 51.2101, "lon": -0.00, "school": False, "info": "£700000, 4 bedrooms"},
        {"name": "Property in Marylebone", "lat": 51.5189, "lon": -0.1499, "school": False, "info": "£500000, 2 bedrooms"},
        {"name": "Property in Highgate", "lat": 51.5717, "lon": -0.00, "school": False, "info": "£650000, 3 bedrooms"},
        {"name": "Property in Walthamstow", "lat": 51.5902, "lon": 0.0173, "school": False, "info": "£700000, 2 bedrooms"},
        {"name": "Property in Forest Gate", "lat": 51.5439, "lon": -0.0264, "school": False, "info": "£280000, 1 bedrooms"},
        {"name": "Property in Brixton", "lat": 51.4613, "lon": -0.1156, "school": False,
         "info": "£300000, 2 bedrooms"},
    ]

    # Create Folium map centered around London
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=11)

    # Add markers
    for loc in locations:
        if loc["school"]:
            icon = folium.Icon(color="red", icon="school", prefix="fa")
        else:
            icon = folium.Icon(color="blue", icon="house", prefix="fa")

        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            tooltip=loc["name"],
            popup=loc["info"],
            icon=icon
        ).add_to(m)

    # Display map in Streamlit
    st.title("Schools & Properties Map")
    st.markdown("Displaying all the good & outstanding Primary schools in London")
    st_data = st_folium(m, width=700, height=500)

if __name__ == '__main__':
    school_map_view()