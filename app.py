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
    df = pd.read_csv("df_final.csv")
    
    # Normaliser species_id et country pour merge / filtres
    df["species_id"] = df["species_id"].astype(str).str.upper().str.strip()
    
    # Corriger le nom de Bolivia pour correspondre au code ISO
    df["country"] = df["country"].replace({"Bolivia (Plurinational State of)": "Bolivia"})
    
    return df

df = load_data()

# ------------------------------
# Supprimer pays ISO3 = -99
# ------------------------------
df = df[df["ISO3"] != "-99"]

# ------------------------------
# Filtre status
# ------------------------------
status_options = ["Native", "Introduced", "Reintroduced", "Extinct"]
selected_status = st.selectbox("Select species status:", status_options)
df_filtered = df[df["status"] == selected_status]

# ------------------------------
# Filtre family optionnel
# ------------------------------
if "family" in df.columns:
    families_available = df["family"].dropna().unique()
    selected_family = st.selectbox("Optional: filter by family:", ["All"] + list(families_available))
    if selected_family != "All":
        df_filtered = df_filtered[df_filtered["family"] == selected_family]

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
# Carte choropleth
# ------------------------------
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
# Sélection du pays
# ------------------------------
available_countries = country_counts["ISO3"].sort_values().unique()
if len(available_countries) > 0:
    selected_country = st.selectbox("Select a country:", available_countries)

    species_in_country = df_filtered[df_filtered["ISO3"] == selected_country]

    # Convertir en liste de dicts pour expanders
    species_list = species_in_country.to_dict(orient="records")

    # ------------------------------
    # Expanders pour chaque espèce
    # ------------------------------
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
