import requests
import sys
term = sys.argv[1]

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
mwapi:gsrsearch "'{term}'";
mwapi:gsrlimit "max".
?item wikibase:apiOutputItem mwapi:title.
}}
?item rdfs:label ?label.
?sitelink ^schema:name ?article .
?article schema:about ?item ;
    schema:isPartOf <https://en.wikipedia.org/> .

    ?item wdt:P279 ?subclassOf.
    FILTER REGEX (?label, "^(\\\\w*\\\\s){{0,2}}?{term}(\\\\sof)?(\\\\s\\\\w*){{0,3}}?$")

    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
}}
order by strlen(str(?label))

LIMIT 30
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
	

#the link to the query on wikidata api https://w.wiki/Sfu

# The query should be something like this
# url = 'https://query.wikidata.org/sparql'
# query = f"""
# SELECT DISTINCT ?item ?itemLabel ?itemDescription ?itemAltLabel
# WHERE
# {{
#     SERVICE wikibase:mwapi
# {{
#     bd:serviceParam wikibase:endpoint "www.wikidata.org";
# wikibase:api "Generator";
# mwapi:generator "search";
# mwapi:gsrsearch "inlabel:'{term}'";
# mwapi:gsrlimit "max".
# ?item wikibase:apiOutputItem mwapi:title.
# }}
# ?item rdfs:label ?label.
# ?sitelink ^schema:name ?article .
# ?article schema:about ?item ;
#     schema:isPartOf <https://en.wikipedia.org/> .


#     FILTER REGEX (?label, "^(\\w*\\s){{0,2}}{term}(\\sof)?(\\s\\w*){{0,3}}$")

#     SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
# }}

# LIMIT 10
# """



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
