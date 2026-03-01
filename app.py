import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🌍 Global distribution of endangered species")

# ------------------------------
# Charger les données
# ------------------------------
@st.cache_data
def load_data():
    df_dist = pd.read_csv("df_final.csv")
    df_species = pd.read_csv("df_species.csv")

    # Nettoyage ID
    df_dist["species_id"] = df_dist["species_id"].astype(str).str.strip()
    df_species["species_id"] = df_species["species_id"].astype(str).str.strip()
    return df_dist, df_species

df_dist, df_species = load_data()

# ------------------------------
# Filtre statut
# ------------------------------
status_options = ["Native", "Introduced", "Reintroduced", "Extinct"]
selected_status = st.selectbox("Select species status:", status_options)

df_filtered = df_dist[df_dist["status"] == selected_status]

# ------------------------------
# Créer la carte avec Folium
# ------------------------------
m = folium.Map(location=[20, 0], zoom_start=2)

# Ajouter des polygones pour chaque pays (approximatif via ISO3)
for iso3 in df_filtered["ISO3"].unique():
    # Pour simplifier, on met un marker au lieu d'une frontière GeoJSON
    country_count = df_filtered[df_filtered["ISO3"] == iso3]["species_id"].nunique()
    folium.Marker(
        location=[0, 0],  # on peut remplacer par vrai centroid si dispo
        popup=f"{iso3} - {country_count} species",
        tooltip=iso3
    ).add_to(m)

# ------------------------------
# Afficher la carte et récupérer le clic
# ------------------------------
st.subheader("Click a country marker to see its species")
map_data = st_folium(m, width=700, height=500)

# ------------------------------
# Vérifier si un marker a été cliqué
# ------------------------------
if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
    # On récupère l'ISO3 depuis le tooltip
    clicked_iso3 = map_data["last_object_clicked"]["tooltip"]
    
    species_in_country = df_filtered[df_filtered["ISO3"] == clicked_iso3].merge(
        df_species[["species_id", "class", "family", "full_name", "english_name", "cites_status"]],
        on="species_id",
        how="left"
    )

    st.subheader(f"Species in {clicked_iso3} with status '{selected_status}'")

    if species_in_country.empty:
        st.info("No species found.")
    else:
        for _, row in species_in_country.iterrows():
            full_name = row.get("full_name", "Unknown name")
            english_name = row.get("english_name", "")
            species_class = row.get("class", "")
            family = row.get("family", "")
            cites = row.get("cites_status", "")

            with st.expander(f"{full_name} ({english_name})"):
                st.markdown(f"**Classe :** {species_class}")
                st.markdown(f"**Famille :** {family}")
                st.markdown(f"**Statut CITES :** {cites}")
                st.markdown(f"**Species ID :** {row['species_id']}")
