from rdflib.namespace import RDF, Namespace
import pandas as pd

def parse_validation_results(results_graph):
    SH = Namespace("http://www.w3.org/ns/shacl#")
    rows = []

    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        focus_node = results_graph.value(result, SH.focusNode)
        result_path = results_graph.value(result, SH.resultPath)
        message = results_graph.value(result, SH.resultMessage)
        source_constraint = results_graph.value(result, SH.sourceConstraintComponent)

        rows.append({
            "Object": str(focus_node) if focus_node else "-",
            "Error detected on": str(result_path) if result_path else "-",
            "Message": str(message) if message else "-",
            "Constraint": str(source_constraint).split("#")[-1] if source_constraint else "-"
        })

    return pd.DataFrame(rows)
