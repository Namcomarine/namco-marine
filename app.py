from datetime import datetime
import email
from email.header import decode_header
import imaplib
import os
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
      if password_input == "namco123":
        st.session_state.authenticated = True
        st.rerun()
      else:
        st.error("❌ Incorrect Password. Please try again.")
  st.stop()


# --- SIDEBAR NAVIGATION ---
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


# --- GMAIL FETCHING FUNCTION ---
def fetch_latest_email_attachment():
  USERNAME = "faisalnamco@gmail.com"  
  PASSWORD = "glup jhez erez mura"  

  try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(USERNAME, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, '(FROM "emailrelay@konectgds.com")')
    if status != "OK":
      return None

    email_ids = messages[0].split()
    if not email_ids:
      return None

    latest_email_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

    for response_part in msg_data:
      if isinstance(response_part, tuple):
        msg = email.message_from_bytes(response_part[1])
        for part in msg.walk():
          if part.get_content_maintype() == "multipart":
            continue
          if part.get("Content-Disposition") is None:
            continue

          filename = part.get_filename()
          if filename and filename.endswith(".txt"):
            filepath = os.path.join(".", filename)
            with open(filepath, "wb") as f:
              f.write(part.get_payload(decode=True))
            mail.logout()
            return filepath
    mail.logout()
  except Exception as e:
    st.sidebar.error(f"Mail sync error: {e}")
  return None


# --- TOP HEADER BAR ---
current_time_str = datetime.now().strftime("%d %b %Y %H:%M")

col_h1, col_h2, col_h3, col_h4 = st.columns([3, 2, 2, 2])
with col_h1:
  st.markdown(
      "### ⚓ NAMCO &nbsp;&nbsp;<span"
      " style='font-size:14px;color:gray;'>Marine Monitoring System</span>",
      unsafe_allow_html=True,
  )
with col_h2:
  st.markdown(
      f"<p style='font-size:12px; color:gray; margin:0;'>LAST"
      f" SYNC<br><b>{current_time_str}</b></p>",
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
  if st.button("🔄 Sync from Gmail", use_container_width=True):
    downloaded_file = fetch_latest_email_attachment()
    if downloaded_file:
      st.success(f"Successfully downloaded: {downloaded_file}")
      st.rerun()
    else:
      st.warning("No new attachment found or check credentials.")

st.markdown("---")


# --- DATA LOADING ---
@st.cache_data
def load_data():
  file_path = "A1_OSD_sn005.txt"
  if os.path.exists(file_path):
    try:
      df = pd.read_csv(file_path, skiprows=4)
      return df
    except:
      pass

  # Fallback Dummy Data
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
  })


df = load_data()


# --- PAGE CONTENT ROUTING ---
if "01 Dashboard" in selected_menu:
  st.markdown(
      "<h2 style='text-align: center;'>NAMCO LIVE MONITORING (Email Integrated"
      " Data)</h2>",
      unsafe_allow_html=True,
  )

  col_d1, col_d2, col_d3 = st.columns(3)

  with col_d1:
    st.markdown(
        f"""
            <div class='custom-card'>
                <h4>D1 &nbsp; 500 m</h4>
                <hr style='border:0.5px solid {border_color};'>
                <p><b>🔵 Surface Water Quality</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>33.09 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>31.53 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>8.26</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>56,224 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon: <b style='color:green;'>0.02 ppb (Normal)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>38.5 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>4.2 m/s</b></div>
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
                <p><b>🔵 Surface Water Quality</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>34.22 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>41.63 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>8.08</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>73,290 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon: <b style='color:green;'>0.01 ppb (Normal)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>39.1 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>5.0 m/s</b></div>
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
                <p><b>🔵 Surface Water Quality</b></p>
                <div style='display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:13px;'>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Temp: <b>0.00 °C</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Salinity: <b>0.00 ppt</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>pH: <b>0.00</b></div>
                    <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Sp.Cond: <b>0 µS</b></div>
                </div>
                <br>
                <p><b>🛢️ Oil Spill Sensor</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:8px; border-radius:5px; font-size:14px;'>
                    Hydrocarbon: <b style='color:gray;'>— (Offline)</b>
                </div>
                <br>
                <p><b>🌤️ Air Meteorology</b></p>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Air Temp: <b>37.4 °C</b></div>
                <div style='background:{card_bg}; border:1px solid {border_color}; padding:6px; border-radius:5px;'>Wind: <b>3.5 m/s</b></div>
            </div>
        """,
        unsafe_allow_html=True,
    )

elif "02 Station Monitor" in selected_menu or "04 Data Table" in selected_menu:
  st.subheader("📋 Station Monitor & Detailed Sensor Records (from Email)")
  st.dataframe(df, use_container_width=True)

elif "03 Plot Studio" in selected_menu:
  st.subheader("📈 Trend Analysis & Plot Studio")
  numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
  if numeric_cols:
    param = st.selectbox("Select Parameter", numeric_cols)
    if "Timestamp" in df.columns:
      fig = px.line(
          df,
          x="Timestamp",
          y=param,
          markers=True,
          title=f"{param} Trend over Time",
      )
      st.plotly_chart(fig, use_container_width=True)
    else:
      st.line_chart(df[param])
  else:
    st.info("No numeric data columns found to plot.")

else:
  st.info(f"You selected: **{selected_menu}**. Module configuration active.")