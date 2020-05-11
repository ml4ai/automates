import requests
import sys
term = sys.argv[1]

url = 'https://query.wikidata.org/sparql'
query = f"""
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?itemAltLabel
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



    FILTER REGEX (?label, "^{term}$")
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}

LIMIT 10
"""
r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()

for result in data["results"]["bindings"]:
    print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}\t{result['itemDescription']['value']}")






# import sys
# from SPARQLWrapper import SPARQLWrapper, JSON
#
# term = sys.argv[1]
#
# sparql = SPARQLWrapper("https://www.mediawiki.org")
# sparql.setReturnFormat(JSON)
# sparql.setQuery(
#     f"""
# SELECT DISTINCT ?item ?itemLabel ?itemDescription ?itemAltLabel
# WHERE
# {{
#   SERVICE wikibase:mwapi
#   {{
#     bd:serviceParam wikibase:endpoint "www.wikidata.org";
#                     wikibase:api "Generator";
#                     mwapi:generator "search";
#                     mwapi:gsrsearch "inlabel:'{term}'";
#                     mwapi:gsrlimit "max".
#     ?item wikibase:apiOutputItem mwapi:title.
#   }}
#   ?item rdfs:label ?label.
#
#
#
# #   FILTER REGEX (?label, "^crop$")
#   SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
# }}
#
# LIMIT 10
#     """
# )
#
# results = sparql.query().convert()
#
# # print("res info: ", results.info())
# for result in results["results"]["bindings"]:
#     print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}\t{result['itemLabel']['value']}")
# #
# #
# # # print(results)
