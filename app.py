import streamlit as st
from rdflib import Graph
from validator import validate_graph
from queries.construct_query import CONSTRUCT_QUERY
from utils.graph_loader import load_shacl_graph_from_sparql, parse_graph_from_file
from utils.result_parser import parse_validation_results
import pandas as pd

st.set_page_config(page_title="Laces Data Validator", layout="wide")

# Custom styling
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="custom-header">
        <div class="logo-section">
            <img src="https://market.laceshub.com/_next/static/media/logo.2f9a686f.svg" alt="LACES Logo">
            <div class="logo-text">Ontology Validator</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Upload sections
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="uploader-title">Upload Ontology file or SPARQL endpoint</div>', unsafe_allow_html=True)
    otl_file = st.file_uploader("Ontology in SHACL format", type=["ttl"])
    sparql_endpoint = st.text_input("SPARQL Endpoint URL")

with col2:
    st.markdown('<div class="uploader-title">Upload Project Data</div>', unsafe_allow_html=True)
    contractor_file = st.file_uploader("Data in RDF format", type=["ttl"])

if st.button("Validate"):
    if (not otl_file and not sparql_endpoint) or not contractor_file:
        st.warning("Please provide either an Ontology file or a SPARQL endpoint, AND a Project Data file.")
    else:
        with st.spinner("Running validation..."):
            try:
                # Load SHACL graph
                if otl_file:
                    shacl_graph = parse_graph_from_file(otl_file, format="turtle")
                else:
                    shacl_graph = load_shacl_graph_from_sparql(sparql_endpoint, CONSTRUCT_QUERY)

                # Load project data graph
                data_graph = parse_graph_from_file(contractor_file, format="turtle")

                # Validate
                conforms, results_graph, results_text = validate_graph(data_graph, shacl_graph)

                if conforms:
                    st.success("Project data conforms to the Ontology structure.")
                else:
                    st.error("Project data does NOT conform to the Ontology structure. See report below.")
                    df = parse_validation_results(results_graph)

                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="validation_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No detailed issues were found in the validation report.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
