import rdflib

g = rdflib.Graph()
try:
    g.parse("./uploads/project1.ttl", format="turtle")
    print("Ontology parsed successfully!")
except Exception as e:
    print(f"Error parsing ontology: {e}")
