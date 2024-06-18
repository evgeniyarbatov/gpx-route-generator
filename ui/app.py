import base64

import streamlit as st

from utils import create_routes

st.title('GPX Generator')

kml_file = st.file_uploader(
  "Destinations", 
  type=["kml"], 
  accept_multiple_files=False,
)

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

def create_download_link(gpx, name):
    b64 = base64.b64encode(gpx.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{name}.gpx"><button>{name}.gpx</button></a>'
    return href

if create:
  if not kml_file:
    st.info('Upload KML file')
  else:
    routes = create_routes(
      start_lat, 
      start_lng,
      kml_file
    )
    for name, fig, gpx in routes:
      st.pyplot(fig)
      st.markdown(create_download_link(gpx, name), unsafe_allow_html=True)


