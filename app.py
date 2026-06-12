import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from folium.plugins import LocateControl
from streamlit_folium import st_folium
import json
import requests

# Настройки страницы
st.set_page_config(layout="wide", page_title="EcoPath AI")

# Адаптивный CSS для мобилок
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { padding: 0 !important; }
        #astana_map { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# Загрузка базы
@st.cache_data
def load_local_addresses():
    try:
        with open("astana_addresses.json", "r", encoding="utf-8") as f:
            return sorted(json.load(f), key=lambda x: (x["street"], x["house"]))
    except: return []

astana_db = load_local_addresses()
address_options = ["-- Выберите адрес --"] + [f"📍 {i['street']}, {i['house']}" for i in astana_db]

# Загрузка графа
@st.cache_data
def load_exact_graph():
    return ox.graph_from_place("Astana, Kazakhstan", network_type="drive")

G = load_exact_graph()

if 'map_clicks' not in st.session_state: st.session_state.map_clicks = []
if 'click_addresses' not in st.session_state: st.session_state.click_addresses = []

def get_address(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        res = requests.get(url, headers={'User-Agent': 'EcoPath_App'}).json()
        return res.get('display_name', '...')
    except: return "..."

@st.fragment
def render_sidebar():
    st.header("Навигатор")
    start = st.selectbox("Старт", address_options, key="s1")
    end = st.selectbox("Финиш", address_options, key="s2")
    
    if st.button("Сброс"):
        st.session_state.map_clicks = []
        st.session_state.click_addresses = []
        st.rerun()

@st.fragment
def render_map():
    m = folium.Map(location=[51.1282, 71.4305], zoom_start=13)
    folium.TileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", attr="OSM").add_to(m)
    
    if st.session_state.map_clicks:
        for i, pos in enumerate(st.session_state.map_clicks):
            folium.Marker(pos, icon=folium.Icon(color="green" if i==0 else "red")).add_to(m)
            
    map_data = st_folium(m, width='100%', height=450, key="astana_map")
    
    if map_data.get("last_clicked"):
        c = map_data["last_clicked"]
        if len(st.session_state.map_clicks) < 2:
            st.session_state.map_clicks.append((c["lat"], c["lng"]))
            st.rerun()

with st.sidebar: render_sidebar()
render_map()