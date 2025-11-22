import streamlit as st
import requests
import json
from typing import List, Dict, Any

DEFAULT_BACKEND = "http://localhost:8000"
try:
    # Try to read Streamlit secrets if available (may not exist in some environments)
    secrets = getattr(st, "secrets", None)
    if secrets:
        # secrets may support .get or dict-style access
        if hasattr(secrets, "get"):
            DEFAULT_BACKEND = secrets.get("backend_url", DEFAULT_BACKEND)
        else:
            DEFAULT_BACKEND = secrets.get("backend_url") if "backend_url" in secrets else DEFAULT_BACKEND
except Exception:
    # Fall back to default if anything goes wrong
    DEFAULT_BACKEND = DEFAULT_BACKEND

import streamlit.components.v1 as components
import json
import requests

def main():
    st.set_page_config(page_title="Super App", page_icon=":rocket:")

    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio("Go to", ["Home", "Reviews", "Mini App 2", "Mini App 3"])

    # backend config
    backend_url = st.sidebar.text_input("Backend base URL", value=DEFAULT_BACKEND)
    st.sidebar.caption("Change this if your API runs on a different host/port")
    app_choice = st.sidebar.radio("Go to", ["Home", "Mini App 1", "Mini App 2", "Accessible Map"])

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "Reviews":
        show_reviews_app(backend_url)
    elif app_choice == "Mini App 2":
        show_mini_app_2()
    elif app_choice == "Mini App 3":
        show_mini_app_3()
    elif app_choice == "Accessible Map":
        show_accessible_map()


def show_home_page():
    st.title("Welcome to the Super App!")
    st.write("This is the central hub for all our mini-applications.")
    st.write("Select 'Reviews' to open the reviews UI where users can submit and view reviews for map locations.")


def show_reviews_app(backend_url: str):
    st.header("Location Reviews")
    st.write("Use this page to find nearby reviewed locations, view existing reviews, and submit your own.")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Map / Search")
        lat = st.number_input("Latitude", value=42.3601, format="%.6f")
        lon = st.number_input("Longitude", value=-71.0589, format="%.6f")
        radius = st.slider("Radius (miles)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
        if st.button("Find nearby locations"):
            st.session_state["nearby_query"] = (lat, lon, radius)

    # fetch nearby when requested
    if "nearby_query" in st.session_state:
        qlat, qlon, qradius = st.session_state["nearby_query"]
        try:
            url = f"{backend_url.rstrip('/')}/reviews/locations/nearby?latitude={qlat}&longitude={qlon}&radius_miles={qradius}"
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            locations = resp.json().get("locations", [])
        except Exception as e:
            st.error(f"Failed to fetch nearby locations: {e}")
            locations = []

        if locations:
            st.subheader("Nearby locations")
            for loc in locations:
                with st.expander(f"{loc.get('location_id')} — {loc.get('review_count')} reviews"):
                    st.write(f"Coords: {loc.get('latitude')}, {loc.get('longitude')}")
                    st.write(f"Avg rating: {loc.get('average_rating')}")
                    if st.button("View reviews", key=f"view-{loc.get('location_id')}"):
                        st.session_state["selected_location"] = loc.get('location_id')

    # show selected location reviews and a submit form
    if "selected_location" in st.session_state:
        location_id = st.session_state["selected_location"]
        st.subheader(f"Reviews for {location_id}")
        try:
            url = f"{backend_url.rstrip('/')}/reviews/reviews/location/{location_id}"
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            reviews = data.get("reviews", [])
            if not reviews:
                st.info("No reviews yet for this location.")
            for r in reviews:
                st.markdown(f"**{r.get('title')}** — {r.get('rating')}/5 by {r.get('author')}")
                st.write(r.get('content'))
                st.write(f"Posted: {r.get('created_at')}")
                st.divider()
        except Exception as e:
            st.error(f"Failed to load reviews: {e}")

        st.subheader("Submit a review")
        with st.form("review_form"):
            title = st.text_input("Title")
            content = st.text_area("Content")
            rating = st.slider("Rating", 1, 5, 5)
            author = st.text_input("Your name")
            tags_input = st.text_input("Tags (comma separated)")
            submit = st.form_submit_button("Submit review")
        if submit:
            payload = {
                "location_id": location_id,
                "latitude": float(st.session_state.get('nearby_query', (lat, lon))[0]),
                "longitude": float(st.session_state.get('nearby_query', (lat, lon))[1]),
                "title": title,
                "content": content,
                "rating": int(rating),
                "author": author or "anonymous",
                "tags": [t.strip() for t in tags_input.split(',') if t.strip()]
            }
            try:
                url = f"{backend_url.rstrip('/')}/reviews/reviews"
                r = requests.post(url, json=payload, timeout=8)
                r.raise_for_status()
                st.success("Review submitted!")
                # refresh selected location reviews
                del st.session_state["selected_location"]
                st.session_state["selected_location"] = location_id
            except Exception as e:
                st.error(f"Failed to submit review: {e}")


def show_mini_app_2():
    st.header("Mini App 2")
    st.write("This is the second mini-application.")


def show_mini_app_3():
    st.header("Mini App 3")
    st.write("This is the third mini-application.")


def show_accessible_map():
    st.header("Accessible Places Map — Boston")
    st.write("Interactive map with accessible park entrances, ramps, parking, playgrounds and service-animal friendly places.")

    try:
        import folium
        from folium import FeatureGroup, LayerControl
    except Exception:
        st.error("The Python package 'folium' is required to render the map. Install it with: pip install folium")
        return

    # Center map on Boston
    center = [42.3601, -71.0589]
    m = folium.Map(location=center, zoom_start=13, tiles='OpenStreetMap')

    # Feature groups for toggling
    entrances_fg = folium.FeatureGroup(name='Park Entrances (accessible)')
    details_fg = folium.FeatureGroup(name='Park Details (augmented)')
    ramps_fg = folium.FeatureGroup(name='Ramps (city infrastructure)')
    service_fg = folium.FeatureGroup(name='Service Animal Friendly')

    # Ask user which category they want to focus on
    category_choice = st.selectbox(
        "What are you looking for?",
        ["All", "Playgrounds", "Parks", "Ramps", "Parking", "Restrooms", "Service Animal Friendly"]
    )

    # Sample POIs (replace with real data later)
    pois = [
        { 'name': 'Accessible Restroom — City Hall', 'lat': 42.3605, 'lng': -71.0580, 'type': 'restroom' },
        { 'name': 'Ramp — Freedom Trail Access', 'lat': 42.3588, 'lng': -71.0570, 'type': 'ramp' },
        { 'name': 'Disability Parking — Government Center', 'lat': 42.3592, 'lng': -71.0595, 'type': 'parking' },
        { 'name': 'Service Animal Friendly — Public Library', 'lat': 42.3493, 'lng': -71.0780, 'type': 'service' },
        { 'name': 'Playground — Friendly Park', 'lat': 42.3612, 'lng': -71.0555, 'type': 'playground' }
    ]

    def make_div_icon(emoji, bg, size=30):
        # size controls diameter and font-size
        font_size = max(8, int(size * 0.53))
        html = f"<div style='background:{bg};color:white;border-radius:50%;width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;font-size:{font_size}px'>{emoji}</div>"
        anchor = int(size / 2)
        return folium.DivIcon(html=html, icon_size=(size, size), icon_anchor=(anchor, anchor))

    def icon_spec_for_props(props, source_name=None):
        # returns (emoji, color, category)
        t = ''
        name = ''
        if isinstance(props, dict):
            t = (props.get('TYPE') or props.get('type') or props.get('feature_type') or props.get('category') or '')
            name = (props.get('NAME') or props.get('name') or props.get('park_name') or '')
        t = (t or '').lower()
        name = (name or '').lower()

        # playground
        if 'play' in t or 'play' in name or 'playground' in name:
            return ('🛝', '#ff66b2', 'Playgrounds')

        # parking
        if 'park' in t or 'parking' in t or 'parking' in name or 'disab' in t:
            return ('P', '#2196f3', 'Parking')

        # ramps
        if source_name == 'Ramps (city infrastructure)' or 'ramp' in t or 'curb' in name or 'slope' in t:
            return ('♿', '#ff8c42', 'Ramps')

        # service animal / dog
        if source_name == 'Service Animal Friendly' or 'dog' in name or 'service animal' in name or 'service dog' in name:
            return ('🐶', '#8b5a2b', 'Service Animal Friendly')

        # park/tree default
        if 'park' in name or source_name == 'Park Details (augmented)' or 'park' in t:
            return ('🌳', '#31a354', 'Parks')

        # restroom fallback
        return ('🚻', '#e34a33', 'Restrooms')

    for p in pois:
        emoji, color, cat = icon_spec_for_props({'type': p.get('type'), 'name': p.get('name')}, source_name=p.get('type'))
        # decide vibrant or subdued
        if category_choice == 'All' or category_choice == cat:
            icon = make_div_icon(emoji, color, size=30)
        else:
            icon = make_div_icon(emoji, '#bdbdbd', size=16)

        # choose feature group mapping for sample types
        if p['type'] == 'playground':
            fg = details_fg
        elif p['type'] == 'restroom':
            fg = entrances_fg
        elif p['type'] == 'ramp':
            fg = ramps_fg
        elif p['type'] == 'parking':
            fg = entrances_fg
        elif p['type'] == 'service':
            fg = service_fg
        else:
            fg = details_fg

        folium.Marker(location=[p['lat'], p['lng']], popup=p['name'], icon=icon).add_to(fg)

    # Add the feature groups to the map
    entrances_fg.add_to(m)
    details_fg.add_to(m)
    ramps_fg.add_to(m)
    service_fg.add_to(m)

    # Server-side fetch of real ArcGIS/Socrata endpoints and add as GeoJSON layers
    endpoints = [
        {
            'name': 'Park Entrances (accessible)',
            'url': 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/BPRD_Accessible_Park_Entrances/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
            'layer': entrances_fg,
            'style': lambda feat: {'color': '#e34a33'}
        },
        {
            'name': 'Park Details (augmented)',
            'url': 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/BPRD_Accessible_Park_Details_Augmented/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson',
            'layer': details_fg,
            'style': lambda feat: {'color': '#31a354'}
        },
        {
            'name': 'Ramps (city infrastructure)',
            'url': 'https://gisportal.boston.gov/arcgis/rest/services/Infrastructure/OpenData/MapServer/3/query?where=1%3D1&outFields=*&f=geojson',
            'layer': ramps_fg,
            'style': lambda feat: {'color': '#756bb1'}
        }
    ]

    # (Removed user URL inputs — datasets are loaded from configured endpoints only)

    for ep in endpoints:
        try:
            resp = requests.get(ep['url'], timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # If FeatureCollection with point features, add as individual markers with icons
            if isinstance(data, dict) and data.get('type') == 'FeatureCollection' and 'features' in data:
                for feat in data['features']:
                    geom = feat.get('geometry') or {}
                    props = feat.get('properties') or {}
                    if geom and geom.get('type') == 'Point':
                        coords = geom.get('coordinates')
                        # GeoJSON coordinates are [lng, lat]
                        if coords and len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                            emoji, color, cat = icon_spec_for_props(props, source_name=ep.get('name'))
                            if category_choice == 'All' or category_choice == cat:
                                icon = make_div_icon(emoji, color, size=30)
                            else:
                                icon = make_div_icon(emoji, '#bdbdbd', size=16)
                            folium.Marker(location=[lat, lng], popup=props.get('NAME') or props.get('name') or '', icon=icon).add_to(ep['layer'])
                    else:
                        # Non-point geometries — add the raw GeoJson to the layer
                        folium.GeoJson(feat, style_function=lambda feature, style=ep['style']: style(feature)).add_to(ep['layer'])
            else:
                # Fallback: add entire GeoJSON if structure unexpected
                folium.GeoJson(data, name=ep['name'], style_function=lambda feature, style=ep['style']: style(feature)).add_to(ep['layer'])
        except Exception as e:
            # Keep errors out of the main page UI; surface them in the sidebar
            st.sidebar.warning(f"Failed to load {ep['name']}: {e}")

    # Add the single LayerControl (one corner bar)
    folium.LayerControl(collapsed=False).add_to(m)

    # Render map HTML and display in Streamlit
    map_html = m.get_root().render()
    components.html(map_html, height=720)

if __name__ == "__main__":
    main()
