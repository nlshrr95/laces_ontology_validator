import streamlit as st
from rdflib import Graph
from validator import validate_graph
import requests
import pandas as pd
from rdflib.namespace import RDF, Namespace

st.set_page_config(page_title="Laces Data Validator", layout="wide")

# Custom CSS styling for the app
st.markdown("""
    <style>
        body {
            background-color: #fbfbfb;
        }
        section.main {
            background-color: #fbfbfb;
        }
        .custom-header {
            background-color: #000000;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'Segoe UI', sans-serif;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        .custom-header .logo-section {
            display: flex;
            align-items: center;
        }
        .custom-header .logo-section img {
            height: 24px;
            margin-right: 12px;
        }
        .custom-header .logo-text {
            font-size: 22px;
            font-weight: 600;
            color: #FFFFFF;
        }
        div.stButton > button:first-child {
            background-color: #6a0dad;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1.5em;
            border: none;
            font-weight: 600;
        }
        div.stButton > button:first-child:hover {
            background-color: #5a059e;
            color: white;
        }
        .uploader-title {
            font-weight: 700;
            font-size: 20px;
            margin-bottom: 10px;
        }
    </style>

    <div class="custom-header">
        <div class="logo-section">
            <img src="https://market.laceshub.com/_next/static/media/logo.2f9a686f.svg" alt="LACES Logo">
            <div class="logo-text">Ontology Validator</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Created  two columns in the layout: Left for  SHACL Ontology upload, right for Project Data upload
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="uploader-title">Upload Ontology file or SPARQL endpoint</div>', unsafe_allow_html=True)
    otl_file = st.file_uploader("Ontology in SHACL format", type=["ttl"])
    sparql_endpoint = st.text_input("SPARQL Endpoint URL")

with col2:
    st.markdown('<div class="uploader-title">Upload Project Data</div>', unsafe_allow_html=True)
    contractor_file = st.file_uploader("Data in RDF format", type=["ttl"])

if st.button("Validate"):
    # Check if all input data is present
    if (not otl_file and not sparql_endpoint) or not contractor_file:
        st.warning("Please provide either an Ontology file or a SPARQL endpoint, AND a Project Data file.")
    else:
        st.info("Running validation...")

        try:
            # Load SHACL ontology graph from file or SPARQL endpoint
            shacl_graph = Graph()

            if otl_file:
                # Parse uploaded file directly
                shacl_graph.parse(otl_file, format="turtle")
            else:
                # Prepare SPARQL CONSTRUCT query (no extra indentation/newlines)
                query = """
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX otl: <http://otl.amsterdam.nl/def/objecttype/>
PREFIX eig: <http://otl.amsterdam.nl/def/eigenschap/>

CONSTRUCT {
  ?shape a sh:NodeShape ;
         sh:targetClass otl:Brug ;
         sh:property ?property .

  ?property sh:path ?path ;
            sh:datatype ?datatype ;
            sh:minCount ?minCount ;
            sh:maxCount ?maxCount ;
            sh:message ?message .
}
WHERE {
  BIND(<http://otl.amsterdam.nl/def/shape/BrugShape> AS ?shape)
  ?shape a sh:NodeShape ;
         sh:targetClass otl:Brug ;
         sh:property ?property .

  OPTIONAL { ?property sh:path ?path }
  OPTIONAL { ?property sh:datatype ?datatype }
  OPTIONAL { ?property sh:minCount ?minCount }
  OPTIONAL { ?property sh:maxCount ?maxCount }
  OPTIONAL { ?property sh:message ?message }
}
"""
                # Request the SPARQL endpoint with the query
                response = requests.post(
                    sparql_endpoint,
                    params={"query": query},
                    headers={"Accept": "text/turtle",
                        "Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()

                # Show TTL response for debug
#                st.text_area("SPARQL TTL Response (debug)", response.text, height=200)

                # Parse the TTL response into the SHACL graph
                shacl_graph.parse(data=response.text, format="turtle")

            # Load project data graph
            data_graph = Graph()
            data_graph.parse(contractor_file, format="turtle")

            # Run validation (assumes validate_graph returns (bool, graph, text))
            conforms, results_graph, results_text = validate_graph(data_graph, shacl_graph)

            if conforms:
                st.success("Project data conforms to the Ontology structure.")
            else:
                st.error("Project data does NOT conform to the Ontology structure. See report below.")
#                st.text_area("SHACL Validation Report", results_text, height=400)
                
                SH = Namespace("http://www.w3.org/ns/shacl#")

                rows = []
                for result in results_graph.subjects(RDF.type, SH.ValidationResult):
                    focus_node = results_graph.value(result, SH.focusNode)
                    result_path = results_graph.value(result, SH.resultPath)
                    message = results_graph.value(result, SH.resultMessage)
                    severity = results_graph.value(result, SH.resultSeverity)
                    source_constraint = results_graph.value(result, SH.sourceConstraintComponent)

                    rows.append({
                        "Object": str(focus_node) if focus_node else "-",
                        "Error detected on": str(result_path) if result_path else "-",
                        "Message": str(message) if message else "-",
                        "Constraint": str(source_constraint).split("#")[-1] if source_constraint else "-"
                    })

                if rows:
                    df = pd.DataFrame(rows)
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
