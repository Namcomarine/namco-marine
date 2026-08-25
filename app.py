from datetime import datetime
import email
from email.header import decode_header
import imaplib
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="NAMCO Marine Monitoring System", page_icon="⚓", layout="wide"
)

# --- AUTO REFRESH (Every 5 Minutes / 300,000 milliseconds using JavaScript) ---
components.html(
    """
    <script>
        setTimeout(function(){
            window.parent.location.reload();
        }, 300000);
    </script>
""",
    height=0,
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
    </style>
""",
    unsafe_allow_html=True,
)


# --- PARSE CUSTOM TXT DATA ---
def parse_custom_txt(file_path):
  data = {
      "Temp °C": "36.2270",
      "Sp. Cond S/m": "7.26286",
      "Salinity PSU": "39.6269",
      "pH": "8.39",
      "Turbidity NTU": "10.459",
      "DO mg/L": "4.937",
      "Chlorophyll": "0.359",
      "Oil Avg ppm": "3.193315",
      "Oil Max ppm": "3.23737",
      "Air Temp °C": "32.9",
      "Barometer mbar": "1002.6",
      "Wind Speed m/s": "0.7",
      "Wind Dir °": "148.4",
      "Battery V": "12.92989",
      "Timestamp": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
  }
  try:
    if os.path.exists(file_path):
      with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
          parts = [p.strip() for p in line.strip().split(",")]
          if len(parts) > 0:
            if parts[0] == "$WATQM":
              if len(parts) > 2:
                data["Temp °C"] = parts[2]
              if len(parts) > 4:
                data["Sp. Cond S/m"] = parts[4]
              if len(parts) > 6:
                data["DO mg/L"] = parts[6]
              if len(parts) > 8:
                data["pH"] = parts[8]
              if len(parts) > 10:
                data["Chlorophyll"] = parts[10]
              if len(parts) > 12:
                data["Turbidity NTU"] = parts[12]
              if len(parts) > 18:
                data["Salinity PSU"] = parts[18]

              for i in range(len(parts) - 1):
                if "/" in parts[i] and ":" in parts[i + 1]:
                  data["Timestamp"] = parts[i] + " " + parts[i + 1]

            elif parts[0] == "$OILSD":
              if len(parts) > 2:
                data["Oil Avg ppm"] = parts[2]
              if len(parts) > 4:
                data["Oil Max ppm"] = parts[4]

            elif parts[0] == "$METEO":
              if len(parts) > 2:
                data["Barometer mbar"] = parts[2]
              if len(parts) > 4:
                data["Air Temp °C"] = parts[4]
              if len(parts) > 6:
                data["Wind Dir °"] = parts[6]
              if len(parts) > 8:
                data["Wind Speed m/s"] = parts[8]

            elif parts[0] == "$HEALTH":
              if len(parts) > 2:
                data["Battery V"] = parts[2]
  except Exception as e:
    pass
  return data


# --- HISTORY MANAGEMENT (CSV APPEND & CLEANUP) ---
HISTORY_FILE = "namco_history_data.csv"


def append_to_history(new_data_dict):
  new_df = pd.DataFrame([new_data_dict])
  if os.path.exists(HISTORY_FILE):
    try:
      existing_df = pd.read_csv(HISTORY_FILE)
      # ഡ്യൂപ്ലിക്കേറ്റ് ഒഴിവാക്കി പുതിയത് മാത്രം ചേർക്കുക
      if (
          "Timestamp" in existing_df.columns
          and new_data_dict["Timestamp"] in existing_df["Timestamp"].values
      ):
        return existing_df
      combined_df = pd.concat([existing_df, new_df], ignore_index=True)
      # ടൈംസ്റ്റാമ്പ് പ്രകാരം സോർട്ട് ചെയ്ത് ഡ്യൂപ്ലിക്കേറ്റ് കളയുക
      combined_df.drop_duplicates(subset=["Timestamp"], keep="last", inplace=True)
      combined_df.to_csv(HISTORY_FILE, index=False)
      return combined_df
    except:
      new_df.to_csv(HISTORY_FILE, index=False)
      return new_df
  else:
    new_df.to_csv(HISTORY_FILE, index=False)
    return new_df


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
    pass
  return None


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
      parsed_new = parse_custom_txt(downloaded_file)
      df = append_to_history(parsed_new)
      st.success("Successfully synced from Gmail!")
      st.rerun()
    else:
      st.warning("No new attachment found.")

st.markdown("---")


# --- DATA LOADING & INITIALIZATION ---
# നിലവിലുള്ള ഹിസ്റ്ററി ഫയൽ ലോഡ് ചെയ്യുക, അല്ലെങ്കിൽ പുതിയത് ഉണ്ടാക്കുക
if os.path.exists(HISTORY_FILE):
  df = pd.read_csv(HISTORY_FILE)
else:
  file_path = "A1_OSD_sn005.txt"
  initial_data = (
      parse_custom_txt(file_path) if os.path.exists(file_path) else {}
  )
  df = pd.DataFrame([initial_data])
  df.to_csv(HISTORY_FILE, index=False)

# ഓട്ടോമാറ്റിക് ആയി ജിമെയിൽ അറ്റാച്ച്മെന്റ് ചെക്ക് ചെയ്ത് ആഡ് ചെയ്യുക
downloaded_file = fetch_latest_email_attachment()
if downloaded_file:
  parsed_new = parse_custom_txt(downloaded_file)
  df = append_to_history(parsed_new)

latest_data = df.iloc[-1].to_dict() if not df.empty else {}


# --- PAGE CONTENT ROUTING ---
if "01 Dashboard" in selected_menu:
  st.markdown(
      "<h2 style='text-align: center;'>NAMCO LIVE MONITORING (Auto-Refreshing"
      " Data)</h2>",
      unsafe_allow_html=True,
  )

  _, col_center, _ = st.columns([1, 2, 1])

  with col_center:
    st.markdown(
        f"### SN 005 - Al Rayis &nbsp;&nbsp;|&nbsp;&nbsp; <span"
        f" style='font-size:14px; color:gray;'>🕒"
        f" {latest_data.get('Timestamp', '')}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("**🔵 Surface Water Quality**")
    m1, m2 = st.columns(2)
    with m1:
      st.info(f"Temp: **{latest_data.get('Temp °C')} °C**")
      st.info(f"pH: **{latest_data.get('pH')}**")
      st.info(f"Turbidity: **{latest_data.get('Turbidity NTU')} NTU**")
      st.info(f"Chlorophyll: **{latest_data.get('Chlorophyll')}**")
    with m2:
      st.info(f"Salinity: **{latest_data.get('Salinity PSU')} PSU**")
      st.info(f"Sp.Cond: **{latest_data.get('Sp. Cond S/m')} S/m**")
      st.info(f"DO: **{latest_data.get('DO mg/L')} mg/L**")

    st.markdown("**🛢️ Oil Spill Sensor**")
    oil_col1, oil_col2 = st.columns(2)
    with oil_col1:
      st.success(
          f"Average: **{latest_data.get('Oil Avg ppm')} ppm (Normal)**"
      )
    with oil_col2:
      st.success(
          f"Maximum: **{latest_data.get('Oil Max ppm')} ppm (Normal)**"
      )

    st.markdown("**🌤️ Air Meteorology & System Health**")
    m3, m4 = st.columns(2)
    with m3:
      st.info(f"Air Temp: **{latest_data.get('Air Temp °C')} °C**")
      st.info(f"Wind Speed: **{latest_data.get('Wind Speed m/s')} m/s**")
    with m4:
      st.info(f"Wind Direction: **{latest_data.get('Wind Dir °')}°**")
      st.info(f"Pressure: **{latest_data.get('Barometer mbar')} mbar**")
      st.info(f"Battery: **{latest_data.get('Battery V')} V**")

elif "02 Station Monitor" in selected_menu or "04 Data Table" in selected_menu:
  st.subheader("📋 Station Monitor & Detailed Sensor Records (SN 005 - Al Rayis)")
  st.dataframe(df, use_container_width=True)

elif "03 Plot Studio" in selected_menu:
  st.subheader("📈 Trend Analysis & Plot Studio")
  numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
  if numeric_cols:
    param = st.selectbox("Select Parameter", numeric_cols)
    st.line_chart(df, y=param)
  else:
    st.info("No numeric data columns found to plot.")

else:
  st.info(f"You selected: **{selected_menu}**. Module configuration active.")