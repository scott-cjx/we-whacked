import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import json
import requests

def main():
    st.set_page_config(page_title="Super App", page_icon=":rocket:")

    # Session state for navigation visibility and current page
    if 'app_choice' not in st.session_state:
        st.session_state.app_choice = 'Home'
    if 'show_nav' not in st.session_state:
        st.session_state.show_nav = False

    # Show the top menu only when navigation is enabled (not on initial homepage)
    if st.session_state.show_nav:
        app_choice = st.selectbox(
            "Menu",
            ["Home", "Accessible Map", "User Accessibility Reviews", "Request Service"],
            index=["Home", "Accessible Map", "User Accessibility Reviews", "Request Service"].index(st.session_state.app_choice)
        )
        st.session_state.app_choice = app_choice
        if app_choice == 'Home':
            st.session_state.show_nav = False
    else:
        app_choice = st.session_state.app_choice

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "User Accessibility Reviews":
        show_mini_app_1()
    elif app_choice == "Request Service":
        show_mini_app_2()
    elif app_choice == "Mini App 3":
        show_mini_app_3()
    elif app_choice == "Accessible Map":
        show_accessible_map()

def show_home_page():
    st.title("Welcome to MapAble Boston!")
    copy = (
        "Your friendly guide to accessible places in Boston. Whether you’re looking for "
        "wheelchair-friendly restaurants, accessible public spaces, or user-rated bathrooms, "
        "MapAble Boston makes it easy to explore the city with confidence. See ratings, read reviews, "
        "and discover the most accessible spots near you—all on one simple, interactive map."
    )
    st.markdown(f"<div style='font-size:18px;line-height:1.5'>{copy}</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown(
        """
        <style>
        .home-row {display:flex; gap:24px; justify-content:center; align-items:center; max-width:780px; margin:12px auto;}
        .home-col {flex:1 1 0; display:flex; justify-content:center}
        .home-col .stButton>button {width:100%; max-width:240px; padding:10px 12px; background-color:#1e90ff; border:1px solid #1677cc; color:#ffffff; border-radius:8px}
        .home-col .stButton>button:hover {background-color:#166bd8}
        .home-col .stButton>button:focus {outline:3px solid rgba(30,144,255,0.25)}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='home-row'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='home-col'>", unsafe_allow_html=True)
        if st.button("Accessible Map", key="home_map"):
            st.session_state.app_choice = "Accessible Map"
            st.session_state.show_nav = True
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='home-col'>", unsafe_allow_html=True)
        if st.button("User Accessibility Reviews", key="home_reviews"):
            st.session_state.app_choice = "User Accessibility Reviews"
            st.session_state.show_nav = True
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='home-col'>", unsafe_allow_html=True)
        if st.button("Request Service", key="home_request"):
            st.session_state.app_choice = "Request Service"
            st.session_state.show_nav = True
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def show_mini_app_1():
    st.header("User Accessibility Reviews")
    st.write("This area will show user-submitted accessibility reviews and ratings.")
    # Add your Mini App 1 code here

def show_mini_app_2():
    st.header("Request Service")
    st.write("Request accessibility-related services or report needs in the city.")
    # Add your Mini App 2 code here

def show_mini_app_3():
    st.header("Mini App 3")
    st.write("This is the third mini-application.")
    # Add your Mini App 3 code here

def show_accessible_map():
    st.header("Accessible Places Map — Boston")
    st.markdown("<div style='font-size:18px; font-weight:600; color:#222; margin-bottom:6px;'>Find all accessible places near you with our map, complete with ratings and reviews!</div>", unsafe_allow_html=True)
    st.write("Interactive map with accessible park entrances, ramps, parking, playgrounds and service-animal friendly places.")

    # Center map
    center = [42.3601, -71.0589]
    m = folium.Map(location=center, zoom_start=13)

    # Layer groups for different POI types
    entrances_fg = folium.FeatureGroup(name="Park Entrances")
    details_fg = folium.FeatureGroup(name="Park Details")
    ramps_fg = folium.FeatureGroup(name="Ramps")
    service_fg = folium.FeatureGroup(name="Service Animal Friendly")

    # Sample restaurant POIs with reviews
    restaurant_pois = [
        {
            'id': 'clover_fin',
            'name': 'CLOVER FOOD LAB (sample location)',
            'lat': 42.3605,
            'lng': -71.0580,
            'rating': 4.9,
            'reviews': [
                { 'text': 'They use online menus to let customers get the menu read out loud', 'stars': 4.8 },
                { 'text': "The fact that I have an access-related question doesn’t faze them because they’re supposed to answer a lot of questions.", 'stars': 5.0 }
            ]
        }
    ]

    # Keep existing ArcGIS/Socrata endpoints intact
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

    # Function to create emoji DivIcon for POIs
    def make_div_icon(emoji, bg, size=30):
        font_size = max(8, int(size * 0.53))
        html = f"<div style='background:{bg};color:white;border-radius:50%;width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;font-size:{font_size}px'>{emoji}</div>"
        anchor = int(size / 2)
        return folium.DivIcon(html=html, icon_size=(size, size), icon_anchor=(anchor, anchor))

    def icon_spec_for_props(props, source_name=None):
        t = ''
        name = ''
        if isinstance(props, dict):
            t = (props.get('TYPE') or props.get('type') or props.get('feature_type') or props.get('category') or '')
            name = (props.get('NAME') or props.get('name') or props.get('park_name') or '')
        t = (t or '').lower()
        name = (name or '').lower()
        if 'play' in t or 'play' in name or 'playground' in name:
            return ('🛝', '#ff66b2', 'Playgrounds')
        if 'park' in t or 'parking' in t or 'parking' in name or 'disab' in t:
            return ('P', '#2196f3', 'Parking')
        if source_name == 'Ramps (city infrastructure)' or 'ramp' in t or 'curb' in name or 'slope' in name:
            return ('♿', '#ff8c42', 'Ramps')
        if source_name == 'Service Animal Friendly' or 'dog' in name or 'service animal' in name or 'service dog' in name:
            return ('🐶', '#8b5a2b', 'Service Animal Friendly')
        if 'park' in name or source_name == 'Park Details (augmented)' or 'park' in t:
            return ('🌳', '#31a354', 'Parks')
        return ('🚻', '#e34a33', 'Restrooms')

    # Fetch and add all endpoint POIs
    for ep in endpoints:
        try:
            resp = requests.get(ep['url'], timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and data.get('type') == 'FeatureCollection' and 'features' in data:
                for feat in data['features']:
                    geom = feat.get('geometry') or {}
                    props = feat.get('properties') or {}
                    if geom and geom.get('type') == 'Point':
                        coords = geom.get('coordinates')
                        if coords and len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                            emoji, color, cat = icon_spec_for_props(props, source_name=ep.get('name'))
                            icon = make_div_icon(emoji, color, size=30)
                            folium.Marker(location=[lat, lng], popup=props.get('NAME') or props.get('name') or '', icon=icon).add_to(ep['layer'])
                    else:
                        folium.GeoJson(feat, style_function=lambda feature, style=ep['style']: style(feature)).add_to(ep['layer'])
            else:
                folium.GeoJson(data, name=ep['name'], style_function=lambda feature, style=ep['style']: style(feature)).add_to(ep['layer'])
        except Exception as e:
            st.sidebar.warning(f"Failed to load {ep['name']}: {e}")

    # Add Clover Food Lab marker with prettier popup
    def make_rating_div_icon(rating, size=64):
        html = (
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"background:#1e90ff;color:#fff;border-radius:10px;padding:6px 10px;min-width:{int(size*0.8)}px;"
            f"font-weight:600;font-size:14px;box-shadow:0 1px 4px rgba(0,0,0,0.25)\">{rating}</div>"
        )
        return folium.DivIcon(html=html, icon_size=(size, int(size*0.6)), icon_anchor=(int(size/2), int(size/2)))

    for r in restaurant_pois:
        popup_html = f"""
        <div style='min-width:250px; font-family:sans-serif;'>
            <div style='font-size:18px; font-weight:700; margin-bottom:4px'>{r['name']}</div>
            <div style='font-size:16px; margin-bottom:6px'>Rating: {r['rating']} ★</div>
            <div style='border-top:1px solid #eee; margin-bottom:6px'></div>
            {''.join([f"<div style='margin-bottom:8px'><strong>{rev['stars']}/5</strong>: {rev['text']}</div>" for rev in r['reviews']])}
        </div>
        """
        folium.Marker(
            location=[r['lat'], r['lng']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=make_rating_div_icon(r['rating'])
        ).add_to(details_fg)

    # Add all layers to map
    entrances_fg.add_to(m)
    details_fg.add_to(m)
    ramps_fg.add_to(m)
    service_fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # Render map in Streamlit
    st_data = st_folium(m, height=720)

if __name__ == "__main__":
    main()
