import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="PRAMAAN", layout="wide")

st.title("PRAMAAN: Cryptographic Attribution")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Sender", "Recipient", "Investigator", "Attack Lab", "Ledger Explorer"])

API_BASE = "http://localhost:8000"

if page == "Dashboard":
    st.header("System Status")
    col1, col2, col3 = st.columns(3)
    col1.metric("Fabric Status", "Online (SmartBFT)")
    col2.metric("PQC Status", "Active (ML-KEM/ML-DSA)")
    col3.metric("Air-gap Status", "Isolated")

elif page == "Sender":
    st.header("Sender / Admin")
    uploaded_file = st.file_uploader("Upload PDF to Encrypt", type=["pdf"])
    if uploaded_file and st.button("Encrypt Once"):
        with st.spinner("Encrypting with AES-256-GCM..."):
            res = requests.post(f"{API_BASE}/documents/encrypt", files={"file": uploaded_file.getvalue()})
            if res.status_code == 200:
                data = res.json()
                st.success(data["message"])
                st.json(data)

elif page == "Recipient":
    st.header("Recipient Portal")
    st.info("Authenticate and request decryption key.")
    # Mock Recipient actions
    st.button("Request Decrypt (Sign with ML-DSA)")
    st.button("Decrypt & Watermark (Layer A, B, C)")
    
elif page == "Investigator":
    st.header("Forensic Investigator")
    leaked_file = st.file_uploader("Upload Leaked PDF", type=["pdf"])
    if leaked_file and st.button("Extract Fingerprint & Verify"):
        with st.spinner("Analyzing..."):
            res = requests.post(f"{API_BASE}/forensics/verify", files={"file": leaked_file.getvalue()})
            if res.status_code == 200:
                st.json(res.json())

elif page == "Attack Lab":
    st.header("Attack Resilience Lab")
    st.button("Run Attack Suite (Screenshot, JPEG, Print-Scan)")

elif page == "Ledger Explorer":
    st.header("Fabric Ledger Explorer")
    st.info("View immutable provenance records.")
