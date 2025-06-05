import requests
from rdflib import Graph

def load_graph_from_endpoint(endpoint_url, query):
    response = requests.post(
        endpoint_url,
        params={"query": query},
        headers={
            "Accept": "text/turtle",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    response.raise_for_status()
    graph = Graph()
    graph.parse(data=response.text, format="turtle")
    return graph
