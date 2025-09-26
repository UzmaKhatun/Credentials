# n8n_imap_credential.py
import streamlit as st
import requests
import json
import imaplib
from urllib.parse import urljoin

st.set_page_config(page_title="n8n IMAP credential creator", layout="centered")
st.title("▶ Create IMAP (Email Trigger) credential in n8n")

st.info("This app will POST an IMAP credential to your n8n instance using your n8n API key (X-N8N-API-KEY).")

# --- n8n connection ---
st.header("n8n connection")
n8n_base = st.text_input("n8n base URL (include protocol)", value="http://localhost:5678")
api_key = st.text_input("n8n API Key (X-N8N-API-KEY)", type="password")

# --- IMAP inputs ---
st.header("IMAP (Email Trigger) details")
cred_name = st.text_input("Credential name (how it'll appear in n8n)", value="User IMAP Credential")
email_user = st.text_input("Email address / username (e.g. user@example.com)")
email_pass = st.text_input("IMAP password / app-password", type="password")
host = st.text_input("IMAP host", value="imap.gmail.com")
port = st.number_input("Port", value=993)
use_ssl = st.checkbox("Use SSL/TLS", value=True)
allow_self_signed = st.checkbox("Allow self-signed certificates (careful!)", value=False)

st.write("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Fetch IMAP credential schema from n8n"):
        if not api_key or not n8n_base:
            st.error("Enter n8n base URL and API key first.")
        else:
            schema_urls = [
                urljoin(n8n_base.rstrip("/") + "/", "api/v1/credentials/schema/imap"),
                urljoin(n8n_base.rstrip("/") + "/", "rest/credentials/schema/imap"),
            ]
            schema = None
            headers = {"X-N8N-API-KEY": api_key}
            for u in schema_urls:
                try:
                    r = requests.get(u, headers=headers, timeout=10)
                except Exception as e:
                    continue
                if r.status_code == 200:
                    schema = r.json()
                    st.success(f"Schema fetched from {u}")
                    st.json(schema)
                    break
            if not schema:
                st.error("Could not fetch schema. Check URL and API key; try both /api/v1/... and /rest/....")

with col2:
    if st.button("Test IMAP connection (from this machine)"):
        if not (host and email_user and email_pass):
            st.error("Provide host, username and password to test.")
        else:
            try:
                if use_ssl:
                    imap = imaplib.IMAP4_SSL(host, int(port))
                else:
                    imap = imaplib.IMAP4(host, int(port))
                imap.login(email_user, email_pass)
                imap.logout()
                st.success("✅ IMAP login successful from this machine.")
            except Exception as e:
                st.error(f"IMAP connection failed: {e}")

st.write("---")

# --- Create credential in n8n ---
if st.button("Create IMAP credential in n8n"):
    if not api_key or not n8n_base:
        st.error("Enter n8n base URL and API key first.")
    elif not (email_user and email_pass):
        st.error("Enter the email username and password.")
    else:
        headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
        payload = {
            "name": cred_name,
            "type": "imap",   # IMAP credential type in n8n
            "typeVersion": 1,
            "data": {
                "user": email_user,
                "password": email_pass,
                "host": host,
                "port": int(port),
                "secure": bool(use_ssl),
                "allowUnauthorizedCerts": bool(allow_self_signed),
            }
        }

        # Try common endpoints in order
        endpoints = [
            urljoin(n8n_base.rstrip("/") + "/", "api/v1/credentials"),
            urljoin(n8n_base.rstrip("/") + "/", "rest/credentials"),
        ]

        resp = None
        for ep in endpoints:
            try:
                r = requests.post(ep, headers=headers, json=payload, timeout=15)
            except Exception as e:
                st.warning(f"Request to {ep} failed: {e}")
                continue

            if r.status_code in (200, 201):
                try:
                    resp_json = r.json()
                except Exception:
                    resp_json = r.text
                st.success(f"Credential created at {ep} ✅")
                st.write("Response:")
                st.json(resp_json)
                resp = r
                break
            else:
                st.error(f"Failed at {ep} — status {r.status_code}: {r.text}")

        if not resp:
            st.error("All endpoints failed. Check the API key, base URL, and that the API is enabled on n8n.")
