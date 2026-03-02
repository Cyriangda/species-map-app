import pandas as pd
import streamlit as st

df_dist = pd.read_csv("df_final.csv")
df_species = pd.read_excel("species_bdd.xlsx")

df_species.columns = df_species.columns.str.strip().str.lower().str.replace(" ", "_")

df_dist["species_id"] = df_dist["species_id"].astype(str).str.upper().str.strip()
df_species["species_id"] = df_species["species_id"].astype(str).str.upper().str.strip()

df_filtered = df_dist[df_dist["status"] == "Native"]  # test
species_in_country = df_filtered.merge(df_species, on="species_id", how="left")

st.write("Filtered DF:", df_filtered.head())
st.write("Species DF:", df_species.head())
st.write("Merged DF:", species_in_country.head())
st.write("Columns after normalization:", df_species.columns.tolist())
