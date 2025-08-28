import streamlit as st
import pandas as pd
from PIL import Image
import re 

# --- CONFIG PAGE ---
st.set_page_config(page_title="ERIBot - Ericsson", page_icon="🚱")

# --- CSS COMPLET ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #002244, #0044cc) !important;
    color: white !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
h1 {
    color: #ffcc00 !important;
    font-weight: bold !important;
    text-align: center !important;
    font-size: 2.5em !important;
    margin-bottom: 20px !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4) !important;
}
[data-testid="stTextInput"] input {
    border: 2px solid #ffcc00 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-size: 16px !important;
    color: #002244 !important;
    background-color: #ffffff !important;
    font-weight: bold !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00ccff !important;
    box-shadow: 0 0 10px #00ccff !important;
    outline: none !important;
}
[data-testid="stButton"] button {
    background-color: #ffcc00 !important;
    color: #002244 !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-size: 16px !important;
}
[data-testid="stButton"] button:hover {
    background-color: #ffaa00 !important;
    color: white !important;
    transform: scale(1.05) !important;
}
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

# --- HEADER ---
col1, col2 = st.columns([1,6])
with col1:
    st.image("ericsson_logo.png", width=80)
with col2:
    st.markdown("<h1>💬 ERIBot - Assistant Réseau Ericsson</h1>", unsafe_allow_html=True)

st.write("Posez-moi une question sur un site radio 👇")

# --- CHARGEMENT CSV ---
df = pd.read_csv("sites_radio_nabeul.csv")
df['LAT'] = df['LAT'].astype(str).str.replace(',', '.').astype(float)
df['LONG'] = df['LONG'].astype(str).str.replace(',', '.').astype(float)
site_col = df.columns[1]

# --- EXTRACTION COORDONNEES ---
def extraire_coordonnees(msg):
    msg_corrige = re.sub(r'(\d),(\d)', r'\1.\2', msg)
    msg_corrige = re.sub(r'(\d\.\d+),(\d)', r'\1 \2', msg_corrige)
    match = re.findall(r'[-+]?\d*\.\d+|\d+', msg_corrige)
    if len(match) >= 2:
        try:
            lat = float(match[0])
            lon = float(match[1])
            return lat, lon
        except:
            return None
    return None

# --- FONCTION PRINCIPALE ---
def get_eribot_response(msg):
    msg_lower = msg.lower()
    msg_upper = msg.upper()

    # Liste tous les sites
    list_keywords = ["tous les sites de nabeul", "liste des sites de nabeul", "afficher tous les sites de nabeul", "les sites de nabeul"]
    if any(keyword in msg_lower for keyword in list_keywords):
        all_sites = df[site_col].tolist()
        return "Voici la liste des sites de Nabeul :\n- " + "\n- ".join(all_sites)

    # Recherche par coordonnées
    coord = extraire_coordonnees(msg)
    if coord:
        lat_val, long_val = coord
        tolerance = 1e-4
        matched_rows = df[((df['LAT'] - lat_val).abs() < tolerance) & ((df['LONG'] - long_val).abs() < tolerance)]
        if not matched_rows.empty:
            site = matched_rows[site_col].iloc[0]
            return f"Le site correspondant aux coordonnées {lat_val}, {long_val} est : {site}"
        else:
            df_temp = df.copy()
            df_temp["DISTANCE"] = ((df_temp["LAT"] - lat_val)**2 + (df_temp["LONG"] - long_val)**2)**0.5
            closest = df_temp.nsmallest(3, "DISTANCE")
            lines = ["Aucun site exact trouvé. Voici les 3 sites les plus proches :"]
            for i, row in enumerate(closest.itertuples(), start=1):
                lines.append(f"{i}. {getattr(row, site_col)} (distance = {row.DISTANCE:.5f})")
            return "\n".join(lines)

    # Recherche par nom de site
    
        # --- Recherche par nom de site (corrigée pour type radio) ---
matched_sites = [site for site in df[site_col] if site.strip().upper() in msg_upper]
if matched_sites:
    site = matched_sites[0]
    site_data = df[df[site_col] == site].iloc[0]
    
    # Vérification du type de radio demandé
    if any(k in msg_lower for k in ["radio type 4g", "type radio 4g"]):
        return f"Le type de radio 4G pour {site} est : {site_data['Radio Type 4G']}"
    elif any(k in msg_lower for k in ["radio type 3g", "type radio 3g"]):
        return f"Le type de radio 3G pour {site} est : {site_data['Radio Type 3G']}"
    elif any(k in msg_lower for k in ["oss", "id"]):
        return f"L’OSS ID du site {site} est : {site_data['4G OSS ID']}"
    elif any(k in msg_lower for k in ["gps", "coordonnée"]):
        return f"Coordonnées GPS de {site} : LAT = {site_data['LAT']}, LONG = {site_data['LONG']}"
    elif any(k in msg_lower for k in ["latitude", "lat"]):
        return f"La latitude du site {site} est : {site_data['LAT']}"
    elif any(k in msg_lower for k in ["longitude", "long"]):
        return f"La longitude du site {site} est : {site_data['LONG']}"
    else:
        return (
            f"Voici les infos disponibles pour le site {site} :\n"
            f"- OSS ID : {site_data['4G OSS ID']}\n"
            f"- Radio Type 4G : {site_data['Radio Type 4G']}\n"
            f"- Radio Type 3G : {site_data['Radio Type 3G']}\n"
            f"- Coordonnées : LAT = {site_data['LAT']}, LONG = {site_data['LONG']}"
        )


    return "Désolé, je n'ai pas trouvé de site correspondant. Vérifiez le nom exact ou fournissez les coordonnées."

# --- INTERFACE UTILISATEUR ---
user_input = st.text_input("Votre question")
if user_input:
    response = get_eribot_response(user_input)
    st.text_area("Réponse ERIBot :", value=response, height=250, key="bot_response")
