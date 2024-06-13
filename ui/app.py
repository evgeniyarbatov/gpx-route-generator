import streamlit as st

st.title('Route Generator')

distance = st.slider("Distance (in km):", min_value=0, max_value=100, value=10, step=1)

