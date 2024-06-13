import streamlit as st

st.title('Route Generator')

distance = st.slider("Distance (in km):", min_value=0, max_value=50, value=10, step=1)

col1, col2 = st.columns(2)

with col1:
  start_lat = st.text_input(
    "Start latitude:", 
    value=1.3097970339490435, 
  )

with col2:
  start_lng = st.text_input(
    "Start longitude:", 
    value=103.89455470068188, 
  )



