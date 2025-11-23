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

    # Session state for navigation visibility and current page
    if 'app_choice' not in st.session_state:
        st.session_state.app_choice = 'Home'
    if 'show_nav' not in st.session_state:
        st.session_state.show_nav = False

    # Show the top menu only when navigation is enabled (not on initial homepage)
    if st.session_state.show_nav:
        app_choice = st.selectbox("Menu", ["Home", "Accessible Map", "User Accessibility Reviews", "Request Service"], index=["Home", "Accessible Map", "User Accessibility Reviews", "Request Service"].index(st.session_state.app_choice))
        st.session_state.app_choice = app_choice
        # If user selects Home from the menu, hide the navigation again
        if app_choice == 'Home':
            st.session_state.show_nav = False
    else:
        app_choice = st.session_state.app_choice

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "User Accessibility Reviews":
        show_mini_app_1()
    elif app_choice == "Request Service":
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
    st.title("Welcome to MapAble Boston!")
    copy = (
        "Your friendly guide to accessible places in Boston. Whether you’re looking for "
        "wheelchair-friendly restaurants, accessible public spaces, or user-rated bathrooms, "
        "MapAble Boston makes it easy to explore the city with confidence. See ratings, read reviews, "
        "and discover the most accessible spots near you—all on one simple, interactive map."
    )
    # Use a clean, slightly larger paragraph font to match the app's simple style
    st.markdown(f"<div style='font-size:18px;line-height:1.5'>{copy}</div>", unsafe_allow_html=True)
    # Buttons for navigation placed under the intro. These reveal the top menu when used.
    st.write("")
    # Inject CSS to make homepage buttons equal width, evenly spaced, and styled light blue
    st.markdown(
        """
        <style>
        /* Row uses fixed gap so spacing between each button is equal */
        .home-row {display:flex; gap:24px; justify-content:center; align-items:center; max-width:780px; margin:12px auto;}
        /* Each column takes equal available space; inner button fills its column (up to max-width) */
        .home-col {flex:1 1 0; display:flex; justify-content:center}
        /* Buttons: solid blue background with white text */
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
    # Prominent intro line (placed above the descriptive line)
    st.markdown("<div style='font-size:18px; font-weight:600; color:#222; margin-bottom:6px;'>Find all accessible places near you with our map, complete with ratings and reviews!</div>", unsafe_allow_html=True)
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

    # Ask user which category they want to focus on. Default to 'All' so map shows everything initially.
    category_options = ["None", "All", "Playgrounds", "Parks", "Ramps", "Parking", "Restrooms", "Service Animal Friendly"]
    # default to 'All' (index 1)
    category_choice = st.selectbox(
        "What are you looking for?",
        category_options,
        index=category_options.index("All")
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

    # Render sample POIs only when the user has chosen a category (not when 'None')
    if category_choice != 'None':
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

    # Only fetch and render endpoint data when the user has selected a category (not when 'None')
    if category_choice != 'None':
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

    # --- Restaurants / Cafes custom markers (soft-corner rectangles with rating) ---
    # We'll add a small infrastructure to place restaurant markers with attached reviews.
    # For now, add a placeholder Clover Food Lab location (use precise coords if you provide them).
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

    def make_rating_div_icon(rating, size=64):
        # Create a soft-corner rectangle with the rating text (white text on blue)
        html = (
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"background:#1e90ff;color:#fff;border-radius:10px;padding:6px 10px;min-width:{int(size*0.8)}px;"
            f"font-weight:600;font-size:14px;box-shadow:0 1px 4px rgba(0,0,0,0.25)\">{rating}</div>"
        )
        return folium.DivIcon(html=html, icon_size=(size, int(size*0.6)), icon_anchor=(int(size/2), int(size/2)))

    # Add restaurant markers to the appropriate feature group (details_fg used here)
    reviews_js_entries = []
    for r in restaurant_pois:
        # build popup content and reviews panel HTML (escaped for JS)
        popup_html = f"<div style='min-width:200px'><strong>{r['name']}</strong><br/>Rating: {r['rating']}</div>"

        # Build the HTML that will become the content under the Reviews title
        # (we do NOT replace the title; we update only the 'reviews-content' div)
        reviews_content_html = f"<div style='font-size:18px;font-weight:700;margin-bottom:6px'>{r['name']}</div>"
        # show numeric rating and stars on top
        stars = '★' * int(round(r['rating']))
        reviews_content_html += f"<div style='font-size:16px;color:#ffb400;font-weight:700;margin-bottom:10px'>{r['rating']} {stars}</div>"
        reviews_content_html += "<div style='border-top:1px solid #eee;margin-bottom:8px'></div>"
        for rev in r['reviews']:
            reviews_content_html += (
                f"<div style='margin-bottom:12px'><div style='font-weight:600'>{rev['stars']}/5</div>"
                f"<div style='color:#222'>{rev['text']}</div></div>"
            )

        # JSON-escape the panel HTML so we can inject it into a small script in the popup
        import json as _json
        escaped_panel = _json.dumps(reviews_content_html)

        # Create a popup that only has a button which sends the reviews HTML
        # to the parent via postMessage. This avoids showing review text on
        # the map itself.
        # Build a JS snippet that posts the escaped HTML panel to the parent window.
        # Use double quotes inside the JS object so we can safely wrap the
        # entire onclick attribute value in single quotes below.
        post_message_js = (
            'window.parent.postMessage({"type":"show_reviews","html":' + escaped_panel + '}, "*");'
        )

        popup_with_button = (
            "<div style='text-align:center;margin-top:6px'>"
            f"<button onclick='{post_message_js}' style='padding:8px 10px; border-radius:6px; border:1px solid #1677cc; background:#1e90ff; color:#fff; cursor:pointer'>Show reviews</button>"
            "</div>"
        )

        folium.Marker(
            location=[r['lat'], r['lng']],
            popup=folium.Popup(popup_with_button, max_width=300),
            icon=make_rating_div_icon(r['rating'])
        ).add_to(details_fg)

        # Add this restaurant's reviews content to the JS mapping so we can
        # attach a click handler to the corresponding Leaflet marker in the
        # rendered map HTML. Use JSON to safely escape the HTML string.
        reviews_js_entries.append({
            'lat': r['lat'],
            'lng': r['lng'],
            'html': reviews_content_html
        })

    # Add the single LayerControl (one corner bar)
    folium.LayerControl(collapsed=False).add_to(m)

    # Render map HTML and display in Streamlit with a left reviews panel
    map_html = m.get_root().render()

    # Inject a small script that finds Leaflet markers by coordinates and
    # attaches a click handler which posts the review HTML to the parent.
    # This works around popup HTML sanitization that can remove onclick handlers.
    try:
        import json as _json
        reviews_js = _json.dumps(reviews_js_entries)
        attach_script = (
            "<script>\n"
            "(function(){\n"
            "  var reviewsMap = " + reviews_js + ";\n"
            "  function attachHandlers(){\n"
            "    try{\n"
            "      for(var k in window.map._layers){\n"
            "        var layer = window.map._layers[k];\n"
            "        if(!layer || !layer.getLatLng) continue;\n"
            "        var ll = layer.getLatLng();\n"
            "        for(var i=0;i<reviewsMap.length;i++){\n"
            "          var r = reviewsMap[i];\n"
            "          if(Math.abs(ll.lat - r.lat) < 1e-6 && Math.abs(ll.lng - r.lng) < 1e-6){\n"
            "            (function(html, lyr){\n"
            "              lyr.on('click', function(){ window.parent.postMessage({type:'show_reviews', html: html}, '*'); });\n"
            "            })(r.html, layer);\n"
            "            break;\n"
            "          }\n"
            "        }\n"
            "      }\n"
            "    }catch(e){console.log('attachHandlers error', e);}\n"
            "  }\n"
            "  setTimeout(attachHandlers, 500);\n"
            "})();\n"
            "</script>\n"
        )
        map_html = map_html + attach_script
    except Exception:
        # If injection fails, continue without the automatic handlers
        pass

    # Prepare initial reviews panel (title + content placeholder) — larger, nicer styling
    reviews_title_html = "<div style='font-size:20px;font-weight:700;margin-bottom:8px;'>Reviews</div>"
    reviews_content_placeholder = ("<div style='padding:6px 0;font-size:14px;color:#666;'>Click an item on the map and then press 'Show reviews' in the popup to view details here.</div>")

    left_col, right_col = st.columns([3, 9])
    with left_col:
            # Reviews panel and a message listener to receive review HTML from
            # the map iframe. The map will postMessage({type:'show_reviews', html: ...})
            # when the user clicks the popup button.
            # Wrap the script in a hidden div so nothing resembling code appears on-screen
            listener_script = '''
            <div style='display:none'>
            <script>
            window.addEventListener('message', function(e) {
                try {
                    var d = e.data;
                    if (d && d.type === 'show_reviews') {
                        var left = document.getElementById('reviews-content'); if (left) { left.innerHTML = d.html; }
                        /* hide map iframe(s) and show reviews in the map area */
                        document.querySelectorAll('iframe').forEach(function(f){ f.style.display='none'; });
                        var mr = document.getElementById('map-reviews');
                        if (mr) {
                            mr.style.display = 'block';
                            mr.innerHTML = d.html + '<div style="margin-top:12px"><button id="back-to-map" style="padding:8px 10px;border-radius:6px;border:1px solid #ccc;background:#f3f3f3;cursor:pointer">Back to map</button></div>';
                            var btn = document.getElementById('back-to-map');
                            if (btn) {
                                btn.addEventListener('click', function(){
                                    mr.style.display='none';
                                    document.querySelectorAll('iframe').forEach(function(f){ f.style.display='block'; });
                                });
                            }
                        }
                    }
                } catch(err) { console.log(err); }
            }, false);
            </script>
            </div>
            '''
            st.markdown("<div id='reviews-panel'>" + reviews_title_html + "<div id='reviews-content'>" + reviews_content_placeholder + "</div></div>" + listener_script, unsafe_allow_html=True)

    with right_col:
        # Placeholder div that will display reviews in place of the map when requested
        st.markdown("<div id='map-reviews' style='display:none;padding:12px;'></div>", unsafe_allow_html=True)
        components.html(map_html, height=720)

if __name__ == "__main__":
    main()
