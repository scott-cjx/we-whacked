import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import json
from datetime import datetime
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
            ["Home", "Accessible Map", "User Accessibility Reviews", "Request Service", "AI Assistant"],
            index=["Home", "Accessible Map", "User Accessibility Reviews", "Request Service", "AI Assistant"].index(st.session_state.app_choice)
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
    elif app_choice == "AI Assistant":
        show_chatbot()

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
    col1, col2, col3, col4 = st.columns(4)
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
    with col4:
        st.markdown("<div class='home-col'>", unsafe_allow_html=True)
        if st.button("AI Assistant", key="home_chatbot"):
            st.session_state.app_choice = "AI Assistant"
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
    # Service request form
    with st.form(key="service_request_form"):
        st.markdown("#### Submit a service request")
        req_type = st.selectbox("Request type", options=["ramp", "parking", "signage", "restroom", "other"]) 
        latitude = st.text_input("Latitude", value="")
        longitude = st.text_input("Longitude", value="")
        address = st.text_input("Address", value="")
        description = st.text_area("Description", value="", height=120)
        priority = st.selectbox("Priority", options=["low", "medium", "high"], index=1)
        requester_name = st.text_input("Your name")
        requester_email = st.text_input("Your email (optional)")

        submit = st.form_submit_button("Submit Request")

    if submit:
        # Basic validation
        errors = []
        try:
            lat_f = float(latitude)
        except Exception:
            errors.append("Latitude must be a number")
        try:
            lng_f = float(longitude)
        except Exception:
            errors.append("Longitude must be a number")
        if not address:
            errors.append("Address is required")
        if not description:
            errors.append("Description is required")
        if not requester_name:
            errors.append("Requester name is required")

        if errors:
            for e in errors:
                st.error(e)
        else:
            payload = {
                "request_type": req_type,
                "latitude": lat_f,
                "longitude": lng_f,
                "address": address,
                "description": description,
                "priority": priority,
                "requester_name": requester_name,
                "requester_email": requester_email or None
            }
            try:
                resp = requests.post("http://localhost:8000/service-requests", json=payload, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Service request created: {data.get('request_id')}")
                    st.json(data)
                else:
                    st.error(f"Failed to create request: {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Error calling backend: {e}")

    # Quick link to AI Assistant
    st.markdown("---")
    st.markdown("If you'd like, use the **AI Assistant** tab to draft a request and have the assistant submit it on your behalf.")

    # Database viewer
    st.markdown("---")
    st.subheader("Database Viewer")
    st.write("Inspect stored service requests, reviews, and locations from the backend.")

    # Dataset selector + refresh with simple session caching
    dataset = st.selectbox("Dataset to view", ["service_requests", "reviews", "locations"])

    if 'db_cache' not in st.session_state:
        st.session_state.db_cache = {}

    do_refresh = st.button("Refresh DB View")

    data = None
    if do_refresh or dataset not in st.session_state.db_cache:
        try:
            with st.spinner("Fetching DB contents..."):
                resp = requests.get("http://localhost:8000/service-requests/db/all", timeout=10)
            if resp.status_code == 200:
                all_data = resp.json()
                st.session_state.db_cache = all_data
                data = all_data.get(dataset, [])
            else:
                st.error(f"Failed to fetch DB: {resp.status_code} - {resp.text}")
                data = None
        except Exception as e:
            st.error(f"Error fetching DB: {e}")
            data = None
    else:
        data = st.session_state.db_cache.get(dataset, [])

    if data is None:
        st.info("No data loaded. Click 'Refresh DB View' to fetch data from backend.")
    else:
        st.markdown(f"**{dataset.replace('_', ' ').title()}** — {len(data)} rows")
        if data:
            try:
                import pandas as _pd
                df = _pd.DataFrame(data)
                st.dataframe(df)
            except Exception:
                st.json(data)
        else:
            st.write(f"No {dataset} found.")
    
def show_chatbot():
    st.header("🤖 AI Assistant")
    st.write("Ask me anything about accessibility in Boston, request services, or submit reviews!")
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("function_call"):
                with st.expander("Action Taken"):
                    st.json(msg["function_call"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Prepare chat request
        chat_data = {
            "message": prompt,
            "conversation_history": [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history[:-1]  # Exclude the just-added user message
            ]
        }
        
        # Call chatbot API
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    "http://localhost:8000/chatbot/chat",
                    json=chat_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    assistant_msg = {
                        "role": "model",
                        "content": result["message"],
                        "function_call": result.get("function_called")
                    }
                    st.session_state.chat_history.append(assistant_msg)
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.write(result["message"])
                        if result.get("function_called"):
                            with st.expander("Action Taken"):
                                st.json(result["function_called"])
                    st.rerun()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to chatbot service: {str(e)}")
            st.info("Make sure the backend server is running on http://localhost:8000")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

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

    # Ensure we have selected_location from previous clicks
    sel = st.session_state.get('selected_location') if 'selected_location' in st.session_state else None

    # Add review form (allows users to submit reviews directly from the map page)
    with st.expander("Add a Review", expanded=False):
        st.markdown("Use this form to add an accessibility review for a location. You can provide coordinates or a location id.")
        # Prefill from map selection if available
        form_location_id = st.text_input("Location ID (optional)", value=(sel.get('location_id') if sel and sel.get('location_id') else ""))
        form_lat = st.text_input("Latitude", value=(str(sel.get('lat')) if sel and sel.get('lat') is not None else ""))
        form_lng = st.text_input("Longitude", value=(str(sel.get('lng')) if sel and sel.get('lng') is not None else ""))
        form_title = st.text_input("Review title")
        form_content = st.text_area("Review content", height=120)
        form_rating = st.slider("Rating", min_value=1, max_value=5, value=5)
        form_author = st.text_input("Your name")
        form_tags = st.text_input("Tags (comma-separated, optional)")

        submit_review = st.button("Submit Review")
        new_review_data = None
        if submit_review:
            # Basic validation
            errors = []
            lat_f = None
            lng_f = None
            try:
                lat_f = float(form_lat) if form_lat else None
            except Exception:
                errors.append("Latitude must be a number or left blank")
            try:
                lng_f = float(form_lng) if form_lng else None
            except Exception:
                errors.append("Longitude must be a number or left blank")
            if not form_title:
                errors.append("Title is required")
            if not form_content:
                errors.append("Content is required")
            if not form_author:
                errors.append("Author name is required")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                payload = {
                    "location_id": form_location_id or (f"loc-{int(datetime.now().timestamp())}" if (lat_f is not None and lng_f is not None) else "unknown"),
                    "latitude": lat_f or 0.0,
                    "longitude": lng_f or 0.0,
                    "title": form_title,
                    "content": form_content,
                    "rating": int(form_rating),
                    "author": form_author,
                    "tags": [t.strip() for t in form_tags.split(',')] if form_tags else []
                }

                try:
                    resp = requests.post("http://localhost:8000/reviews", json=payload, timeout=10)
                    if resp.status_code == 200:
                        new_review_data = resp.json()
                        # persist last created review so map can show it
                        st.session_state.last_review = new_review_data
                        st.success(f"Review created: {new_review_data.get('review_id')}")
                        st.json(new_review_data)
                    else:
                        st.error(f"Failed to create review: {resp.status_code} - {resp.text}")
                except Exception as e:
                    st.error(f"Error calling backend: {e}")


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

    # Build GeoJSON features so st_folium can report clicks on features
    poi_features = []
    for r in restaurant_pois:
        popup_html = (
            f"<div style='min-width:250px; font-family:sans-serif;'>"
            f"<div style='font-size:18px; font-weight:700; margin-bottom:4px'>{r['name']}</div>"
            f"<div style='font-size:16px; margin-bottom:6px'>Rating: {r['rating']} ★</div>"
            f"<div style='border-top:1px solid #eee; margin-bottom:6px'></div>"
            + ''.join([f"<div style='margin-bottom:8px'><strong>{rev['stars']}/5</strong>: {rev['text']}</div>" for rev in r['reviews']])
            + "</div>"
        )
        # Create a GeoJSON feature with properties we can read back on click
        feat = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [r['lng'], r['lat']]},
            'properties': {
                'location_id': r.get('id'),
                'name': r.get('name'),
                'rating': r.get('rating'),
                'popup_html': popup_html
            }
        }
        poi_features.append(feat)

    # If a new review was just created earlier in the session, add it to the map as a marker
    try:
        last_rev = st.session_state.get('last_review')
        if last_rev:
            nr = last_rev
            try:
                latn = float(nr.get('latitude', 0))
                lngn = float(nr.get('longitude', 0))
            except Exception:
                latn, lngn = None, None
            if latn and lngn:
                popup_html = f"<div style='min-width:200px'><strong>{nr.get('title')}</strong><div>Rating: {nr.get('rating')} ★</div><div>{nr.get('content')}</div></div>"
                folium.Marker(location=[latn, lngn], popup=folium.Popup(popup_html, max_width=300), icon=make_div_icon('★', '#ffb400', size=28)).add_to(details_fg)
    except Exception:
        pass

    # Add GeoJSON layer for POIs (so st_folium reports clicks)
    try:
        if poi_features:
            geojson = {
                'type': 'FeatureCollection',
                'features': poi_features
            }
            folium.GeoJson(
                geojson,
                name='POIs',
                tooltip=folium.GeoJsonTooltip(fields=['name', 'rating'], aliases=['Name', 'Rating']),
                popup=folium.GeoJsonPopup(fields=['popup_html'], labels=False)
            ).add_to(details_fg)
    except Exception:
        # fallback: add markers individually
        for r in restaurant_pois:
            folium.Marker(location=[r['lat'], r['lng']], popup=r['name']).add_to(details_fg)

    # Add all layers to map
    entrances_fg.add_to(m)
    details_fg.add_to(m)
    ramps_fg.add_to(m)
    service_fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # Render map in Streamlit and capture clicks
    st_data = st_folium(m, height=720)

    # When a GeoJSON feature is clicked, st_folium provides 'last_object_clicked'
    clicked = None
    if isinstance(st_data, dict):
        clicked = st_data.get('last_object_clicked') or st_data.get('last_clicked')

    if clicked and isinstance(clicked, dict):
        props = clicked.get('properties') or {}
        geometry = clicked.get('geometry') or {}
        coords = geometry.get('coordinates') if geometry else None
        lat_click = coords[1] if coords and len(coords) >= 2 else None
        lng_click = coords[0] if coords and len(coords) >= 2 else None
        # Save selected location to session state for the review form
        st.session_state.selected_location = {
            'location_id': props.get('location_id') or props.get('id') or None,
            'name': props.get('name') or (props.get('popup_html')[:60] if props.get('popup_html') else None),
            'lat': lat_click,
            'lng': lng_click,
        }
    # If user selected via GeoJSON popup, also try to parse popup_html for coordinates if missing
    if 'selected_location' in st.session_state and st.session_state.selected_location:
        sel = st.session_state.selected_location
    else:
        sel = None

if __name__ == "__main__":
    main()
