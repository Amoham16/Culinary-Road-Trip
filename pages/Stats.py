import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="Stats & Visualisations", layout="wide")

# Charger le CSS externe (optionnel)
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ==========================
# 🔹 Navigation
# ==========================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Carte 3D", "Statistiques"])


# ==========================
# 🔹 Chargement des données (cache)
# ==========================
@st.cache_data(ttl=3600)
def load_data():
    usecols = [
        "restaurant_name", "country", "city",
        "latitude", "longitude",
        "avg_rating", "total_reviews_count",
        "cuisines"
    ]

    df = pd.read_csv("tripadvisor_european_restaurants.csv", usecols=usecols)

    # Nettoyage de base
    df = df.dropna(subset=["latitude", "longitude"])
    df["cuisines"] = df["cuisines"].fillna("Inconnue")
    df["cuisines_clean"] = df["cuisines"].apply(lambda x: x.split(",")[0].strip())
    df["city"] = df["city"].fillna("Inconnue")
    df["country"] = df["country"].fillna("Inconnu")

    return df


df = load_data()


# ===========================
# PAGE 1 : CARTE 3D
# ===========================
if page == "Carte 3D":
    st.title("🏙️ Carte 3D — Visualisation des restaurants")

    # -------- Filtres ----------
    col1, col2, col3 = st.columns(3)

    with col1:
        cuisine = st.selectbox(
            "🍽 Type de cuisine",
            ["Toutes"] + sorted(df["cuisines_clean"].unique())
        )

    with col2:
        country = st.selectbox(
            "🌍 Pays",
            ["Tous"] + sorted(df["country"].unique())
        )

    with col3:
        min_rating = st.slider(
            "⭐ Note minimum", 0.0, 5.0, 4.0, step=0.1
        )

    # Appliquer filtres
    df_filtered = df.copy()

    if cuisine != "Toutes":
        df_filtered = df_filtered[df_filtered["cuisines_clean"] == cuisine]

    if country != "Tous":
        df_filtered = df_filtered[df_filtered["country"] == country]

    df_filtered = df_filtered[df_filtered["avg_rating"] >= min_rating]

    # -------- Mode d'affichage ----------
    st.subheader("🎛️ Mode d'affichage (hauteur des colonnes)")

    mode = st.selectbox(
        "Afficher la hauteur en fonction de :",
        [
            "Nombre d'avis",
            "Note moyenne",
            "Popularité (note × avis)",
            "Uniforme"
        ]
    )

    df_filtered = df_filtered.copy()  # éviter les warnings

    if mode == "Nombre d'avis":
        df_filtered["height"] = df_filtered["total_reviews_count"]

    elif mode == "Note moyenne":
        df_filtered["height"] = df_filtered["avg_rating"] * 20  # scaling

    elif mode == "Popularité (note × avis)":
        df_filtered["height"] = (
            df_filtered["avg_rating"] * df_filtered["total_reviews_count"] / 5
        )

    else:  # Uniforme
        df_filtered["height"] = 50

    # Normalisation si trop grand
    if not df_filtered.empty and df_filtered["height"].max() > 5000:
        df_filtered["height"] = df_filtered["height"] / 50

    # -------- Carte 3D ----------
    st.subheader("🗺️ Carte 3D")

    if df_filtered.empty:
        st.warning("Aucun restaurant trouvé avec ces filtres.")
    else:
        view = pdk.ViewState(
            latitude=df_filtered["latitude"].mean(),
            longitude=df_filtered["longitude"].mean(),
            zoom=4,
            pitch=55,
        )

        layer_3d = pdk.Layer(
            "ColumnLayer",
            data=df_filtered,
            get_position=["longitude", "latitude"],
            get_elevation="height",        # 🔹 on utilise la colonne calculée
            elevation_scale=15,
            radius=12000,
            get_color=[60, 120, 255, 180],
            pickable=True,
            auto_highlight=True,
        )

        deck_3d = pdk.Deck(
            initial_view_state=view,
            layers=[layer_3d],
            tooltip={
                "text": "{restaurant_name}\n⭐ {avg_rating}\nAvis: {total_reviews_count}"
            },
        )

        st.pydeck_chart(deck_3d)

    # -------- Analyses graphiques ----------
    st.subheader("📊 Analyses complémentaires")

    if not df_filtered.empty:
        df_country = (
            df_filtered.groupby("country")
            .agg(
                avg_rating_mean=("avg_rating", "mean"),
                total_reviews_sum=("total_reviews_count", "sum"),
                count_resto=("restaurant_name", "count"),
            )
            .sort_values(by="avg_rating_mean", ascending=False)
        )

        df_cuisine = (
            df_filtered.groupby("cuisines_clean")
            .agg(
                avg_rating_mean=("avg_rating", "mean"),
                total_reviews_sum=("total_reviews_count", "sum"),
                count_resto=("restaurant_name", "count"),
            )
            .sort_values(by="avg_rating_mean", ascending=False)
        )

        st.write("Top pays (par note moyenne) :")
        st.dataframe(df_country.head(10))

        st.write("Top cuisines (par note moyenne) :")
        st.dataframe(df_cuisine.head(10))
    else:
        st.info("Pas d'analyses possibles : aucun restaurant après filtrage.")


# ===========================
# PAGE 2 : TRENDING / STAT
# ===========================
elif page == "Statistiques":
    # -------- Filtres --------
    col1, col2 = st.columns(2)
    with col1:
        country_filter = st.multiselect(
            "Filter by Country",
            options=sorted(df["country"].unique()),
            default=None,
        )
    with col2:
        cuisine_filter = st.multiselect(
            "Filter by Cuisine",
            options=sorted(df["cuisines_clean"].unique()),
            default=None,
        )

    filtered_df = df.copy()
    if country_filter:
        filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]
    if cuisine_filter:
        filtered_df = filtered_df[filtered_df["cuisines_clean"].isin(cuisine_filter)]



    # -------- Metrics --------
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Restaurants", len(filtered_df))
    with c2:
        if len(filtered_df) > 0:
            st.metric("Average Rating", f"{filtered_df['avg_rating'].mean():.2f}")
        else:
            st.metric("Average Rating", "N/A")
    with c3:
        st.metric("Countries", filtered_df["country"].nunique())

    # -------- Top countries by count --------
    st.subheader("Top Countries by Restaurant Count")
    if not filtered_df.empty:
        country_counts = filtered_df["country"].value_counts().head(10)
        fig = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation="h",
            labels={"x": "Number of Restaurants", "y": "Country"},
            color=country_counts.values,
            color_continuous_scale="Viridis",
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display for country distribution.")

    # -------- Cuisine distribution --------
    st.subheader("Cuisine Type Distribution")
    if not filtered_df.empty:
        cuisine_counts = filtered_df["cuisines_clean"].value_counts()
        fig2 = px.pie(
            values=cuisine_counts.values,
            names=cuisine_counts.index,
            title="",
            hole=0.4,
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data to display for cuisine distribution.")
