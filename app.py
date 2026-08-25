import os
import imaplib
import email
from email.header import decode_header
import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="NAMCO Marine Monitoring System", layout="wide")
st.title("🌊 NAMCO Marine Monitoring System")

DATA_FILE = "buoy_data.csv"

# 2. Function to process text content from email body or attachments
def parse_buoy_data_from_text(text_content, all_rows):
    lines = text_content.strip().split('\n')
    for line in lines:
        if line.startswith("$") and "," in line:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                table_type = parts[0].replace("$", "")
                sensor_id = parts[1]
                
                # Extract timestamp if present in standard formats (e.g., YYYY/M/D or similar)
                timestamp = "N/A"
                for p in parts:
                    if "/" in p and ":" in p:
                        timestamp = p
                        break
                
                row_data = {
                    "Timestamp": timestamp,
                    "Table_Type": table_type,
                    "Sensor_ID": sensor_id,
                    "Raw_Data": line
                }
                
                # Dynamically map parameters and values
                param_idx = 1
                i = 2
                while i < len(parts) - 1:
                    val_str = parts[i]
                    # Check if next part is a unit
                    unit_str = ""
                    if i + 1 < len(parts) and not parts[i+1].replace('.', '', 1).isdigit() and "/" not in parts[i+1] and ":" not in parts[i+1]:
                        unit_str = parts[i+1]
                        i += 1 # skip unit in next iteration
                    
                    try:
                        val_float = float(val_str)
                        col_name = f"{table_type}_{param_idx} ({unit_str})" if unit_str else f"{table_type}_{param_idx}"
                        row_data[col_name] = val_float
                        param_idx += 1
                    except ValueError:
                        pass
                    i += 1
                
                all_rows.append(row_data)

# 3. Function to fetch emails and read .txt attachments / body
def fetch_latest_emails():
    IMAP_SERVER = "imap.gmail.com"
    EMAIL_USER = "faisalnamco@gmail.com"
    EMAIL_PASS = "raggzvkhkzftkwlx"

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(FROM "emailrelay@konectgds.com")')
        
        if status == 'OK':
            new_rows = []
            for num in messages[0].split():
                res, msg = mail.fetch(num, '(RFC822)')
                if res == 'OK':
                    for response in msg:
                        if isinstance(response, tuple):
                            msg_obj = email.message_from_bytes(response[1])
                            
                            # Check body
                            body = ""
                            if msg_obj.is_multipart():
                                for part in msg_obj.walk():
                                    content_disposition = str(part.get("Content-Disposition"))
                                    # Check if it's an attachment (.txt file)
                                    if "attachment" in content_disposition or part.get_filename():
                                        filename = part.get_filename()
                                        if filename and filename.endswith('.txt'):
                                            attachment_data = part.get_payload(decode=True)
                                            if attachment_data:
                                                txt_content = attachment_data.decode('utf-8', errors='ignore')
                                                parse_buoy_data_from_text(txt_content, new_rows)
                                    elif part.get_content_type() == "text/plain":
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body = payload.decode('utf-8', errors='ignore')
                            else:
                                payload = msg_obj.get_payload(decode=True)
                                if payload:
                                    body = payload.decode('utf-8', errors='ignore')
                            
                            if body:
                                parse_buoy_data_from_text(body, new_rows)

            if new_rows:
                df_new = pd.DataFrame(new_rows)
                if os.path.exists(DATA_FILE):
                    df_old = pd.read_csv(DATA_FILE)
                    df_combined = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates().reset_index(drop=True)
                else:
                    df_combined = df_new
                df_combined.to_csv(DATA_FILE, index=False)
                return True
        mail.logout()
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
    return False

# 4. Sidebar / Update Button
if st.button("🔄 Check New Emails & Update All Data"):
    with st.spinner("Fetching text files & logs from email..."):
        success = fetch_latest_emails()
        if success:
            st.success("All attachment data fetched successfully!")
        else:
            st.info("No new data or already up to date.")

# 5. Load and Display All Data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    
    st.subheader("📊 Complete Buoy Sensor Records (From Email Text/Attachments)")
    st.dataframe(df, use_container_width=True)

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if len(numeric_cols) >= 1:
        st.subheader("📈 Sensor Parameters Trend Analysis")
        selected_param = st.selectbox("Select Parameter to Plot:", numeric_cols)
        
        fig = px.line(df, x="Timestamp" if "Timestamp" in df.columns else df.index, y=selected_param, markers=True)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data file found. Click the button above to fetch records from your email.")