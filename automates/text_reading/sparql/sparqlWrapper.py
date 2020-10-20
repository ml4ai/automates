import sys
from SPARQLWrapper import SPARQLWrapper, JSON

term = sys.argv[1]
sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
sparql.setQuery(
    f"""
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix svu: <http://www.geoscienceontology.org/svo/svu#>
    prefix skos: <http://www.w3.org/2004/02/skos/core#>

    select ?x ?name ?prefLabel ?wikip ?classname
    where {{
        ?x rdfs:label ?xname .
        ?x a ?cl .
        ?cl rdfs:label ?classname .
        optional {{?x skos:prefLabel ?label.
                  BIND(STR(?label) as ?prefLabel)}} .
        optional {{?x svu:hasAssociatedWikipediaPage ?wikip}}.
        FILTER(REGEX(?xname, '(?=.*(^|~|_|-){term}($|~|_|-))','i')) .
        BIND (STR(?xname) as ?name)}}
    ORDER BY ?x ?name ?prefLabel ?wikip

    LIMIT 10
    """
)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(f"{term}\t{result['name']['value']}\t{result['classname']['value']}")


# print(results)
