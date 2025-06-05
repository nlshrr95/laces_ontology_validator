def get_brug_construct_query():
    return """
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
