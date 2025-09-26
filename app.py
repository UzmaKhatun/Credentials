import streamlit as st
import requests
import urllib.parse
from dotenv import load_dotenv
import os
load_dotenv()


# 🔑 Config
N8N_BASE_URL = os.getenv("N8N_BASE_URL")
N8N_API_KEY = os.getenv("N8N_API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Step 1: LinkedIn OAuth URL
AUTH_URL = (
    "https://www.linkedin.com/oauth/v2/authorization?"
    + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "r_liteprofile r_emailaddress w_member_social"
    })
)

# UI
st.title("LinkedIn Credential Setup for n8n")

if "code" not in st.query_params:
    st.write("Click below to login with LinkedIn")
    st.markdown(f"[Login with LinkedIn]({AUTH_URL})")

else:
    code = st.query_params["code"]
    st.success("Authorization code received from LinkedIn ✅")

    # Step 2: Exchange Code for Access Token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    res = requests.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if res.status_code == 200:
        token_data = res.json()
        access_token = token_data.get("access_token")
        st.success("Access Token received from LinkedIn ✅")

        # Step 3: Push Credential to n8n
        cred_payload = {
            "name": "LinkedIn OAuth Credential",
            "type": "linkedinOAuth2Api",
            "data": {
                "clientId": CLIENT_ID,
                "clientSecret": CLIENT_SECRET,
                "accessToken": access_token,
                "refreshToken": ""  # LinkedIn may not always return this
            }
        }

        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }

        n8n_url = f"{N8N_BASE_URL}/api/v1/credentials"
        n8n_res = requests.post(n8n_url, headers=headers, json=cred_payload)

        if n8n_res.status_code == 200:
            st.success("✅ LinkedIn credentials successfully added to n8n")
        else:
            st.error(f"❌ Failed to push credentials: {n8n_res.text}")
    else:
        st.error(f"❌ Failed to get access token: {res.text}")
