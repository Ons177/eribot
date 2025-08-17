import streamlit as st
import pandas as pd
from PIL import Image
import re

# --- CONFIG PAGE ET STYLE ---
st.set_page_config(page_title="ERIBot - Ericsson", page_icon="🚱")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #003399;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1 {
        color: #ff0000;
        font-weight: bold;
    }
    textarea {
        background-color: #e6f0ff;
        color: #003399;
        font-weight: 600;
    }
    input[type="text"] {
        border: 2px solid #ff0000;
        border-radius: 8px;
        padding: 8px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOGO ---
logo = Image.open("ericsson_logo.png")
st.image(logo, width=150)
st.title("💬 ERIBot - Assistant Réseau Ericsson")
st.write("Posez-moi une question sur un site radio 👇")

# --- CHARGEMENT DU CSV ---
df = pd.read_csv("sites_radio_nabeul.csv")

# Nettoyage et conversion coordonnées
df['LAT'] = df['LAT'].astype(str).str.replace(',', '.').astype(float)
df['LONG'] = df['LONG'].astype(str).str.replace(',', '.').astype(float)

# Récupérer la colonne du nom de site (2e colonne)
site_col = df.columns[1]

# --- EXTRACTION COORDONNEES AVEC REGEX ---
def extraire_coordonnees(msg):
    # Remplacer la virgule décimale dans les nombres par un point (ex: 36,847 -> 36.847)
    msg_corrige = re.sub(r'(\d),(\d)', r'\1.\2', msg)
    # Remplacer la virgule séparatrice entre latitude et longitude par un espace
    msg_corrige = re.sub(r'(\d\.\d+),(\d)', r'\1 \2', msg_corrige)
    # Extraire tous les nombres décimaux (flottants)
    match = re.findall(r'[-+]?\d*\.\d+|\d+', msg_corrige)
    if len(match) >= 2:
        try:
            lat = float(match[0])
            lon = float(match[1])
            return lat, lon
        except:
            return None
    return None

# --- LOGIQUE ERIBOT ---
def get_eribot_response(msg):
    msg_lower = msg.lower()
    msg_upper = msg.upper()

    # --- Mots-clés pour lister tous les sites de Nabeul ---
    list_keywords = [
        "tous les sites",
        "liste des sites",
        "afficher tous les sites",
        "tous les sites de nabeul",
        "liste des sites de nabeul"
    ]

    # --- Mots-clés pour recherche du site le plus proche ---
    nearest_keywords = ["plus proche", "site le plus proche", "nearest", "proche"]

    # 1) ----- Liste de tous les sites de Nabeul -----
    if any(keyword in msg_lower for keyword in list_keywords) and "nabeul" in msg_lower:
        all_sites = df[site_col].tolist()
        return "Voici la liste des sites de Nabeul :\n- " + "\n- ".join(all_sites)

    # 2) ----- Recherche du site le plus proche -----
    if any(keyword in msg_lower for keyword in nearest_keywords):
        coords = extraire_coordonnees(msg)
        if coords:
            lat_user, lon_user = coords
            # Calcul des distances euclidiennes
            df_temp = df.copy()
            df_temp["DISTANCE"] = ((df_temp["LAT"] - lat_user) ** 2 + (df_temp["LONG"] - lon_user) ** 2) ** 0.5
            # Trier et prendre les 3 premiers
            closest = df_temp.nsmallest(3, "DISTANCE")
            # Génération de la réponse
            lines = ["Voici les 3 sites les plus proches :"]
            for i, row in enumerate(closest.itertuples(), start=1):
                lines.append(f"{i}. {getattr(row, site_col)} (distance = {row.DISTANCE:.5f})")
            return "\n".join(lines)

    # 3) ----- Recherche par nom de site -----
    site_data = None
    matched_sites = [site for site in df[site_col] if site.upper() in msg_upper]

    if matched_sites:
        site = matched_sites[0]
        site_data = df[df[site_col] == site].iloc[0]

        if any(k in msg_lower for k in ["oss", "id"]):
            return f"L’OSS ID du site {site} est : {site_data['4G OSS ID']}"
        elif any(k in msg_lower for k in ["radio type 4g", "type radio 4g"]):
            return f"Le type de radio 4G pour {site} est : {site_data['Radio Type 4G']}"
        elif any(k in msg_lower for k in ["radio type 3g", "type radio 3g"]):
            return f"Le type de radio 3G pour {site} est : {site_data['Radio Type 3G']}"
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

    # 4 ----- Recherche dans autres colonnes -----
    msg_clean = msg_lower.replace('[','').replace(']','').replace("'",'').replace('"','').replace(',', '.')
    tokens = msg_clean.split()
    for col in ['4G OSS ID', 'Radio Type 4G', 'Radio Type 3G', 'LAT', 'LONG']:
        for token in tokens:
            if col in ['LAT', 'LONG']:
                try:
                    val = float(token)
                    matched_rows = df[(df[col] - val).abs() < 0.0001]
                except:
                    continue
            else:
                matched_rows = df[df[col].astype(str).str.lower() == token]
            if not matched_rows.empty:
                sites_found = matched_rows[site_col].tolist()
                return f"Les sites correspondants à la valeur '{token}' dans la colonne '{col}' sont : {', '.join(sites_found)}"

    return "Désolé, je n'ai pas trouvé de site correspondant à l'information fournie. Peux-tu reformuler ?"

# --- INTERFACE UTILISATEUR ---
user_input = st.text_input("Votre question")
if user_input:
    response = get_eribot_response(user_input)
    st.text_area("Réponse ERIBot :", value=response, height=250)
