import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="AUTOSAR HLD Assistant", layout="wide")

st.title("AUTOSAR HLD Document Analysis Assistant")

tab1, tab2, tab3 = st.tabs(["Upload", "Query", "Documents"])

with tab1:
    st.header("Upload Document")
    project_id = st.text_input("Project ID", value="default_project")
    doc_name = st.text_input("Document Name", value="HLD_v1")
    version = st.text_input("Version", value="1.0")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if st.button("Upload & Process"):
        if uploaded_file and project_id and doc_name and version:
            with st.spinner("Uploading and starting processing..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                data = {
                    "project_id": project_id,
                    "name": doc_name,
                    "version": version
                }
                response = requests.post(f"{API_URL}/documents", files=files, data=data)
                
                if response.status_code == 200:
                    st.success("Document uploaded successfully! It is now processing in the background.")
                else:
                    st.error(f"Error: {response.text}")
        else:
            st.warning("Please fill all fields and select a file.")

with tab2:
    st.header("Ask Questions")
    q_project_id = st.text_input("Project ID for Query", value="default_project")
    query = st.text_area("Question")
    if st.button("Ask"):
        if query and q_project_id:
            with st.spinner("Searching and generating answer..."):
                data = {
                    "project_id": q_project_id,
                    "query": query,
                    "top_k": 5
                }
                try:
                    response = requests.post(f"{API_URL}/query", json=data)
                    if response.status_code == 200:
                        res_json = response.json()
                        st.markdown("### Answer")
                        st.write(res_json["answer"])
                        st.markdown(f"**Limitation Indicator**: {res_json['limitation']}")
                        
                        st.markdown("### Citations")
                        if res_json["citations"]:
                            for c in res_json["citations"]:
                                st.write(f"- Document ID: {c['document_id']}, Page: {c['page_start']}, Chunk ID: {c['chunk_id']}")
                        else:
                            st.write("No citations.")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")

with tab3:
    st.header("Document Status")
    if st.button("Refresh"):
        try:
            response = requests.get(f"{API_URL}/documents")
            if response.status_code == 200:
                docs = response.json()
                if docs:
                    import pandas as pd
                    df = pd.DataFrame(docs)
                    # Select useful columns
                    if not df.empty:
                        df = df[['document_id', 'project_id', 'name', 'version', 'status', 'uploaded_at']]
                        st.dataframe(df)
                else:
                    st.write("No documents found.")
            else:
                st.error("Failed to fetch documents")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")
