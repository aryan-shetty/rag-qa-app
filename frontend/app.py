import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG Q&A App", page_icon="📄", layout="centered")

st.title("📄 Document Q&A")
st.caption("Upload one or more PDFs and ask questions about them.")

# --- Indexed files sidebar ---
st.sidebar.header("📚 Indexed Documents")
try:
    files_response = requests.get(f"{API_URL}/files")
    if files_response.status_code == 200:
        indexed_files = files_response.json().get("indexed_files", [])
        if indexed_files:
            for f in indexed_files:
                st.sidebar.markdown(f"✅ {f}")
        else:
            st.sidebar.info("No documents indexed yet.")
except:
    st.sidebar.warning("Backend not reachable.")

# --- Upload section ---
st.subheader("1. Upload your PDF(s)")
uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Indexing {uploaded_file.name}..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            )
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(f"Failed to upload {uploaded_file.name}. Make sure the backend is running.")

# --- Q&A section ---
st.subheader("2. Ask a question")
question = st.text_input("Enter your question here")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question}
        )
    if response.status_code == 200:
        data = response.json()
        st.markdown("### Answer")
        st.write(data["answer"])

        if data.get("citations"):
            st.markdown("### 📎 Citations")
            for cite in data["citations"]:
                st.markdown(f"- **{cite['source']}** — Page {cite['page']}")
    else:
        st.error("Something went wrong. Please try again.")