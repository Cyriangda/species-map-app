import streamlit as st
import pandas as pd

st.title("🌍 Distribution des espèces")

df = pd.read_csv("df_final.csv")
st.write(df.head())
