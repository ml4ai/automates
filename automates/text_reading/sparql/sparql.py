query = """prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix svu: <http://www.geoscienceontology.org/svo/svu#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

select ?x ?name ?prefLabel ?wikip ?classname
where {
    ?x rdfs:label ?xname .
    ?x a ?cl .
    ?cl rdfs:label ?classname .
    optional {?x skos:prefLabel ?label.
              BIND(STR(?label) as ?prefLabel)} .
    optional {?x svu:hasAssociatedWikipediaPage ?wikip}.
    FILTER(REGEX(?xname, '(?=.*(^|~|_|-)crop($|~|_|-))','i')) .
    BIND (STR(?xname) as ?name)}
ORDER BY ?x ?name ?prefLabel ?wikip"""
bashCommand = '''curl -X POST -H "Accept:application/sparql-results+json" --data-urlencode "query='query'" http://35.194.43.13:3030/ds/query'''
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(process)
