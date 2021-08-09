from automates.model_assembly.metadata import MetadataMethod, ProvenanceData, TypedMetadata, VariableTextDefinition
import os

from automates.model_assembly.networks import GroundedFunctionNetwork
from automates.model_assembly.interfaces import TextReadingInterface
from automates.model_assembly.linking import (
    CodeVarNode,
    CommSpanNode,
    EqnVarNode,
    GVarNode,
    ParameterSettingNode,
    build_link_graph,
    extract_link_tables
)
from automates.model_assembly.metadata import TypedMetadata, ProvenanceData, MetadataMethod

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

    def groundings_to_metadata(self, groundings):
        vars_to_metadata = {}
        for var,grounding in groundings.items():   
            vars_to_metadata[var] = list()

            provenance = {
                "method": "TEXT_READING_PIPELINE",
                "timestamp": ProvenanceData.get_dt_timestamp(),
            }

            for text_definition in grounding["text_definition"]:
                vars_to_metadata[var].append(TypedMetadata.from_data({
                    "type": "TEXT_DEFINITION",
                    "provenance": provenance,
                    "text_extraction": text_definition["text_extraction"],
                    "variable_identifier": grounding["gvar"],
                    "variable_definition": text_definition["variable_def"]
                }))

            for param_setting in grounding["parameter_setting"]:
                vars_to_metadata[var].append(TypedMetadata.from_data({
                        "type": "PARAMETER_SETTING",
                        "provenance": provenance,
                        "text_extraction": param_setting["text_extraction"],
                        "variable_identifier": grounding["gvar"],
                        "value": param_setting["value"]
                }))

            for equation_parameter in grounding["equation_parameter"]:
                vars_to_metadata[var].append(TypedMetadata.from_data({
                    "type": "EQUATION_PARAMETER",
                    "provenance": provenance,
                    "equation_extraction": equation_parameter["equation_extraction"],
                    "variable_identifier": grounding["gvar"],
                    "value": equation_parameter["value"]
                }))

        return vars_to_metadata

    def build_text_extraction(self, text_extraction):
        return {
            "text_spans": [
                {
                    "span": {
                        "char_begin": span.char_begin,
                        "char_end": span.char_end
                    }
                } for span in text_extraction.spans
            ]
        }

    def build_text_definition(self, gvar: GVarNode):
        return [
            {
                "variable_def": text_var.content,
                "text_extraction": self.build_text_extraction(text_var.text_extraction)
            }
            for text_var in gvar.text_vars
        ]

    def build_parameter_setting(self, gvar: GVarNode, L):
        parameter_settings = [
            param 
            for param in L.successors(gvar) 
            if isinstance(param, ParameterSettingNode)
        ] 

        return [
            {
                "value": param.content,
                "text_extraction": self.build_text_extraction(param.text_extraction),
            } 
            for param in parameter_settings
        ]


    def build_equation_groundings(self, gvar: GVarNode, L):
        equation_vars = [
            param 
            for param in L.predecessors(gvar) 
            if isinstance(param, EqnVarNode)
        ] 
        selected_eqn_var = max(equation_vars, key=lambda eq: L.edges[eq, gvar]["weight"])

        return [
            {
                "value": selected_eqn_var.content,
                "equation_extraction": {
                    "equation_number": selected_eqn_var.equation_number
                }
            }
        ]
        

    def get_links_from_graph(self, L):
        grfn_var_to_groundings = {}
        for code_var in [n for n in L.nodes if isinstance(n, CodeVarNode)]:
            code_var_name = code_var.content

            comm_nodes_to_gvars = {
                comm: [
                    gvar 
                    for gvar in L.predecessors(comm) 
                    if isinstance(gvar, GVarNode)
                ] 
                for comm in L.predecessors(code_var) 
                if isinstance(comm, CommSpanNode)
            }

            for comm, gvars in comm_nodes_to_gvars.items():
                for gvar in gvars:
                    score = min(L.edges[comm, code_var]["weight"], L.edges[gvar, comm]["weight"])
                    if (
                        code_var_name not in grfn_var_to_groundings 
                        or grfn_var_to_groundings[code_var_name]["score"] < score
                    ):
                        grfn_var_to_groundings[code_var_name] = {
                            "score": score,
                            "gvar": gvar.content, 
                            "equation_parameter": self.build_equation_groundings(gvar, L),
                            "parameter_setting": self.build_parameter_setting(gvar, L),
                            "text_definition": self.build_text_definition(gvar)
                        }

        return grfn_var_to_groundings

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

        # Generate temporary output file names for TR mentions
        cur_dir = os.getcwd()
        mentions_path = f"{cur_dir}/mentions.json"

        # Generate variables list for linking
        variable_ids = [v.identifier for k,v in grfn.variables.items()]

        # Build the hypothesis data by first getting mentions then generating 
        # the hypothesis
        self.text_reading_interface.extract_mentions(tr_sources["doc_file"], 
            mentions_path)
        hypothesis_data = self.text_reading_interface.get_link_hypotheses(
            mentions_path, 
            tr_sources["eqn_file"], 
            tr_sources["comm_file"], 
            variable_ids
        )

        # Cleanup temp files
        if os.path.isfile(mentions_path):
            os.remove(mentions_path)

        L = build_link_graph(hypothesis_data)
        grfn_var_to_groundings = self.get_links_from_graph(L)
        vars_to_metadata = self.groundings_to_metadata(grfn_var_to_groundings)

        for var_id,var in grfn.variables.items():
            var_name = var_id.name
            if var_name in vars_to_metadata:
                for metadata in vars_to_metadata[var_name]:
                    var.add_metadata(metadata)
        
        return grfn
