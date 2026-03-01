import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

st.title("🌍 Distribution des espèces")

# Charger données
df = pd.read_csv("df_final.csv")          # species × pays × status
gdf = gpd.read_file("countries.geojson")  # GeoJSON des pays
df_species = pd.read_csv("df_species.csv")  # caractéristiques espèces

# Filtre statut
status_selected = st.selectbox(
    "Choisir le statut",
    ["Native", "Introduced", "Reintroduced", "Extinct"]
)

# Filtrer selon statut choisi
df_filtered = df[df["status"] == status_selected]

# Ajouter info espèces
df_filtered = df_filtered.merge(
    df_species, on="species_ID", how="left"
)

# Compter nombre d'espèces par pays
country_counts = df_filtered.groupby("ISO3")["species_ID"].nunique().reset_index()
country_counts.rename(columns={"species_ID": "nb_species"}, inplace=True)

# Carte choroplèthe avec Plotly
fig = px.choropleth(
    country_counts,
    locations="ISO3",
    color="nb_species",
    hover_name="ISO3",
    color_continuous_scale="Reds"
)
st.plotly_chart(fig)

# Liste espèces par pays si on clique
st.subheader("Détails des espèces")
for iso3 in country_counts["ISO3"]:
    st.write(f"**Pays : {iso3}**")
    species_in_country = df_filtered[df_filtered["ISO3"] == iso3]
    for _, row in species_in_country.iterrows():
        st.markdown(f"- {row['species_name']}: {row.get('caracteristiques','')}") 
