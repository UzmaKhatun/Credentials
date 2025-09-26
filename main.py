import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()

# 🔑 Config
N8N_BASE_URL = os.getenv("N8N_BASE_URL")
N8N_API_KEY = os.getenv("N8N_API_KEY")


# UI
st.title("Connect LinkedIn via n8n")

st.write(
    """
    Click the button below to connect your LinkedIn account.
    This will open n8n's LinkedIn OAuth2 flow in a new tab.
    """
)

# n8n OAuth2 URL for LinkedIn
# This URL is the credential creation endpoint in n8n
linkedin_oauth_url = f"{N8N_BASE_URL}/rest/oauth2-credential/linkedinOAuth2Api?apiKey={N8N_API_KEY}"

st.markdown(f"[Connect LinkedIn]({linkedin_oauth_url})")
st.info(
    """
    After completing the login in LinkedIn:
    1. n8n will automatically store your access token.
    2. You can now use the LinkedIn credential in your n8n workflows.
    """
)
