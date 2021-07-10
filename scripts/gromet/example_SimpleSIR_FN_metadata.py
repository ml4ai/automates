from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    # ----- Metadata -----

    # -- code span reference metadata

    file_simple_sir_py_uid = UidCodeFileReference("simple_sir_code")

    code_s_in = \
        CodeSpanReference(uid=UidMetadatum("code_s_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=9,
                          col_end=None)

    code_s_out = \
        CodeSpanReference(uid=UidMetadatum("code_s_out"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=53,
                          line_end=None,
                          col_begin=13,
                          col_end=None)

    code_i_in = \
        CodeSpanReference(uid=UidMetadatum("code_i_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=19,
                          col_end=None)

    code_i_out = \
        CodeSpanReference(uid=UidMetadatum("code_i_out"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=53,
                          line_end=None,
                          col_begin=16,
                          col_end=None)

    code_r_in = \
        CodeSpanReference(uid=UidMetadatum("code_r_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=29,
                          col_end=None)

    code_r_out = \
        CodeSpanReference(uid=UidMetadatum("code_r_out"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=53,
                          line_end=None,
                          col_begin=19,
                          col_end=None)

    code_beta_in = \
        CodeSpanReference(uid=UidMetadatum("code_beta_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=39,
                          col_end=42)

    code_gamma_in = \
        CodeSpanReference(uid=UidMetadatum("code_gamma_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=52,
                          col_end=56)

    code_dt_in = \
        CodeSpanReference(uid=UidMetadatum("code_gamma_in"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=None,
                          col_begin=66,
                          col_end=67)

    code_infected_id = \
        CodeSpanReference(uid=UidMetadatum("code_infected_id"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=46,
                          line_end=None,
                          col_begin=5,
                          col_end=12)

    code_recovered_id = \
        CodeSpanReference(uid=UidMetadatum("code_infected_id"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='IDENTIFIER',
                          file_id=file_simple_sir_py_uid,
                          line_begin=47,
                          line_end=None,
                          col_begin=5,
                          col_end=13)

    code_infected_exp = \
        CodeSpanReference(uid=UidMetadatum("code_infected_exp"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=46,
                          line_end=None,
                          col_begin=5,
                          col_end=50)

    code_recovered_exp = \
        CodeSpanReference(uid=UidMetadatum("code_recovered_exp"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=47,
                          line_end=None,
                          col_begin=5,
                          col_end=32)

    code_s_update_exp = \
        CodeSpanReference(uid=UidMetadatum("code_s_update_exp"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=49,
                          line_end=None,
                          col_begin=5,
                          col_end=21)

    code_i_update_exp = \
        CodeSpanReference(uid=UidMetadatum("code_i_update_exp"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=50,
                          line_end=None,
                          col_begin=5,
                          col_end=33)

    code_r_update_exp = \
        CodeSpanReference(uid=UidMetadatum("code_r_update_exp"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=51,
                          line_end=None,
                          col_begin=5,
                          col_end=22)

    code_sir_fn = \
        CodeSpanReference(uid=UidMetadatum("code_sir_fn"),
                          provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                timestamp=get_current_datetime()),
                          code_type='CODE_BLOCK',
                          file_id=file_simple_sir_py_uid,
                          line_begin=31,
                          line_end=53,
                          col_begin=None,
                          col_end=None)

    # -- model interface metadata

    simple_sir_model_interface = \
        ModelInterface(uid=UidMetadatum("simple_sir_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[UidVariable("S"), UidVariable("I"), UidVariable("R"),
                                  UidVariable("S_2"), UidVariable("I_2"), UidVariable("R_2"),
                                  UidVariable("beta"), UidVariable("gamma"),
                                  UidVariable("dt"), UidVariable("infected"), UidVariable("recovered")],
                       parameters=[UidVariable("beta"), UidVariable("gamma"),
                                   UidVariable("dt")],
                       initial_conditions=[UidVariable("S"), UidVariable("I"), UidVariable("R")])

    # -- code collection reference metadata

    file_simple_sir_py_code_file_reference = \
        CodeFileReference(uid=file_simple_sir_py_uid,
                          name="Simple_SIR",
                          path="SIR-simple.py")
    askeid_simple_sir_code = \
        GlobalReferenceId(type='aske_id',
                          id='fa2a6b75-2dfd-4124-99b3-e6a8587a7f55')
    metadatum_code_collection_ref = \
        CodeCollectionReference(uid=UidMetadatum("simple_sir_code_collection_ref"),
                                provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                      timestamp=get_current_datetime()),
                                global_reference_id=askeid_simple_sir_code,
                                file_ids=[file_simple_sir_py_code_file_reference])

    # -- textual document reference set
    askeid_simple_sir_doc_wiki = \
        GlobalReferenceId(type='aske_id',
                          id='4b429087-7e7c-4623-80fd-64fb934a8be6')
    text_doc_simple_sir_wiki = \
        TextualDocumentReference(uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                                 global_reference_id=askeid_simple_sir_doc_wiki,
                                 cosmos_id="COSMOS",
                                 cosmos_version_number="3.0",
                                 automates_id="AutoMATES-TR",
                                 automates_version_number="2.0",
                                 bibjson=Bibjson(title="The SIR Model Without Vital Dynamics - Wikipedia",
                                                 author=[BibjsonAuthor(name="Wikimedia Foundation")],
                                                 type="wikipedia",
                                                 website=BibjsonLinkObject(type="url", location="https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SIR_model_without_vital_dynamics"),
                                                 timestamp="2021-01-21T20:13",
                                                 link=[BibjsonLinkObject(type="gdrive", location="https://drive.google.com/file/d/1lexWCycLLTZq6FtQZ4AtBw30Bjeo5hRD/view?usp=sharing")],
                                                 identifier=[BibjsonIdentifier(type="aske_id", id="4b429087-7e7c-4623-80fd-64fb934a8be6")]))
    metadatum_textual_document_reference_set = \
        TextualDocumentReferenceSet(uid=UidMetadatum("simple_sir_textual_document_ref_set"),
                                    provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                          timestamp=get_current_datetime()),
                                    documents=[text_doc_simple_sir_wiki])

    # -- Variable text definition metadata

    # NOTE: The TextExtraction coordinates are made up here,
    #       just to show examples of the kinds of values that will appear.

    variable_S_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=1,
                                            char_begin=1,
                                            char_end=7)])
    variable_S_text_definition = \
        TextDescription(uid=UidMetadatum("S_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_S_text_definition_extraction,
                        variable_identifier="S",
                        variable_description="the stock of susceptible population",
                        description_type="definition")

    variable_I_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=1,
                                            char_begin=8,
                                            char_end=13)])
    variable_I_text_definition = \
        TextDescription(uid=UidMetadatum("I_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_I_text_definition_extraction,
                        variable_identifier="I",
                        variable_description="stock of infected",
                        description_type="definition")

    variable_R_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=1,
                                            char_begin=15,
                                            char_end=21)])
    variable_R_text_definition = \
        TextDescription(uid=UidMetadatum("R_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_R_text_definition_extraction,
                        variable_identifier="R",
                        variable_description="the stock of recovered population",
                        description_type="definition")

    variable_beta_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=2,
                                            char_begin=32,
                                            char_end=45)])
    variable_beta_text_definition = \
        TextDescription(uid=UidMetadatum("beta_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_beta_text_definition_extraction,
                        variable_identifier="β",
                        variable_description="Rate of transmission via contact",
                        description_type="definition")

    variable_gamma_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=2,
                                            char_begin=52,
                                            char_end=65)])
    variable_gamma_text_definition = \
        TextDescription(uid=UidMetadatum("gamma_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_gamma_text_definition_extraction,
                        variable_identifier="γ",
                        variable_description="Rate of recovery from infection",
                        description_type="definition")

    variable_dt_text_definition_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=1,
                                            block=4,
                                            char_begin=22,
                                            char_end=32)])
    variable_dt_text_definition = \
        TextDescription(uid=UidMetadatum("dt_text_definition"),
                        provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                              timestamp=get_current_datetime()),
                        text_extraction=variable_dt_text_definition_extraction,
                        variable_identifier="dt",
                        variable_description="Next inter-event time",
                        description_type="definition")

    # -- Variable TextUnit metadata

    # NOTE: The TextUnit metadatum is made up
    #       -- the simple_sir_wiki document does not itself include any units

    variable_S_text_unit_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=1,
                                            char_begin=10,
                                            char_end=20)])
    variable_S_text_unit = \
        TextUnit(uid=UidMetadatum("S_text_unit"),
                 provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                       timestamp=get_current_datetime()),
                 text_extraction=variable_S_text_unit_extraction,
                 unit="individual")

    variable_I_text_unit_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=2,
                                            char_begin=32,
                                            char_end=42)])
    variable_I_text_unit = \
        TextUnit(uid=UidMetadatum("I_text_unit"),
                 provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                       timestamp=get_current_datetime()),
                 text_extraction=variable_I_text_unit_extraction,
                 unit="individual")

    variable_R_text_unit_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=2,
                                            char_begin=82,
                                            char_end=92)])
    variable_R_text_unit = \
        TextUnit(uid=UidMetadatum("R_text_unit"),
                 provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                       timestamp=get_current_datetime()),
                 text_extraction=variable_R_text_unit_extraction,
                 unit="individual")

    variable_dt_text_unit_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=3,
                                            char_begin=12,
                                            char_end=16)])
    variable_dt_text_unit = \
        TextUnit(uid=UidMetadatum("dt_text_unit"),
                 provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                       timestamp=get_current_datetime()),
                 text_extraction=variable_dt_text_unit_extraction,
                 unit="days")

    # -- Variable text parameter metadata

    # NOTE: This is made up (the text_doc_simple_sir_wiki does not include parameter mentions)
    #       This is just an example of what a TextParameter metadata might look like

    beta_text_parameter_extraction = \
        TextExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                       text_spans=[TextSpan(page=0,
                                            block=5,
                                            char_begin=67,
                                            char_end=79)])
    beta_text_parameter = \
        TextParameter(uid=UidMetadatum("example_beta_text_parameter"),
                      provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                            timestamp=get_current_datetime()),
                      text_extraction=beta_text_parameter_extraction,
                      variable_identifier="β",
                      value="0.0000001019")

    # -- Equation definition metadata

    s_diff_equation_extraction = \
        EquationExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                           equation_number=0,
                           equation_source_latex="\frac{dS}{dt} = - \frac{\beta I S}{N}",
                           equation_source_mml='<?xml version="1.0" encoding="utf-8" standalone="no"?> <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="\frac{dS}{dt} = - \frac{\beta I S}{N} "> <mrow> <mfrac> <mrow> <mi>d</mi> <mi>S</mi> </mrow> <mrow> <mi>d</mi> <mi>t</mi> </mrow> </mfrac> <mo>=</mo> <mo>-</mo> <mfrac> <mrow> <mi>β</mi> <mi>I</mi> <mi>S</mi> </mrow> <mrow> <mi>N</mi> </mrow> </mfrac> </mrow> </math>')
    s_diff_equation_definition = \
        EquationDefinition(uid=UidMetadatum("s_diff_equation_definition"),
                           provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                 timestamp=get_current_datetime()),
                           equation_extraction=s_diff_equation_extraction)

    i_diff_equation_extraction = \
        EquationExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                           equation_number=1,
                           equation_source_latex="\frac{dI}{dt} = \frac{\beta I S}{N} - \gamma I",
                           equation_source_mml='<?xml version="1.0" encoding="utf-8" standalone="no"?> <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="\frac{dI}{dt} = \frac{\beta I S}{N} - \gamma I "> <mrow> <mfrac> <mrow> <mi>d</mi> <mi>I</mi> </mrow> <mrow> <mi>d</mi> <mi>t</mi> </mrow> </mfrac> <mo>=</mo> <mfrac> <mrow> <mi>β</mi> <mi>I</mi> <mi>S</mi> </mrow> <mrow> <mi>N</mi> </mrow> </mfrac> <mo>-</mo> <mi>γ</mi> <mi>I</mi> </mrow> </math>')
    i_diff_equation_definition = \
        EquationDefinition(uid=UidMetadatum("i_diff_equation_definition"),
                           provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                 timestamp=get_current_datetime()),
                           equation_extraction=i_diff_equation_extraction)

    r_diff_equation_extraction = \
        EquationExtraction(document_reference_uid=UidDocumentReference("text_doc_simple_sir_wiki"),
                           equation_number=2,
                           equation_source_latex="\frac{dR}{dt} = \gamma I",
                           equation_source_mml='<?xml version="1.0" encoding="utf-8" standalone="no"?> <math xmlns="http://www.w3.org/1998/Math/MathML" display="block" title="\frac{dR}{dt} = \gamma I "> <mrow> <mfrac> <mrow> <mi>d</mi> <mi>R</mi> </mrow> <mrow> <mi>d</mi> <mi>t</mi> </mrow> </mfrac> <mo>=</mo> <mi>γ</mi> <mi>I</mi> </mrow> </math>')
    r_diff_equation_definition = \
        EquationDefinition(uid=UidMetadatum("r_diff_equation_definition"),
                           provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                                 timestamp=get_current_datetime()),
                           equation_extraction=r_diff_equation_extraction)

    # ----- Model component definitions -----

    variables = [
        # state input
        Variable(uid=UidVariable("S"), name="S", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.S"),
                 states=[UidPort("P:sir.in.S"),
                         UidWire("W:S1.1"), UidWire("W:S1.2"),
                         UidPort("P:infected_exp.in.S"),
                         UidPort("P:S_update_exp.in.S")
                         ],
                 metadata=[variable_S_text_definition,
                           variable_S_text_unit]),
        Variable(uid=UidVariable("I"), name="I", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.I"),
                 states=[UidPort("P:sir.in.I"),
                         UidWire("W:I1.1"), UidWire("W:I1.2"), UidWire("W:I1.3"),
                         UidPort("P:infected_exp.in.I"),
                         UidPort("P:recovered_exp.in.I"),
                         UidPort("P:I_update_exp.in.I")
                         ],
                 metadata=[variable_I_text_definition,
                           variable_I_text_unit]),
        Variable(uid=UidVariable("R"), name="R", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.R"),
                 states=[UidPort("P:sir.in.R"),
                         UidWire("W:R1.1"), UidWire("W:R1.2"),
                         UidPort("P:infected_exp.in.R"),
                         UidPort("P:R_update_exp.in.R")
                         ],
                 metadata=[variable_R_text_definition,
                           variable_R_text_unit]),

        # state output
        Variable(uid=UidVariable("S_2"), name="S", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.out.S"),
                 states=[UidPort("P:sir.out.S"),  # out
                         UidWire("W:S1.1"), UidWire("W:S1.2"),
                         UidWire("W:S2"),
                         UidPort("P:S_update_exp.out.S")
                         ],
                 metadata=[variable_S_text_definition,
                           variable_S_text_unit]),
        Variable(uid=UidVariable("I_2"), name="I", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.out.I"),
                 states=[UidPort("P:sir.out.I"),
                         UidWire("W:I1.1"), UidWire("W:I1.2"), UidWire("W:I1.3"),
                         UidWire("W:I2"),
                         UidPort("P:I_update_exp.out.I")
                         ],
                 metadata=[variable_I_text_definition,
                           variable_I_text_unit]),
        Variable(uid=UidVariable("R_2"), name="R", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.out.R"),
                 states=[UidPort("P:sir.out.R"),
                         UidWire("W:R1.1"), UidWire("W:R1.2"),
                         UidWire("W:R2"),
                         UidPort("P:R_update_exp.out.R")
                         ],
                 metadata=[variable_R_text_definition,
                           variable_R_text_unit]),

        # parameters
        Variable(uid=UidVariable("beta"), name="beta", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.beta"),
                 states=[UidPort("P:sir.in.beta"),
                         UidWire("W:beta"),
                         UidPort("P:infected_exp.in.beta")
                         ],
                 metadata=[variable_beta_text_definition,
                           beta_text_parameter]),
        Variable(uid=UidVariable("gamma"), name="gamma", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.gamma"),
                 states=[UidPort("P:sir.in.gamma"),
                         UidWire("W:gamma"),
                         UidPort("P:recovered_exp.in.gamma")
                         ],
                 metadata=[variable_gamma_text_definition]),
        Variable(uid=UidVariable("dt"), name="dt", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.dt"),
                 states=[UidPort("P:sir.in.dt"),
                         UidWire("W:dt.1"), UidWire("W:dt.2"),
                         UidPort("P:infected_exp.in.dt"),
                         UidPort("P:recovered_exp.in.dt")
                         ],
                 metadata=[variable_dt_text_definition,
                           variable_dt_text_unit]),

        # internal
        Variable(uid=UidVariable("infected"), name="infected", type=UidType("Float"),
                 proxy_state=UidPort("P:infected_exp.out.infected"),
                 states=[UidPort("P:infected_exp.out.infected"),
                         UidWire("W:infected.1"), UidWire("W:infected.2"),
                         UidPort("P:S_update_exp.in.infected"),
                         UidPort("P:I_update_exp.in.infected")
                         ],
                 metadata=None),
        Variable(uid=UidVariable("recovered"), name="recovered", type=UidType("Float"),
                 proxy_state=UidPort("P:recovered_exp.out.recovered"),
                 states=[UidPort("P:recovered_exp.out.recovered"),
                         UidWire("W:recovered.1"), UidWire("W:recovered.2"),
                         UidPort("P:I_update_exp.in.recovered"),
                         UidPort("P:R_update_exp.in.recovered")
                         ],
                 metadata=None),
    ]

    wires = [
        # Var "S"
        Wire(uid=UidWire("W:S1.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.S"),
             tgt=UidPort("P:infected_exp.in.S")),
        Wire(uid=UidWire("W:S1.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.S"),
             tgt=UidPort("P:S_update_exp.in.S")),

        # Var "I"
        Wire(uid=UidWire("W:I1.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:infected_exp.in.I")),
        Wire(uid=UidWire("W:I1.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:recovered_exp.in.I")),
        Wire(uid=UidWire("W:I1.3"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.I"),
             tgt=UidPort("P:I_update_exp.in.I")),

        # Var "R"
        Wire(uid=UidWire("W:R1.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.R"),
             tgt=UidPort("P:infected_exp.in.R")),
        Wire(uid=UidWire("W:R1.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.R"),
             tgt=UidPort("P:R_update_exp.in.R")),

        # Var "beta"
        Wire(uid=UidWire("W:beta"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.beta"),
             tgt=UidPort("P:infected_exp.in.beta")),

        # Var "gamma"
        Wire(uid=UidWire("W:gamma"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.gamma"),
             tgt=UidPort("P:recovered_exp.in.gamma")),

        # Var "dt"
        Wire(uid=UidWire("W:dt.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.dt"),
             tgt=UidPort("P:infected_exp.in.dt")),
        Wire(uid=UidWire("W:dt.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.dt"),
             tgt=UidPort("P:recovered_exp.in.dt")),

        # Wire for Var "infected"
        Wire(uid=UidWire("W:infected.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:infected_exp.out.infected"),
             tgt=UidPort("P:S_update_exp.in.infected")),
        Wire(uid=UidWire("W:infected.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:infected_exp.out.infected"),
             tgt=UidPort("P:I_update_exp.in.infected")),

        # Wire for Var "recovered"
        Wire(uid=UidWire("W:recovered.1"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:recovered_exp.out.recovered"),
             tgt=UidPort("P:I_update_exp.in.recovered")),
        Wire(uid=UidWire("W:recovered.2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:recovered_exp.out.recovered"),
             tgt=UidPort("P:R_update_exp.in.recovered")),

        # part of Var "S"
        Wire(uid=UidWire("W:S2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:S_update_exp.out.S"),
             tgt=UidPort("P:sir.out.S")),

        # part of Var "I"
        Wire(uid=UidWire("W:I2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:I_update_exp.out.I"),
             tgt=UidPort("P:sir.out.I")),

        # part of Var "R"
        Wire(uid=UidWire("W:R2"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:R_update_exp.out.R"),
             tgt=UidPort("P:sir.out.R")),
    ]

    ports = [
        # The input ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.in.S"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="S", value=None,
             metadata=[code_s_in]),
        Port(uid=UidPort("P:sir.in.I"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="I", value=None,
             metadata=[code_i_in]),
        Port(uid=UidPort("P:sir.in.R"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="R", value=None,
             metadata=[code_r_in]),
        Port(uid=UidPort("P:sir.in.beta"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="beta", value=None,
             metadata=[code_beta_in]),
        Port(uid=UidPort("P:sir.in.gamma"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="gamma", value=None,
             metadata=[code_gamma_in]),
        Port(uid=UidPort("P:sir.in.dt"), box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="dt", value=None,
             metadata=[code_dt_in]),
        # The output ports to the 'sir' outer/parent Function
        Port(uid=UidPort("P:sir.out.S"), box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="S", value=None,
             metadata=[code_s_out]),
        Port(uid=UidPort("P:sir.out.I"), box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="I", value=None,
             metadata=[code_i_out]),
        Port(uid=UidPort("P:sir.out.R"), box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="R", value=None,
             metadata=[code_r_out]),

        # The input ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.in.S"), box=UidBox("B:infected_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="S", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.I"), box=UidBox("B:infected_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.R"), box=UidBox("B:infected_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="R", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.beta"), box=UidBox("B:infected_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="beta", value=None, metadata=None),
        Port(uid=UidPort("P:infected_exp.in.dt"), box=UidBox("B:infected_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="dt", value=None, metadata=None),
        # The output ports to the 'infected_exp' anonymous assignment Expression
        Port(uid=UidPort("P:infected_exp.out.infected"), box=UidBox("B:infected_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="infected", value=None,
             metadata=[code_infected_id]),

        # The input ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.in.I"), box=UidBox("B:recovered_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.gamma"), box=UidBox("B:recovered_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="gamma", value=None, metadata=None),
        Port(uid=UidPort("P:recovered_exp.in.dt"), box=UidBox("B:recovered_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="dt", value=None, metadata=None),
        # The output ports to the 'recovered_exp' anonymous assignment Expression
        Port(uid=UidPort("P:recovered_exp.out.recovered"), box=UidBox("B:recovered_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="recovered", value=None,
             metadata=[code_recovered_id]),

        # The input ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.in.S"), box=UidBox("B:S_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="S", value=None, metadata=None),
        Port(uid=UidPort("P:S_update_exp.in.infected"), box=UidBox("B:S_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="infected", value=None, metadata=None),
        # The output ports to the 'S_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:S_update_exp.out.S"), box=UidBox("B:S_update_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="S", value=None, metadata=None),

        # The input ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.in.I"), box=UidBox("B:I_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="I", value=None, metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.infected"), box=UidBox("B:I_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="infected", value=None, metadata=None),
        Port(uid=UidPort("P:I_update_exp.in.recovered"), box=UidBox("B:I_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="recovered", value=None, metadata=None),
        # The output ports to the 'I_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:I_update_exp.out.I"), box=UidBox("B:I_update_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="I", value=None, metadata=None),

        # The input ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.in.R"), box=UidBox("B:R_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="R", value=None, metadata=None),
        Port(uid=UidPort("P:R_update_exp.in.recovered"), box=UidBox("B:R_update_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"), name="recovered", value=None, metadata=None),
        # The output ports to the 'R_update_exp' anonymous assignment Expression
        Port(uid=UidPort("P:R_update_exp.out.R"), box=UidBox("B:R_update_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"), name="R", value=None, metadata=None)
    ]

    # Expression 'infected_exp' (SIR-simple line 46) -- input: (S I R beta dt)
    # Expr's:
    # e1 : (* beta S I) -> e1
    e1 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort("P:infected_exp.in.beta"),
                    UidPort("P:infected_exp.in.S"),
                    UidPort("P:infected_exp.in.I")])

    # This is an implementation bug in the original source code
    # e2 : (* e1 Literal(-1)) -> e2
    # e2 = Expr(call=RefOp(UidOp("*")),
    #           args=[e1, Literal(uid=None, type=UidType("Int"), value=Val("-1"),
    #                             name=None, metadata=None)])

    # e3 : (+ S I R) -> e3
    e3 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:infected_exp.in.S"),
                    UidPort("P:infected_exp.in.I"),
                    UidPort("P:infected_exp.in.R")])
    # e4 : (/ e2 e3) -> e4
    e4 = Expr(call=RefOp(UidOp("/")), args=[e1, e3])
    # e5 : (* e4 dt) -> e5
    e5 = Expr(call=RefOp(UidOp("*")), args=[e4, UidPort("P:infected_exp.in.dt")])
    # The anonymous Expression
    infected_exp = Expression(uid=UidBox("B:infected_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:infected_exp.in.S"),
                                     UidPort("P:infected_exp.in.I"),
                                     UidPort("P:infected_exp.in.R"),
                                     UidPort("P:infected_exp.in.beta"),
                                     UidPort("P:infected_exp.in.dt"),
                                     UidPort("P:infected_exp.out.infected")],
                              tree=e5,
                              metadata=[code_infected_exp])

    # Expression 'recovered_exp' (SIR-simple line 47) -- input: (gamma I dt)
    # Expr's:
    # e6 : (* gamma I) -> e6
    e6 = Expr(call=RefOp(UidOp("*")), args=[UidPort("P:recovered_exp.in.gamma"), UidPort("P:recovered_exp.in.I")])
    # e7 : (* e6 dt) -> e7
    e7 = Expr(call=RefOp(UidOp("*")), args=[e6, UidPort("P:recovered_exp.in.dt")])
    # The anonymous Expression
    recovered_exp = Expression(uid=UidBox("B:recovered_exp"),
                               type=None,
                               name=None,
                               ports=[UidPort("P:recovered_exp.in.I"),
                                      UidPort("P:recovered_exp.in.gamma"),
                                      UidPort("P:recovered_exp.in.dt"),
                                      UidPort("P:recovered_exp.out.recovered")],
                               tree=e7,
                               metadata=[code_recovered_exp])

    # Expression 'S_update_exp' (SIR-simple line 49) -- input: (S infected)
    # Expr's:
    # e8 : (- S infected) -> e8
    e8 = Expr(call=RefOp(UidOp("-")),
              args=[UidPort("P:S_update_exp.in.S"), UidPort("P:S_update_exp.in.infected")])
    # The anonymous Expression
    s_update_exp = Expression(uid=UidBox("B:S_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:S_update_exp.in.S"),
                                     UidPort("P:S_update_exp.in.infected"),
                                     UidPort("P:S_update_exp.out.S")],
                              tree=e8,
                              metadata=[s_diff_equation_definition,
                                        code_s_update_exp])

    # Expression 'I_update_exp' (SIR-simple line 50) -- input: (I infected recovered)
    # Expr's
    # e9 : (+ I infected) -> e9
    e9 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:I_update_exp.in.I"), UidPort("P:I_update_exp.in.infected")])
    # e10 : (- e9 recovered) -> e10
    e10 = Expr(call=RefOp(UidOp("-")),
               args=[e9, UidPort("P:I_update_exp.in.recovered")])
    # The anonymous Expression
    i_update_exp = Expression(uid=UidBox("B:I_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:I_update_exp.in.I"),
                                     UidPort("P:I_update_exp.in.infected"),
                                     UidPort("P:I_update_exp.in.recovered"),
                                     UidPort("P:I_update_exp.out.I")],
                              tree=e10,
                              metadata=[i_diff_equation_definition,
                                        code_i_update_exp])

    # Expression 'R_update_exp' (SIR-simple line 50) -- input: (R recovered)
    # Expr's
    # e11 : (+ R recovered) -> e11
    e11 = Expr(call=RefOp(UidOp("+")),
               args=[UidPort("P:R_update_exp.in.R"), UidPort("P:R_update_exp.in.recovered")])
    # The anonymous Expression
    r_update_exp = Expression(uid=UidBox("B:R_update_exp"),
                              type=None,
                              name=None,
                              ports=[UidPort("P:R_update_exp.in.R"),
                                     UidPort("P:R_update_exp.in.recovered"),
                                     UidPort("P:R_update_exp.out.R")],
                              tree=e11,
                              metadata=[r_diff_equation_definition,
                                        code_r_update_exp])

    sir = Function(uid=UidBox("B:sir"),
                   type=None,
                   name=UidOp("sir"),
                   ports=[UidPort("P:sir.in.S"),
                          UidPort("P:sir.in.I"),
                          UidPort("P:sir.in.R"),
                          UidPort("P:sir.in.beta"),
                          UidPort("P:sir.in.gamma"),
                          UidPort("P:sir.in.dt"),
                          UidPort("P:sir.out.S"),
                          UidPort("P:sir.out.I"),
                          UidPort("P:sir.out.R")],

                   # contents
                   wires=[UidWire("W:S1.1"), UidWire("W:S1.2"),
                          UidWire("W:I1.1"), UidWire("W:I1.2"), UidWire("W:I1.3"),
                          UidWire("W:R1.1"), UidWire("W:R1.2"),
                          UidWire("W:beta"), UidWire("W:gamma"),
                          UidWire("W:dt.1"), UidWire("W:dt.2"),
                          UidWire("W:infected.1"), UidWire("W:infected.2"),
                          UidWire("W:recovered.1"), UidWire("W:recovered.2"),
                          UidWire("W:S2"), UidWire("W:I2"), UidWire("W:R2")],
                   boxes=[UidBox("B:infected_exp"),
                          UidBox("B:recovered_exp"),
                          UidBox("B:S_update_exp"),
                          UidBox("B:I_update_exp"),
                          UidBox("B:R_update_exp")],
                   junctions=None,

                   metadata=[code_sir_fn])

    boxes = [sir, infected_exp, recovered_exp,
             s_update_exp, i_update_exp, r_update_exp]

    _g = Gromet(
        uid=UidGromet("SimpleSIR_FN"),
        name="SimpleSIR_metadata",
        type=UidType("FunctionNetwork"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=[simple_sir_model_interface,
                  metadatum_code_collection_ref,
                  metadatum_textual_document_reference_set]
    )

    return _g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
