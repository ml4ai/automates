import os

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.interfaces import TextReadingInterface
from automates.model_assembly.linking import (
    build_link_graph,
    extract_link_tables
)

class TextReadingLinker:
    text_reading_interface: TextReadingInterface

    def __init__(self, text_reading_interface) -> None:
        self.text_reading_interface = text_reading_interface

    def gather_tr_sources(grfn: GroundedFunctionNetwork):
        """
        Given a GrFN, gather the following required sources for TR:
            1. Comment text document
            2. Source document text
            3. Equations document

        TODO At this point these files will be passed into the GrFN translation 
        process. Eventually we need to attempt to automatically generate this 
        data for all GrFNs passed in.


        Args:
            grfn (GroundedFunctionNetwork): GrFN to generate TR data for
        """
        pass


    def perform_tr_grfn_linking(self, grfn: GroundedFunctionNetwork, tr_sources: dict):
        """
        Enriches the given grfn with text reading metadata given the text reading
        source files (comments, source document, and equations text files).

        Args:
            grfn (GroundedFunctionNetwork): [description]
            tr_sources (dict, optional): [description]. Defaults to None.
        """

        # Make sure all required sources are given
        for document_type in ["doc_file", "comm_file", "eqn_file"]:
            if document_type not in tr_sources:
                print(f"Error: required TR source {document_type} not passed "
                    + "into TR-GrFN linking.")
                return grfn

        # Generate temporary output file names for TR mentions and GrFN json
        cur_dir = os.getcwd()
        mentions_path = f"{cur_dir}/mentions.json"
        grfn_json_path = f"{cur_dir}/grfn.json"

        grfn.to_json_file(grfn_json_path)

        # Build the hypothesis data by first getting mentions then generating 
        # the hypothesis
        self.text_reading_interface.extract_mentions(tr_sources["doc_file"], mentions_path)
        hypothesis_data = self.text_reading_interface.get_link_hypotheses(
            mentions_path, tr_sources["eqn_file"], grfn, tr_sources["comm_file"]
        )

        # Cleanup temp files
        for i in [mentions_path, grfn_json_path]:
            os.remove(i)

        # TODO Perform linking between the GrFN vars and TR hypothesis
        L = build_link_graph(hypothesis_data)
        tables = extract_link_tables(L)
        grfn_var_to_groundings = {}
        for var_name, var_data in tables.items():
            short_varname = var_name
            for link_data in var_data:
                score = link_data["link_score"]
                if (
                    short_varname not in grfn_var_to_groundings
                    or grfn_var_to_groundings[short_varname]["link_score"] < score
                ):
                    grfn_var_to_groundings = link_data