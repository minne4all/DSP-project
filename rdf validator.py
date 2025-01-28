import rdflib

g = rdflib.Graph()
try:
    g.parse("./ontology/aerius-extension2.ttl", format="turtle")
    print("Ontology parsed successfully!")
except Exception as e:
    print(f"Error parsing ontology: {e}")
