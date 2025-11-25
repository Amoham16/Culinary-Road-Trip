import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np
from pathlib import Path
import base64

# Page configuration
st.set_page_config(
    page_title="Open Data Culinary Road Trip",
    page_icon="🍽️",
    layout="wide"
)
# Load data
@st.cache_data
def load_data():
    """Load the European restaurants dataset"""
    df = pd.read_csv('european_restaurants.csv')
    return df


# ---------- Charger le CSS externe ----------
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ---------- Helper : image -> background-image ----------
def media_div(image_path: str, fallback_gradient: str) -> str:
    path = Path(image_path)
    if path.exists():
        img_data = base64.b64encode(path.read_bytes()).decode()
        return f"<div class='media' style=\"background-image: url('data:image/png;base64,{img_data}');\"></div>"
    else:
        return f"<div class='media' style=\"background-image: {fallback_gradient}\"></div>"


# ---------- Header ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("""
<div class="headerbar">
  <h1 class="site-title">NAMEDLY</h1>
  <div class="headerlinks">
    <a href="#" target="_self">Contact</a>
    <a href="#" target="_self">Download</a>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------- Cards Grid ----------
st.markdown('<div class="grid">', unsafe_allow_html=True)

# ---------------------- CARD 1 ----------------------
st.markdown(
    "<a href='/miashs' target='_self' class='card-link'>"
    "<div class='card clickable-card'>"
    + media_div(
        "images/map_preview.png",
        "radial-gradient(circle at 20% 30%, #d4e5dd 0%, #d4e5dd 25%, #f6f7f8 26%, #f6f7f8 100%)"
      )
    + """
      <div class="body">
        <h3>Carte interactive</h3>
        <p>Présentation visuelle des restaurants sur une carte.
           Filtres par cuisine, prix, note et région.</p>
      </div>
    </div>
    </a>
    """,
    unsafe_allow_html=True
)


# ---------------------- CARD 2 ----------------------
st.markdown(
    "<a href='./app' target='_self' class='card-link'>"
    "<div class='card clickable-card'>"
    + media_div(
        "images/roadtrip.png",
        "radial-gradient(circle at 70% 20%, #ffd6c2 0%, #ffd6c2 18%, #f7e6e0 19%, #f7e6e0 100%)"
      )
    + """
      <div class="body">
        <h3>Road Trip Culinaire</h3>
        <p>Planification d’un itinéraire gourmand selon la localisation
           de l’utilisateur et les étapes proposées.</p>
      </div>
    </div>
    </a>
    """,
    unsafe_allow_html=True
)


# ---------------------- CARD 3 ----------------------
st.markdown(
    "<a href='/Top5' target='_self' class='card-link'>"
    "<div class='card clickable-card'>"
    + media_div(
        "images/profile.png",
        "radial-gradient(circle at 30% 40%, #ffe7a0 0%, #ffe7a0 14%, #f3f4f6 15%, #f3f4f6 100%)"
      )
    + """
      <div class="body">
        <h3>Profil Gourmet</h3>
        <p>Formulaire de goûts, budget et ambiance.
           Génération de recommandations personnalisées.</p>
      </div>
    </div>
    </a>
    """,
    unsafe_allow_html=True
)

# Close containers
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
