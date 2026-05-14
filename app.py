from helpers import *
import streamlit as st
import folium 
from streamlit_folium import folium_static

# Example URL to fetch bike share data 
station_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
latlonurl = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'



st.title("Toronto Bike Share Station Status")  # Set the title of the Streamlit app
st.markdown("This app shows the current status of bike share stations in Toronto. It uses data from the Toronto Bike Share API and displays it on an interactive map.")  # Add a description
#fetch data for initial visualisation
data_df = query_station_status(station_url)  # Get station status data
latlon_df = get_station_latlon(latlonurl)  # Get station latitude and longitude data
data = join_latlon(data_df,latlon_df)
data = data.dropna(subset=['lat', 'lon'])
data = data.reset_index(drop=True) 
# st.dataframe(data)


col1,col2,col3 = st.columns(3)
with col1:

    st.metric(label='Bikes available now', value=sum(data['num_bikes_available']))
    st.metric(label='E-Bikes available now', value=sum(data['ebike']))

with col2:

    st.metric(label='Stations w Available Bikes',value=len(data[data['num_bikes_available']>0]))
    st.metric(label='Stations w Available E-Bikes',value=len(data[data['ebike']>0]))    

with col3:
    st.metric(label='Stations w Empty Docks',value=len(data[data['num_docks_available']>0]))  

# Initialize variables for user input and state
iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False
input_bike_modes = []

with st.sidebar:
    bike_method = st.selectbox('Are you looking to rent or return a bike?',('Rent','Return'))
    if bike_method == 'Rent':
        st.multiselect('What kind of bikes are you looking to rent?',
                       ['ebike','mechanical'])
        st.header('Where are you located?')
        input_street = st.text_input('Street','')
        input_city = st.text_input('City','Toronto')
        input_country = st.text_input('Country','Canada')
        drive = st.checkbox("I'm driving there") # gives true or false
        findmeabike = st.button('Find me a bike!',type = 'primary')
        if findmeabike:
            if input_street !=" ":
                iamhere = geocode(input_street+" "+input_city+" "+input_country)  # Geocode the input address
                if iamhere == " ":
                   st.subheader(':red[Input address not valid!]')

            else:
                st.subheader(':red[Input address not valid!]')
    elif bike_method=='Return':
        st.subheader('Where are you located?')
        input_street = st.text_input('Street','')
        input_city = st.text_input('City','Toronto')
        input_country = st.text_input('Country','Canada')
        findmeadock = st.button('Find me a dock!',type = 'primary')
        if findmeadock:
            if input_street !=" ":
                iamhere_return = geocode(input_street+" "+input_city+" "+input_country)  # Geocode the input address
                if iamhere_return == " ":
                   st.subheader(':red[Input address not valid!]')

            else:
                st.subheader(':red[Input address not valid!]')

if bike_method == 'Rent' and findmeabike == False:
    # initial map
    # create a map centered around Toronto
    center = [43.65107, -79.347015] # coordinates for Toronto
    m = folium.Map(location=center, zoom_start=13,tiles='cartodbpositron') # create a map with a grey background

    # Add circle markers to the map for each station
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['num_bikes_available'])  # Get the color based on bike availability
        folium.CircleMarker(
            location=[row['lat'], row['lon']],  # Set the location of the marker
            radius=2,  # Set the radius of the marker
            color=marker_color,  # Set the color of the marker
            fill=True,  # Fill the marker with color
            fill_color=marker_color,  # Set the fill color to be the same as the border color
            fill_opacity=0.7,  # Set the opacity of the fill
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                            f"Mechanical Bikes Available: {row['mechanical']}<br>"
                            f"eBike Available: {row['ebike']}", max_width=300)  # Add a popup with station information
        ).add_to(m)  # Add the marker to the map

    folium_static(m)  # Display the map in the Streamlit app

if bike_method == 'Return' and findmeadock == False:
    # initial map
    # create a map centered around Toronto
    center = [43.65107, -79.347015] # coordinates for Toronto
    m = folium.Map(location=center, zoom_start=13,tiles='cartodbpositron') # create a map with a grey background

    # Add circle markers to the map for each station
    for _, row in data.iterrows():
        marker_color = get_marker_color(row['num_bikes_available'])  # Get the color based on bike availability
        folium.CircleMarker(
            location=[row['lat'], row['lon']],  # Set the location of the marker
            radius=2,  # Set the radius of the marker
            color=marker_color,  # Set the color of the marker
            fill=True,  # Fill the marker with color
            fill_color=marker_color,  # Set the fill color to be the same as the border color
            fill_opacity=0.7,  # Set the opacity of the fill
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                            f"Mechanical Bikes Available: {row['mechanical']}<br>"
                            f"eBike Available: {row['ebike']}", max_width=300)  # Add a popup with station information
        ).add_to(m)  # Add the marker to the map

    folium_static(m)  # Display the map in the Streamlit app

# Logic for finding a bike
if findmeabike:
    if input_street != "":
        if iamhere != "":
            chosen_station = get_bike_availability(iamhere, data, input_bike_modes)  # Get bike availability (id, lat, lon)
            center = iamhere  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(row['num_bikes_available'])  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                       f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                       f"Mechanical Bike Available: {row['mechanical']}<br>"
                                       f"eBike Available: {row['ebike']}", max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Rent your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time

# Logic for finding a dock
if findmeadock:
    if input_street != "":
        if iamhere_return != "":
            chosen_station = get_dock_availability(iamhere_return, data)  # Get dock availability (id, lat, lon)
            center = iamhere_return  # Center the map on user's location
            m1 = folium.Map(location=center, zoom_start=16, tiles='cartodbpositron')  # Create a detailed map
            for _, row in data.iterrows():
                marker_color = get_marker_color(row['num_bikes_available'])  # Determine marker color based on bikes available
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                       f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                       f"Mechanical Bike Available: {row['mechanical']}<br>"
                                       f"eBike Available: {row['ebike']}", max_width=300)
                ).add_to(m1)
            folium.Marker(
                location=iamhere_return,
                popup="You are here.",
                icon=folium.Icon(color="blue", icon="person", prefix="fa")
            ).add_to(m1)
            folium.Marker(location=(chosen_station[1], chosen_station[2]),
                          popup="Return your bike here.",
                          icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                          ).add_to(m1)
            coordinates, duration = run_osrm(chosen_station, iamhere_return)  # Get route coordinates and duration
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="it'll take you {} to get here.".format(duration),
            ).add_to(m1)
            folium_static(m1)  # Display the map in the Streamlit app
            with col3:
                st.metric(label=":green[Travel Time (min)]", value=duration)  # Display travel time