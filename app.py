import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Global Species Map")
st.title("🌍 Global distribution of endangered species")

# ------------------------------
# Charger les données
# ------------------------------
@st.cache_data
def load_data():
    df_dist = pd.read_csv("df_final.csv")
    df_species = pd.read_excel("cites_listing_bdd.xlsx")
    
    # Normaliser species_id (string, majuscules, strip)
    df_dist["species_id"] = df_dist["species_id"].astype(str).str.upper().str.strip()
    df_species["species_id"] = df_species["species_id"].astype(str).str.upper().str.strip()
    
    return df_dist, df_species

df_dist, df_species = load_data()

# ------------------------------
# Filtrer les pays invalides (ISO3 = -99)
# ------------------------------
df_dist = df_dist[df_dist["ISO3"] != "-99"]

# ------------------------------
# Filtre status
# ------------------------------
status_options = ["Native", "Introduced", "Reintroduced", "Extinct"]
selected_status = st.selectbox("Select species status:", status_options)
df_filtered = df_dist[df_dist["status"] == selected_status]

# ------------------------------
# Filtre family optionnel
# ------------------------------
if "family" in df_species.columns:
    families_available = df_species["family"].dropna().unique()
    selected_family = st.selectbox("Optional: filter by family:", ["All"] + list(families_available))
    if selected_family != "All":
        species_ids_family = df_species[df_species["family"] == selected_family]["species_id"].unique()
        df_filtered = df_filtered[df_filtered["species_id"].isin(species_ids_family)]

# ------------------------------
# KPI
# ------------------------------
total_species = df_filtered["species_id"].nunique()
total_countries = df_filtered["ISO3"].nunique()
col1, col2 = st.columns(2)
col1.metric("Total species", total_species)
col2.metric("Total countries", total_countries)

# ------------------------------
# Compter espèces par pays
# ------------------------------
country_counts = df_filtered.groupby("ISO3")["species_id"].nunique().reset_index()
country_counts.rename(columns={"species_id": "Nombre d'espèces"}, inplace=True)

# ------------------------------
# Containers séparés pour carte et liste d'espèces
# ------------------------------
map_container = st.container()
species_container = st.container()

# ------------------------------
# Carte choropleth
# ------------------------------
with map_container:
    fig = px.choropleth(
        country_counts,
        locations="ISO3",
        color="Nombre d'espèces",
        hover_name="ISO3",
        color_continuous_scale="Reds",
        projection="natural earth"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Selectbox pour le pays
# ------------------------------
available_countries = country_counts["ISO3"].sort_values().unique()
if len(available_countries) > 0:
    selected_country = st.selectbox("Select a country:", available_countries)

    # Merge sécurisé pour récupérer les caractéristiques
    species_in_country = df_filtered[df_filtered["ISO3"] == selected_country].merge(
        df_species,
        on="species_id",
        how="left"
    )

    # Remplacer les NaN par "Unknown"
    species_in_country.fillna("Unknown", inplace=True)

    # Convertir en liste de dicts pour l'affichage
    species_list = species_in_country.to_dict(orient="records")

    # ------------------------------
    # Liste espèces avec expanders
    # ------------------------------
    with species_container:
        st.subheader(f"Species in {selected_country} ({selected_status})")
        if not species_list:
            st.info("No species found.")
        else:
            for species in species_list:
                full_name = str(species.get("full_name", "Unknown"))
                english_name = str(species.get("english_name", "Unknown"))
                family = str(species.get("family", "Unknown"))
                cites_status = str(species.get("cites_status", "Unknown"))
                species_id = str(species.get("species_id", "Unknown"))

                expander_title = f"{full_name} ({english_name})"

                with st.expander(expander_title):
                    st.markdown(f"**Family:** {family}")
                    st.markdown(f"**CITES status:** {cites_status}")
                    st.markdown(f"**Species ID:** {species_id}")
else:
    st.warning("No countries available for this status.")
