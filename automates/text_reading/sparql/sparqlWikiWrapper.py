import requests
import sys
term = sys.argv[1]

# tutorial: https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
#" It is possible for a query to access Wikidata's search function with the MediaWiki API Query Service. [...]  uses the MediaWiki API, and can therefore run without timeout" (https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/query_optimization)
#the link to the query on wikidata api https://w.wiki/Sfu
#todo for the query:
#have this regex as filter: "^(\\w*\\s){{0,2}}{term}(\\sof)?(\\s\\w*){{0,3}}$"
#make item description optional in the printout (some sort of getOrElse("None"))
# is mwapi:gsrsearch '{term}' more time consuming than mwapi:gsrsearch "inlabel:'{term}'"? (potentially larger search space)
# todo: get this to work order by desc(strlen(str(?searchterm))/strlen(str(?itemLabel))) with search term defined as   VALUES ?term {term} before service

url = 'https://query.wikidata.org/sparql'
query = f"""
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?itemAltLabel ?subclassOf
WHERE
{{
    SERVICE wikibase:mwapi
{{
    bd:serviceParam wikibase:endpoint "www.wikidata.org";
wikibase:api "Generator";
mwapi:generator "search";
mwapi:gsrsearch "inlabel:'{term}'";
mwapi:gsrlimit "max".
?item wikibase:apiOutputItem mwapi:title.
}}
?item rdfs:label ?label.
OPTIONAL {{ ?item wdt:P279 ?subclassOf. }}
?sitelink ^schema:name ?article .
?article schema:about ?item ;
    schema:isPartOf <https://en.wikipedia.org/> .


    FILTER REGEX (?label, "^(\\\\w*\\\\s){{0,2}}?{term}(\\\\sof)?(\\\\s\\\\w*){{0,3}}?$")

    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}
order by strlen(str(?label))

LIMIT 20
"""
r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()



for result in data["results"]["bindings"]:
    item = result['item']['value']
    itemLabel = result['itemLabel']['value']
    descr = result['itemDescription']['value'] if 'itemDescription' in result.keys()  else "NA"
    altLabel = result['itemAltLabel']['value'] if 'itemAltLabel' in result.keys()  else "NA"
    subClassOf = result['subclassOf']['value'] if 'subclassOf' in result.keys()  else "NA"

    print(f"{term}\t{item}\t{itemLabel}\t{descr}\t{altLabel}\t{subClassOf}")
