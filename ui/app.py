import base64

import streamlit as st

from utils import create_routes

def create_download_link(gpx, distance):
    b64 = base64.b64encode(gpx.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{distance}km.gpx"><button>{distance}km.gpx</button></a>'
    return href

st.title('Route Generator')

distance_km = st.slider("Distance (in km):", min_value=0, max_value=5, value=2, step=1)

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
  
create = st.button(
  "Create",
  type="primary",
  use_container_width=True,
)

if create:  
  figs, gpx_routes, distances = create_routes(start_lat, start_lng, distance_km)
  for fig, gpx_route, distance in zip(figs, gpx_routes, distances):
    st.pyplot(fig)
    st.markdown(create_download_link(gpx_route, distance), unsafe_allow_html=True)


