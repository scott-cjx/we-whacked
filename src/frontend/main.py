import streamlit as st
import streamlit.components.v1 as components
import json
import requests

def main():
    st.set_page_config(page_title="Super App", page_icon=":rocket:")

    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio("Go to", ["Home", "Mini App 1", "Mini App 2", "Accessible Map"])

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "Mini App 1":
        show_mini_app_1()
    elif app_choice == "Mini App 2":
        show_mini_app_2()
    elif app_choice == "Mini App 3":
        show_mini_app_3()
    elif app_choice == "Accessible Map":
        show_accessible_map()

def show_home_page():
    st.title("Welcome to the Super App!")
    st.write("This is the central hub for all our amazing mini-applications.")
    st.write("Please select a mini-app from the navigation sidebar to get started.")

def show_mini_app_1():
    st.header("Mini App 1")
    st.write("This is the first mini-application.")
    # Add your Mini App 1 code here

def show_mini_app_2():
    st.header("Mini App 2")
    st.write("This is the second mini-application.")
    # Add your Mini App 2 code here

def show_mini_app_3():
    st.header("Mini App 3")
    st.write("This is the third mini-application.")
    # Add your Mini App 3 code here

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
