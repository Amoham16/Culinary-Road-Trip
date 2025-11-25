import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np


# Load data
@st.cache_data
def load_data():
    """Load the European restaurants dataset"""
    df = pd.read_csv('european_restaurants.csv')
    return df

# Main title
st.title("🍽️ Open Data Culinary Road Trip")
st.markdown("*Discover trending restaurants, find the best spots nearby, and plan a foodie road trip across Europe!*")
st.write("Bienvenue dans votre exploration culinaire en Europe à partir de données **Open Data** 🍷🇫🇷🇮🇹🇪🇸")

# Load the data
df = load_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Trending Restaurants", "Road Trip Planner"])



# ===========================
# PAGE 3: ROAD TRIP PLANNER
# ===========================
if page == "Road Trip Planner":
    st.header("🚗 Multi-Day Foodie Road Trip Planner")
    st.markdown("Plan your perfect culinary journey across Europe!")

    # --- stocker le résultat dans le state (simple) ---
    if "roadtrip_results" not in st.session_state:
        st.session_state.roadtrip_results = None

    # =========
    # CRITÈRES
    # =========
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Trip Settings")
        min_rating_trip = st.slider(
            "Minimum Restaurant Rating",
            min_value=3.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )

        preferred_cuisines = st.multiselect(
            "Preferred Cuisines (optional)",
            options=sorted(df['cuisine'].unique()),
            default=None
        )

    with c2:
        st.subheader("Location Preferences")

        all_countries = sorted(df['country'].unique())
        preferred_countries = st.multiselect(
            "Countries to Visit",
            options=all_countries,
            default=[]
        )

        # Villes dispo selon les pays choisis
        if preferred_countries:
            possible_cities = sorted(
                df[df['country'].isin(preferred_countries)]['city'].unique()
            )
        else:
            possible_cities = sorted(df['city'].unique())

        selected_cities = st.multiselect(
            "Cities to include in the trip",
            options=possible_cities,
            default=possible_cities[:3] if len(possible_cities) >= 3 else possible_cities
        )

    st.markdown("### Number of days per city")
    days_per_city = {}
    total_days = 0
    for city in selected_cities:
        days = st.number_input(
            f"Days in {city}",
            min_value=1,
            max_value=30,
            value=2,
            step=1,
            key=f"days_{city}"
        )
        days_per_city[city] = days
        total_days += days

    # ======================
    #   GÉNÉRATION DU TRIP
    # ======================
    if st.button("🎯 Generate Road Trip", type="primary"):
        if not selected_cities:
            st.warning("Please select at least one city.")
            st.session_state.roadtrip_results = None
        else:
            trip_df = df.copy()

            if preferred_countries:
                trip_df = trip_df[trip_df['country'].isin(preferred_countries)]
            if selected_cities:
                trip_df = trip_df[trip_df['city'].isin(selected_cities)]
            if preferred_cuisines:
                trip_df = trip_df[trip_df['cuisine'].isin(preferred_cuisines)]

            trip_df = trip_df[trip_df['rating'] >= min_rating_trip]

            # Coût estimé (optionnel)
            price_to_cost = {'$': 20, '$$': 40, '$$$': 80, '$$$$': 150}
            trip_df['estimated_cost'] = trip_df['price_range'].map(price_to_cost)

            selected_restaurants = []
            for city, n_days in days_per_city.items():
                city_df = trip_df[trip_df['city'] == city].sort_values(
                    ['rating', 'reviews_count'],
                    ascending=[False, False]
                )
                if len(city_df) == 0:
                    st.warning(f"No restaurants found for {city} with these filters.")
                    continue
                if len(city_df) < n_days:
                    st.warning(f"Only {len(city_df)} restaurants found for {city} (need {n_days}).")
                    n_days = len(city_df)

                # 1 resto par jour : top n_days
                selected_restaurants.extend(city_df.head(n_days).to_dict(orient="records"))

            if len(selected_restaurants) == 0:
                st.warning("No restaurants found. Try relaxing your filters (rating, cuisine, etc.).")
                st.session_state.roadtrip_results = None
            else:
                total_cost = float(sum(
                    r.get('estimated_cost', 0)
                    for r in selected_restaurants
                    if not pd.isna(r.get('estimated_cost', np.nan))
                ))
                countries_visited = len(set(r['country'] for r in selected_restaurants))
                avg_rating = float(np.mean([r['rating'] for r in selected_restaurants]))

                st.session_state.roadtrip_results = {
                    "selected_restaurants": selected_restaurants,
                    "days_per_city": days_per_city,
                    "total_days": total_days,
                    "countries_visited": countries_visited,
                    "avg_rating": avg_rating,
                    "total_cost": total_cost
                }

                st.success("✅ Road trip generated and saved! Scroll to see it below 👇")

    # ======================
    #   AFFICHAGE DU TRIP
    # ======================
    results = st.session_state.roadtrip_results

    if results is None:
        st.info("Choose countries, cities and days per city, then click **Generate Road Trip**.")
    else:
        selected_restaurants = results["selected_restaurants"]
        days_per_city = results["days_per_city"]
        total_days = results["total_days"]

        st.subheader("📊 Trip Summary")
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1:
            st.metric("Total Days", total_days)
        with cc2:
            st.metric("Restaurant Stops", len(selected_restaurants))
        with cc3:
            st.metric("Countries", results["countries_visited"])
        with cc4:
            st.metric("Avg Rating", f"⭐ {results['avg_rating']:.2f}")

        st.subheader("📅 Your Itinerary")

        day_idx = 0
        for city, n_days in days_per_city.items():
            if n_days == 0:
                continue
            st.markdown(f"## 📍 {city} — {n_days} day(s)")
            for i in range(n_days):
                if day_idx >= len(selected_restaurants):
                    break
                r = selected_restaurants[day_idx]
                st.markdown(f"### Day {day_idx + 1}")
                with st.container():
                    k1, k2, k3 = st.columns([3, 1, 1])
                    with k1:
                        st.markdown(f"**Restaurant: {r['name']}**")
                        st.markdown(f"📍 {r['city']}, {r['country']} | 🍴 {r['cuisine']}")
                        st.markdown(f"📧 {r.get('address', 'Address not available')}")
                    with k2:
                        st.markdown(f"⭐ **{r['rating']}**")
                        if not pd.isna(r.get('estimated_cost', np.nan)):
                            st.markdown(f"💰 {r['price_range']} (~€{int(r['estimated_cost'])})")
                        else:
                            st.markdown(f"💰 {r['price_range']}")
                    with k3:
                        st.markdown(f"📞 {r.get('phone', 'N/A')}")
                day_idx += 1
            st.divider()

        # ======================
        #        MAP
        # ======================
        st.subheader("🗺️ Trip Map")
        trip_restaurants_df = pd.DataFrame(selected_restaurants)
        center_lat = trip_restaurants_df['latitude'].mean()
        center_lon = trip_restaurants_df['longitude'].mean()

        trip_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='OpenStreetMap'
        )

        for idx, r in enumerate(selected_restaurants):
            folium.Marker(
                location=[r['latitude'], r['longitude']],
                popup=f"<b>Stop {idx+1}: {r['name']}</b><br>{r['city']}, {r['country']}",
                tooltip=f"Stop {idx+1}: {r['name']}",
                icon=folium.DivIcon(html=f"""
                    <div style="background-color: #FF4B4B;
                                color: white;
                                border-radius: 50%;
                                width: 30px;
                                height: 30px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-weight: bold;
                                font-size: 14px;
                                border: 2px solid white;">
                        {idx+1}
                    </div>
                """)
            ).add_to(trip_map)

        coordinates = [
            [r['latitude'], r['longitude']]
            for r in selected_restaurants
        ]
        folium.PolyLine(
            coordinates,
            color='#FF4B4B',
            weight=3,
            opacity=0.7,
            popup='Trip Route'
        ).add_to(trip_map)

        st_folium(trip_map, width=1400, height=500)
