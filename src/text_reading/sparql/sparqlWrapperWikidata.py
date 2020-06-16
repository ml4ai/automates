import requests
import sys
term = sys.argv[1]

#the link to the query on wikidata api https://w.wiki/Sfu
#todo for the query:
#have this regex as filter: "^(\\w*\\s){{0,2}}{term}(\\sof)?(\\s\\w*){{0,3}}$"
#make item description optional in the printout (some sort of getOrElse("None"))

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
	if 'itemDescription' in result.keys() and 'itemAltLabel' in result.keys():
		print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}\t{result['itemDescription']['value']}\t{result['itemAltLabel']['value']}")
	elif 'itemDescription' in result.keys() and not 'itemAltLabel' in result.keys():
		print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}\t{result['itemDescription']['value']}")
	
	elif 'itemAltLabel' in result.keys() and not 'itemDescription' in result.keys():
		print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}\t{result['itemAltLabel']['value']}")
	
	else:
	    print(f"{term}\t{result['item']['value']}\t{result['itemLabel']['value']}")#\t{result['itemDescription']['value']}")


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
