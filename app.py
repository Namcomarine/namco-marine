import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="NAMCO Marine Monitoring System", page_icon="⚓", layout="wide"
)

# --- THEME SELECTION & STYLING ---
if "theme" not in st.session_state:
  st.session_state.theme = "Light"

# Colors based on theme
if st.session_state.theme == "Light":
  bg_color = "#f8fafc"
  card_bg = "#ffffff"
  text_color = "#0f172a"
  sidebar_bg = "#ffffff"
  border_color = "#e2e8f0"
else:
  bg_color = "#0f172a"
  card_bg = "#1e293b"
  text_color = "#f8fafc"
  sidebar_bg = "#0f172a"
  border_color = "#334155"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .custom-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- PASSWORD AUTHENTICATION SECTION ---
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  try:
    col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
    with col_l2:
      st.image("Picture1-Picsart-BackgroundRemover.png", width=120)
  except:
    pass

  st.markdown(
      "<h2 style='text-align: center; color: #0284c7;'>⚓ NAMCO Marine"
      " Monitoring System</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #64748b;'>Please enter your"
      " password to access the system</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1, 1])
  with col2:
    password_input = st.text_input("Password", type="password")
    if st.button("Sign In", use_container_width=True):
      if password_input == "namco123":  # ഇവിടെ പാസ്‌വേഡ് മാറ്റാം
        st.session_state.authenticated = True
        st.rerun()
      else:
        st.error("❌ Incorrect Password. Please try again.")
  st.stop()


# --- SIDEBAR NAVIGATION (With Uploaded Logo) ---
with st.sidebar:
  try:
    st.image("Picture1-Picsart-BackgroundRemover.png", width=140)
  except:
    pass

  st.markdown(
      "<p"
      " style='color:gray; font-size:11px; margin-top:-5px;'>NAMCO Marine"
      " Monitoring System</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  st.markdown("**MONITORING**")

  selected_menu = st.radio(
      "Navigation",
      [
          "01 Dashboard",
          "02 Station Monitor",
          "03 Plot Studio",
          "04 Data Table",
          "05 QC & Availability",
          "06 Alarm Centre",
          "07 Map & Forecast",
          "08 Settings",
      ],
      label_visibility="collapsed",
  )

  st.markdown("---")
  st.markdown(
      "<div style='font-size:12px; color:gray;'>Preview"
      " User<br><b>Administrator</b></div>",
      unsafe_allow_html=True,
  )
  if st.button("🚪 SIGN OUT", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()


# --- TOP HEADER BAR ---
col_h1, col_h2, col_h3, col_h4 = st.columns([3, 2, 2, 2])
with col_h1:
  st.markdown(
      "### ⚓ NAMCO &nbsp;&nbsp;<span"
      " style='font-size:14px;color:gray;'>Marine Monitoring System</span>",
      unsafe_allow_html=True,
  )
with col_h2:
  st.markdown(
      "<p style='font-size:12px; color:gray; margin:0;'>LAST"
      " SYNC<br><b>25 Aug 2026 13:18</b></p>",
      unsafe_allow_html=True,
  )
with col_h3:
  theme_label = (
      "🌙 Dark theme" if st.session_state.theme == "Light" else "☀️ Light theme"
  )
  if st.button(theme_label):
    st.session_state.theme = (
        "Dark" if st.session_state.theme == "Light" else "Light"
    )
    st.rerun()
with col_h4:
  if st.button("🔄 Refresh Data", use_container_width=True):
    st.success("Data updated!")

st.markdown("---")


# --- DUMMY DATA FOR STATIONS (Including Water Quality, Oil Spill, Air Met) ---
@st.cache_data
def load_data():
  return pd.DataFrame({
      "Timestamp": [
          "28/05/2026 04:00 PM",
          "28/05/2026 03:30 PM",
          "28/05/2026 03:00 PM",
          "28/05/2026 02:30 PM",
          "28/05/2026 02:00 PM",
      ],
      "Temp °C": [33.1, 33.1, 33.0, 33.2, 33.3],
      "Sp. Cond µS": [56224.0, 56732.5, 56417.9, 55879.0, 55944.5],
      "Salinity": [31.5, 31.9, 31.7, 31.1, 31.2],
      "pH": [8.26, 8.27, 8.30, 8.28, 8.29],
      "DO mg/L": [10.89, 10.81, 10.73, 10.54, 10.38],
      "Oil Spill (ppb)": [0.02, 0.01, 0.00, 0.03, 0.01],
      "Air Temp °C": [38.5, 38.8, 39.0, 38.6, 38.2],
      "Wind Speed m/s": [4.2, 4.5, 3.8, 5.1, 4.0],
      "Wind Dir °": [140, 145, 135, 150, 142],
  })


df = load_data()


# --- PAGE CONTENT ROUTING BASED ON SIDEBAR ---
if "01 Dashboard" in selected_menu:
  st.markdown(
      "<h2 style='text-align: center;'>NAMCO LIVE MONITORING (Water Quality,"
      " Oil Spill & Air Met)</h2>",
      unsafe_allow_html=True,
  )

  col_d1, col_d2, col_d3 = st.columns(3)

  # Station 1 Card (500m)
  with col_d1:
    st.markdown(
        f"""
            <div class='custom-card'>
                <h4>D1 &nbsp; 500 m</h4>
                <hr style='border:0.5px solid {border_color};'>
                <p><b>🔵 Surface Water Quality</b> <span style='float:right; font-size:12px; color:gray;'>28 May 2026</span></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>33.09 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>31.53 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>8.26</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>56,224 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon Concentration: <b style='color:green;'>0.02 ppb (Normal)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>38.5 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>4.2 m/s (140°)</b></div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col_d2:
    st.markdown(
        f"""
            <div class='custom-card'>
                <h4>D2 &nbsp; 1000 m</h4>
                <hr style='border:0.5px solid {border_color};'>
                <p><b>🔵 Surface Water Quality</b> <span style='float:right; font-size:12px; color:gray;'>08 Jun 2026</span></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>34.22 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>41.63 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>8.08</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>73,290 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon Concentration: <b style='color:green;'>0.01 ppb (Normal)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>39.1 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>5.0 m/s (145°)</b></div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  with col_d3:
    st.markdown(
        f"""
            <div class='custom-card'>
                <h4>D3 &nbsp; 2000 m</h4>
                <hr style='border:0.5px solid {border_color};'>
                <p><b>🔵 Surface Water Quality</b> <span style='float:right; font-size:12px; color:gray;'>25 May 2026</span></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>0.00 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>0.00 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>0.00</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>0 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon Concentration: <b style='color:gray;'>— (Offline)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>37.4 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>3.5 m/s (130°)</b></div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

elif "02 Station Monitor" in selected_menu or "04 Data Table" in selected_menu:
  st.subheader("📋 Station Monitor & Detailed Sensor Records")
  st.dataframe(df, use_container_width=True)

elif "03 Plot Studio" in selected_menu:
  st.subheader("📈 Trend Analysis & Plot Studio")
  param = st.selectbox(
      "Select Parameter",
      [
          "Temp °C",
          "Sp. Cond µS",
          "Salinity",
          "pH",
          "Oil Spill (ppb)",
          "Air Temp °C",
          "Wind Speed m/s",
      ],
  )
  fig = px.line(
      df,
      x="Timestamp",
      y=param,
      markers=True,
      title=f"{param} Trend over Time",
  )
  st.plotly_chart(fig, use_container_width=True)

else:
  st.info(f"You selected: **{selected_menu}**. Module configuration active.")