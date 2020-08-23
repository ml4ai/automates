import json

from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm


class QueryConductor:
    """Creates a reusable SPARQL query connection used for SVO querying

    Attributes:
        SPARQL_CONN (SPARQLWrapper): The connection used for sending queries
    """

    def __init__(self):
        self.SPARQL_CONN = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
        self.SPARQL_CONN.setReturnFormat(JSON)

    def query_with_term(self, term: str, progress_bar: tqdm) -> list:
        """Runs an SVO query using the provided <term> string

        Args:
            term (str): An SVO query search term for a extracted text variable
            progress_bar (tqdm): A TQDM object that tracks query progress

        Returns:
            list: a list of pairs of (<name>, <classname>) for <term>

        """
        self.SPARQL_CONN.setQuery(
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

        progress_bar.update(1)
        return [
            (v["name"]["value"], v["classname"]["value"])
            for v in self.SPARQL_CONN.query().convert()["results"]["bindings"]
        ]


def process_text_var_terms(input_filepath: str, output_filepath: str) -> None:
    """Run a set of queries through SVO and saves the result to JSON

    Args:
        input_filepath (str): path to a JSON file
            (e.g. tests/data/TR/var_terms.json)
        output_filepath (str): path for a JSON file to store output
    """
    if not (
        input_filepath.endswith(".json") and output_filepath.endswith(".json")
    ):
        raise RuntimeError("Expected both filepath arguments to be JSON files")

    queryer = QueryConductor()
    text_var_terms = json.load(open(input_filepath, "r"))
    num_queries = sum([len(o["svo_query_terms"]) for o in text_var_terms])
    with tqdm(total=num_queries, desc="Querying SVO") as pbar:
        query_results = {
            tv_obj["text_var"]: {
                term: queryer.query_with_term(term, pbar)
                for term in tv_obj["svo_query_terms"]
            }
            for tv_obj in text_var_terms
        }
        json.dump(query_results, open(output_filepath, "w"))
