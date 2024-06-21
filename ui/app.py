import base64

import streamlit as st

from utils import create_routes, get_kml_destinations

st.title('GPX Generator')

start = st.text_input(
  "Start", 
  value="1.3097970339490435, 103.89455470068188"
)

input_choice = st.selectbox(
  "Destination", 
  [
    "Enter location",
    "Upload KML file", 
  ],
)

destinations = []
if input_choice == "Upload KML file":
  kml_file = st.file_uploader(
    "Destinations", 
    type=["kml"], 
    accept_multiple_files=False,
  )
  if kml_file:
    destinations = get_kml_destinations(kml_file)
else:
  destination = st.text_input(
    "Destination", 
    value="1.282100743659439, 103.85441068499448"
  )
  stop_lat, stop_lng = map(float, destination.split(","))
  destinations.append(["Route", stop_lat, stop_lng])

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
    start_lat, start_lng = map(float, start.split(","))
    routes = create_routes(
      start_lat, 
      start_lng,
      destinations,
    )
    for name, fig, gpx in routes:
      st.pyplot(fig)
      st.markdown(create_download_link(gpx, name), unsafe_allow_html=True)


