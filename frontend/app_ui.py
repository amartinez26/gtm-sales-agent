import streamlit as st
import requests

# Page Config
st.set_page_config(page_title="GTM Sales Agent", page_icon="🤖", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4285F4; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 GTM Sales Agent")
st.write("Analyze strategy documents and generate high-impact sales pitches using **Gemini 3 Flash**.")

with st.sidebar:
    st.header("Project Info")
    st.info("This agent uses a **RAG (Retrieval-Augmented Generation)** architecture to ground AI responses in private strategy data.")
    st.divider()
    st.write("Built by: **Antonio Martinez**")

# User Input Section
query = st.text_area("Enter your strategy question or target company:", 
                     placeholder="e.g., Based on the 2026 STIHL strategy, what are the key talking points for the iMOW line?")

if st.button("Generate Pitch"):
    if query:
        with st.spinner("Analyzing strategy and generating pitch..."):
            try:
                # This calls your Dockerized FastAPI backend
                response = requests.post("http://localhost:8000/pitch", json={"query": query})
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete!")
                    st.markdown("### 📝 Generated Pitch")
                    st.write(result.get("pitch", "No pitch generated."))
                else:
                    st.error(f"Error: The backend returned status code {response.status_code}")
            except Exception as e:
                st.error(f"Could not connect to the backend. Is the Docker container running? (Error: {e})")
    else:
        st.warning("Please enter a query first!")