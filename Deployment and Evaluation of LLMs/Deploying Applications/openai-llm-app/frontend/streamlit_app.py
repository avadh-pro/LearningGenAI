"""Streamlit frontend for the customer-support classifier."""

import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 45

st.set_page_config(page_title="Support Triage", page_icon="💬", layout="centered")
st.title("Customer Support Triage")
st.caption("OpenAI Responses API · Structured customer-support output")

message = st.text_area(
    "Customer message",
    height=160,
    max_chars=4000,
    placeholder="My order was due yesterday, but it has not arrived.",
)

if st.button("Generate response", type="primary", use_container_width=True):
    if not message.strip():
        st.warning("Enter a customer message first.")
    else:
        try:
            with st.spinner("Classifying the request..."):
                response = requests.post(
                    f"{API_BASE_URL}/generate",
                    json={"message": message},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            if response.ok:
                result = response.json()
                col1, col2, col3 = st.columns(3)
                col1.metric("Category", result["category"])
                col2.metric("Intent", result["intent"])
                col3.metric("Priority", result["priority"])
                st.subheader("Suggested reply")
                st.write(result["reply"])
                with st.expander("Structured JSON"):
                    st.json(result)
            else:
                detail = response.json().get("detail", response.text)
                st.error(f"API error ({response.status_code}): {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")

st.divider()
st.caption(f"Backend: {API_BASE_URL}")
