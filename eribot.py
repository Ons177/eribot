import streamlit as st
import pandas as pd
from PIL import Image
import re

# --- CONFIG PAGE ---
st.set_page_config(page_title="ERIBot - Ericsson", page_icon="🚱")

# --- CSS MODERNE ---
st.markdown("""
<style>
/* Fond global */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #002244, #0044cc) !important;
    color: white !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}

/* TITRE */
h1 {
    color: #ffcc00 !important;
    font-weight: bold !important;
    text-align: center !important;
    font-size: 2.5em !important;
    margin-bottom: 20px !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4) !important;
}

/* INPUT USER */
[data-testid="stTextInput"] input {
    border: 2px solid #ffcc00 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-size: 16px !important;
    color: #002244 !important;
    background-color: #ffffff !important;
    font-weight: bold !important;
    transition: all 0.3s ease-in-out !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00ccff !important;
    box-shadow: 0 0 10px #00ccff !important;
    outline: none !important;
}

/* BOUTONS */
[data-testid="stButton"] button {
    background-color: #ffcc00 !important;
    color: #002244 !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 20px !important;
    font-size: 16px !important;
    transition: all 0.3s ease-in-out !important;
}
[data-testid="stButton"] button:hover {
    background-color: #ffaa00 !important;
    color: white !important;
    transform: scale(1.05) !important;
}

/* CARD BOT */
.bot-card {
    background: #e6f0ff !important;
    color: #002244 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin-bottom: 15px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER avec LOGO + TITRE ---
col1, col2 = st.columns([1,6])
with col1:
    st.image("ericsson_logo.png", width=80)
with col2:
    st.markdown("<h1>💬 ERIBot - Assistant Réseau Ericsson</h1>", unsafe_allow_html=True)

st.write("Posez-moi une question sur un site radio 👇")

# --- CHARGEMENT DU CSV ---
df = pd.read_csv("sites_radio_nabeul.csv")

# Nettoyage et conversion coordonnées
df['LAT'] = df['LAT'].astype(str).str.replace(',', '.').astype(float)
df['LONG'] = df['LONG'].astype(str).str.replace(',', '.').astype(float)

# Récupérer la colonne du nom de site
site_col = df.columns[1]

# --- FONCTION DE NORMALISATION ---
def normalize(text):
    return re.sub(r'[\s_]', '', text).upper()

# --- FONCTION DE RÉPONSE ---
def get_eribot_response(msg):
    msg_norm = normalize(msg)

    # Recherche du site par nom
    matched_sites = [site for site in df[site_col] if normalize(site) in msg_norm]

    if matched_sites:
        site = matched_sites[0]
        site_data = df[df[site_col] == site].iloc[0]

        # Recherche de l'information demandée
        if "radio type 4g" in msg.lower():
            return f"Le type de radio 4G pour {site} est : {site_data['Radio Type 4G']}"
        elif "radio type 3g" in msg.lower():
            return f"Le type de radio 3G pour {site} est : {site_data['Radio Type 3G']}"
        elif "oss" in msg.lower():
            return f"L’OSS ID du site {site} est : {site_data['4G OSS ID']}"
        elif "latitude" in msg.lower() or "lat" in msg.lower():
            return f"La latitude du site {site} est : {site_data['LAT']}"
        elif "longitude" in msg.lower() or "long" in msg.lower():
            return f"La longitude du site {site} est : {site_data['LONG']}"
        else:
            return (
                f"Voici les infos disponibles pour le site {site} :\n"
                f"- OSS ID : {site_data['4G OSS ID']}\n"
                f"- Radio Type 4G : {site_data['Radio Type 4G']}\n"
                f"- Radio Type 3G : {site_data['Radio Type 3G']}\n"
                f"- Coordonnées : LAT = {site_data['LAT']}, LONG = {site_data['LONG']}"
            )

    return "Désolé, je n'ai pas trouvé de site correspondant. Vérifie le nom du site."

# --- INTERFACE UTILISATEUR ---
user_input = st.text_input("Votre question")
if user_input:
    response = get_eribot_response(user_input)
    st.text_area("Réponse ERIBot :", value=response, height=250)
