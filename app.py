import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Global distribution of endangered species")

# Charger les données
@st.cache_data
def load_data():
    df_dist = pd.read_csv("df_final.csv")
    df_species = pd.read_csv("df_species.csv")
    df_dist["species_id"] = df_dist["species_id"].astype(str).str.strip()
    df_species["species_id"] = df_species["species_id"].astype(str).str.strip()
    return df_dist, df_species

df_dist, df_species = load_data()

# Filtre statut
status_options = ["Native", "Introduced", "Reintroduced", "Extinct"]
selected_status = st.selectbox("Select species status:", status_options)
df_filtered = df_dist[df_dist["status"] == selected_status]

# Compter espèces par pays
country_counts = df_filtered.groupby("ISO3")["species_id"].nunique().reset_index()
country_counts.rename(columns={"species_id": "Nombre d'espèces"}, inplace=True)

# Carte choropleth
fig = px.choropleth(
    country_counts,
    locations="ISO3",
    color="Nombre d'espèces",
    hover_name="ISO3",
    color_continuous_scale="Reds",
    projection="natural earth"
)
fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

st.subheader("Click on a country to see its species")
clicked = st.plotly_chart(fig, use_container_width=True)

# Récupérer le pays cliqué
click_data = st.session_state.get("click_data", None)
click_data = st.plotly_chart(fig, use_container_width=True).clickData if True else None

selected_country = None
if click_data and "points" in click_data:
    selected_country = click_data["points"][0]["location"]

if selected_country:
    species_in_country = df_filtered[df_filtered["ISO3"] == selected_country].merge(
        df_species[["species_id", "class", "family", "full_name", "english_name", "cites_status"]],
        on="species_id",
        how="left"
    )

    st.subheader(f"Species in {selected_country} with status '{selected_status}'")

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
