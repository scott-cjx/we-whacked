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


def main():
    st.set_page_config(page_title="Super App", page_icon=":rocket:")

    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio("Go to", ["Home", "Reviews", "Mini App 2", "Mini App 3"])

    # backend config
    backend_url = st.sidebar.text_input("Backend base URL", value=DEFAULT_BACKEND)
    st.sidebar.caption("Change this if your API runs on a different host/port")

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "Reviews":
        show_reviews_app(backend_url)
    elif app_choice == "Mini App 2":
        show_mini_app_2()
    elif app_choice == "Mini App 3":
        show_mini_app_3()


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


if __name__ == "__main__":
    main()
