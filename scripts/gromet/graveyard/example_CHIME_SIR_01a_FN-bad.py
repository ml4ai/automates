from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:
    # ----- Metadata -----

    chime_model_description = \
        ModelDescription(uid=UidMetadatum('chime_model_description'),
                         provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                               timestamp=get_current_datetime()),
                         name='CHIME v01 [SIR dynamics only]',
                         description='The CHIME (COVID-19 Hospital Impact Model for Epidemics) App '
                                     'is designed to assist hospitals and public health officials '
                                     'understand hospital capacity needs as they relate to the '
                                     'COVID-19 pandemic. CHIME enables capacity planning by providing '
                                     'estimates of total daily (i.e. new) and running totals of '
                                     '(i.e. census) inpatient hospitalizations, ICU admissions, and '
                                     'patients requiring ventilation. These estimates are generated '
                                     'using a SIR (Susceptible, Infected, Recovered) model, a standard '
                                     'epidemiological modeling technique.')

    chime_model_interface = \
        ModelInterface(uid=UidMetadatum("chime_model_interface"),
                       provenance=Provenance(method=MetadatumMethod('Manual_claytonm@az'),
                                             timestamp=get_current_datetime()),
                       variables=[UidVariable("V:sir.s_in"),
                                  UidVariable("V:sir.s_out"),
                                  UidVariable("V:sir.i_in"),
                                  UidVariable("V:sir.i_out"),
                                  UidVariable("V:sir.r_in"),
                                  UidVariable("V:sir.r_out")],  # todo update
                       parameters=[UidVariable("V:sir.n"),
                                   UidVariable("V:sir.beta"),
                                   UidVariable("V:sir.gamma")],  # todo update
                       initial_conditions=[UidVariable("V:sir.s_in"),
                                           UidVariable("V:sir.i_in"),
                                           UidVariable("V:sir.r_in")]  # todo update
                       )

    # ----- Model component definitions -----

    variables = [

        # -- sim_sir() Variables --

        # todo

        # -- sir() Variables --

        # sir input
        Variable(uid=UidVariable("V:sir.n"),
                 name="n", type=UidType("Integer"),
                 proxy_state=UidPort("P:sir.n"),
                 states=[UidPort("P:sir.n"),
                         UidWire("W:sir.n>sir_scale_exp.n"),
                         UidPort("P:sir_scale_exp.n")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.beta"),
                 name="beta", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.beta"),
                 states=[UidPort("P:sir.in.beta"),
                         UidWire("W:sir.beta>sir_s_n_exp.beta"),
                         UidPort("P:sir_s_n_exp.beta"),
                         UidWire("W:sir.beta>sir_i_n_exp.beta"),
                         UidPort("P:sir_i_n_exp.beta")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.gamma"),
                 name="gamma", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.gamma"),
                 states=[UidPort("P:sir.in.gamma"),
                         UidWire("W:sir.gamma>sir_i_n_exp.gamma"),
                         UidPort("P:sir_i_n_exp.gamma"),
                         UidWire("W:sir.gamma>sir_r_n_exp.gamma"),
                         UidPort("P:sir_r_n_exp.gamma")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.s_in"),
                 name="s", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.s"),
                 states=[UidPort("P:sir.in.s"),
                         UidWire("W:sir.s_in>sir_s_n_exp.s"),
                         UidPort("P:sir_s_n_exp.s"),
                         UidWire("W:sir.s_in>sir_i_n_exp.s"),
                         UidPort("P:sir_i_n_exp.s")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.i_in"),
                 name="i", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.r"),
                 states=[UidPort("P:sir.in.r"),
                         UidWire("W:sir.i_in>sir_s_n_exp.i"),
                         UidPort("P:sir_s_n_exp.i"),
                         UidWire("W:sir.i_in>sir_i_n_exp.i"),
                         UidPort("P:sir_i_n_exp.i"),
                         UidWire("W:sir.i_in>sir_r_n_exp.i"),
                         UidPort("P:sir_r_n_exp.i")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.r_in"),
                 name="r", type=UidType("Float"),
                 proxy_state=UidPort("P:sir.in.r"),
                 states=[UidPort("P:sir.in.r"),
                         UidWire("W:sir.r_in>sir_r_n_exp.r"),
                         UidPort("P:sir_r_n_exp.r")],
                 metadata=None),

        # sir internal
        Variable(uid=UidVariable("V:sir.s_n"),
                 name="s_n", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_s_n_exp.s_n"),
                 states=[UidPort("P:sir_s_n_exp.s_n"),
                         UidWire("W:sir_s_n_exp.s_n>sir_scale_exp.s_n"),
                         UidPort("P:sir_scale_exp.s_n"),
                         UidWire("W:sir_s_n_exp.s_n>sir_s_exp.s_n"),
                         UidPort("P:sir_s_exp.s_n")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.i_n"),
                 name="i_n", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_i_n_exp.i_n"),
                 states=[UidPort("P:sir_i_n_exp.i_n"),
                         UidWire("W:sir_i_n_exp.i_n>sir_scale_exp.i_n"),
                         UidPort("P:sir_scale_exp.i_n"),
                         UidWire("W:sir_i_n_exp.i_n>sir_i_exp.i_n"),
                         UidPort("P:sir_i_exp.i_n")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.r_n"),
                 name="r_n", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_r_n_exp.r_n"),
                 states=[UidPort("P:sir_r_n_exp.r_n"),
                         UidWire("W:sir_r_n_exp.r_n>sir_scale_exp.r_n"),
                         UidPort("P:sir_scale_exp.r_n"),
                         UidWire("W:sir_r_n_exp.r_n>sir_r_exp.r_n"),
                         UidPort("P:sir_r_exp.r_n")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.scale"),
                 name="scale", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_scale_exp.scale"),
                 states=[UidPort("P:sir_scale_exp.scale"),
                         UidWire("W:sir_scale_exp.scale>sir_s_exp.scale"),
                         UidPort("P:sir_s_exp.scale"),
                         UidWire("W:sir_scale_exp.scale>sir_i_exp.scale"),
                         UidPort("P:sir_i_exp.scale"),
                         UidWire("W:sir_scale_exp.scale>sir_r_exp.scale"),
                         UidPort("P:sir_r_exp.scale")],
                 metadata=None),

        # sir output
        Variable(uid=UidVariable("V:sir.s_out"),
                 name="s", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_s_exp.s"),
                 states=[UidPort("P:sir_s_exp.s"),
                         UidWire("W:sir_s_exp.s>sir.s_out"),
                         UidPort("P:sir.out.s")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.i_out"),
                 name="i", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_i_exp.i"),
                 states=[UidPort("P:sir_i_exp.i"),
                         UidWire("W:sir_i_exp.i>sir.i_out"),
                         UidPort("P:sir.out.i")],
                 metadata=None),
        Variable(uid=UidVariable("V:sir.r_out"),
                 name="r", type=UidType("Float"),
                 proxy_state=UidPort("P:sir_r_exp.r"),
                 states=[UidPort("P:sir_r_exp.r"),
                         UidWire("W:sir_r_exp.r>sir.r_out"),
                         UidPort("P:sir.out.r")],
                 metadata=None)
    ]

    wires = [

        # -- sim_sir() Wires --

        # todo: Rewire when updating simsir
        Wire(uid=UidWire("W:simsir.in.s>sir.in.s"),
             type=None,
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidPort("P:simsir.in.s"),
             tgt=UidPort("P:sir.in.s"), ),
        # todo: Rewire when updating simsir
        Wire(uid=UidWire("W:sir.out.s>simsir.out.s"),
             type=None,
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.out.s"),
             tgt=UidPort("P:simsir.out.s")),

        # -- sir() Wires --

        # sir
        Wire(uid=UidWire("W:sir.n>sir_scale_exp.n"),
             type=None,
             value_type=UidType("Integer"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.n"),
             tgt=UidPort("P:sir_scale_exp.n")),
        Wire(uid=UidWire("W:sir.beta>sir_s_n_exp.beta"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.beta"),
             tgt=UidPort("P:sir_s_n_exp.beta")),
        Wire(uid=UidWire("W:sir.beta>sir_i_n_exp.beta"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.beta"),
             tgt=UidPort("P:sir_i_n_exp.beta")),
        Wire(uid=UidWire("W:sir.gamma>sir_i_n_exp.gamma"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.gamma"),
             tgt=UidPort("P:sir_i_n_exp.gamma")),
        Wire(uid=UidWire("W:sir.gamma>sir_r_n_exp.gamma"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.gamma"),
             tgt=UidPort("P:sir_r_n_exp.gamma")),
        Wire(uid=UidWire("W:sir.s_in>sir_s_n_exp.s"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.s"),
             tgt=UidPort("P:sir_s_n_exp.s")),
        Wire(uid=UidWire("W:sir.s_in>sir_i_n_exp.s"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.s"),
             tgt=UidPort("P:sir_i_n_exp.s")),
        Wire(uid=UidWire("W:sir.i_in>sir_s_n_exp.i"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.r"),
             tgt=UidPort("P:sir_s_n_exp.i")),
        Wire(uid=UidWire("W:sir.i_in>sir_i_n_exp.i"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.r"),
             tgt=UidPort("P:sir_i_n_exp.i")),
        Wire(uid=UidWire("W:sir.i_in>sir_r_n_exp.i"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.r"),
             tgt=UidPort("P:sir_r_n_exp.i")),
        Wire(uid=UidWire("W:sir.r_in>sir_r_n_exp.r"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.in.r"),
             tgt=UidPort("P:sir_r_n_exp.r")),
        Wire(uid=UidWire("W:sir_s_n_exp.s_n>sir_scale_exp.s_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_s_n_exp.s_n"),
             tgt=UidPort("P:sir_scale_exp.s_n")),
        Wire(uid=UidWire("W:sir_s_n_exp.s_n>sir_s_exp.s_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_s_n_exp.s_n"),
             tgt=UidPort("P:sir_s_exp.s_n")),
        Wire(uid=UidWire("W:sir_i_n_exp.i_n>sir_scale_exp.i_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_i_n_exp.i_n"),
             tgt=UidPort("P:sir_scale_exp.i_n")),
        Wire(uid=UidWire("W:sir_i_n_exp.i_n>sir_i_exp.i_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_i_n_exp.i_n"),
             tgt=UidPort("P:sir_i_exp.i_n")),
        Wire(uid=UidWire("W:sir_r_n_exp.r_n>sir_scale_exp.r_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_r_n_exp.r_n"),
             tgt=UidPort("P:sir_scale_exp.r_n")),
        Wire(uid=UidWire("W:sir_r_n_exp.r_n>sir_r_exp.r_n"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_r_n_exp.r_n"),
             tgt=UidPort("P:sir_r_exp.r_n")),

        Wire(uid=UidWire("W:sir_scale_exp.scale>sir_s_exp.scale"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_scale_exp.scale"),
             tgt=UidPort("P:sir_s_exp.scale")),
        Wire(uid=UidWire("W:sir_scale_exp.scale>sir_i_exp.scale"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_scale_exp.scale"),
             tgt=UidPort("P:sir_i_exp.scale")),
        Wire(uid=UidWire("W:sir_scale_exp.scale>sir_r_exp.scale"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_scale_exp.scale"),
             tgt=UidPort("P:sir_r_exp.scale")),

        Wire(uid=UidWire("W:sir_s_exp.s>sir.s_out"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_s_exp.s"),
             tgt=UidPort("P:sir.out.s")),

        Wire(uid=UidWire("W:sir_i_exp.i>sir.i_out"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_i_exp.i"),
             tgt=UidPort("P:sir.out.i")),

        Wire(uid=UidWire("W:sir_r_exp.r>sir.r_out"),
             type=None,
             value_type=UidType("Float"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir_r_exp.r"),
             tgt=UidPort("P:sir.out.r"))
    ]

    ports = [

        # -- sim_sir() Ports --

        # simsir in
        Port(uid=UidPort("P:simsir.in.s"),
             box=UidBox("B:simsir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),
        # simsir out
        Port(uid=UidPort("P:simsir.out.s"),
             box=UidBox("B:simsir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),

        # -- sir() Ports --

        # sir in
        Port(uid=UidPort("P:sir.n"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Integer"),
             name="n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.beta"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="beta",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.gamma"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="gamma",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.s"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.r"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.in.r"),
             box=UidBox("B:sir"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="r",
             value=None, metadata=None),
        # sir out
        Port(uid=UidPort("P:sir.out.s"),
             box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.out.i"),
             box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir.out.r"),
             box=UidBox("B:sir"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="r",
             value=None, metadata=None),

        # sir_s_n_exp in
        Port(uid=UidPort("P:sir_s_n_exp.beta"),
             box=UidBox("B:sir_s_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="beta",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_s_n_exp.s"),
             box=UidBox("B:sir_s_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_s_n_exp.i"),
             box=UidBox("B:sir_s_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),
        # sir_s_n_exp out
        Port(uid=UidPort("P:sir_s_n_exp.s_n"),
             box=UidBox("B:sir_s_n_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="s_n",
             value=None, metadata=None),

        # sir_s_n_exp in
        Port(uid=UidPort("P:sir_i_n_exp.beta"),
             box=UidBox("B:sir_i_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="beta",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_i_n_exp.s"),
             box=UidBox("B:sir_i_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_i_n_exp.i"),
             box=UidBox("B:sir_i_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_i_n_exp.gamma"),
             box=UidBox("B:sir_i_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="gamma",
             value=None, metadata=None),
        # sir_i_n_exp out
        Port(uid=UidPort("P:sir_i_n_exp.i_n"),
             box=UidBox("B:sir_i_n_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="i_n",
             value=None, metadata=None),

        # sir_r_n_exp in
        Port(uid=UidPort("P:sir_r_n_exp.gamma"),
             box=UidBox("B:sir_r_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="gamma",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_r_n_exp.i"),
             box=UidBox("B:sir_r_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_r_n_exp.r"),
             box=UidBox("B:sir_r_n_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="r",
             value=None, metadata=None),
        # sir_r_n_exp out
        Port(uid=UidPort("P:sir_r_n_exp.r_n"),
             box=UidBox("B:sir_r_n_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="r_n",
             value=None, metadata=None),

        # sir_scale_exp in
        Port(uid=UidPort("P:sir_scale_exp.n"),
             box=UidBox("B:sir_scale_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_scale_exp.s_n"),
             box=UidBox("B:sir_scale_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s_n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_scale_exp.i_n"),
             box=UidBox("B:sir_scale_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i_n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_scale_exp.r_n"),
             box=UidBox("B:sir_scale_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="r_n",
             value=None, metadata=None),
        # sir_scale_exp out
        Port(uid=UidPort("P:sir_scale_exp.scale"),
             box=UidBox("B:sir_scale_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="scale",
             value=None, metadata=None),

        # sir_s_exp in
        Port(uid=UidPort("P:sir_s_exp.s_n"),
             box=UidBox("B:sir_s_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="s_n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_s_exp.scale"),
             box=UidBox("B:sir_s_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="scale",
             value=None, metadata=None),
        # sir_s_exp out
        Port(uid=UidPort("P:sir_s_exp.s"),
             box=UidBox("B:sir_s_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="s",
             value=None, metadata=None),

        # sir_i_exp in
        Port(uid=UidPort("P:sir_i_exp.i_n"),
             box=UidBox("B:sir_i_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="i_n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_i_exp.scale"),
             box=UidBox("B:sir_i_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="scale",
             value=None, metadata=None),
        # sir_i_exp out
        Port(uid=UidPort("P:sir_i_exp.i"),
             box=UidBox("B:sir_i_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="i",
             value=None, metadata=None),

        # sir_r_exp in
        Port(uid=UidPort("P:sir_r_exp.r_n"),
             box=UidBox("B:sir_r_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="r_n",
             value=None, metadata=None),
        Port(uid=UidPort("P:sir_r_exp.scale"),
             box=UidBox("B:sir_r_exp"),
             type=UidType("PortInput"),
             value_type=UidType("Float"),
             name="scale",
             value=None, metadata=None),
        # sir_r_exp out
        Port(uid=UidPort("P:sir_r_exp.r"),
             box=UidBox("B:sir_r_exp"),
             type=UidType("PortOutput"),
             value_type=UidType("Float"),
             name="r",
             value=None, metadata=None),
    ]

    # -- sim_sir() Expressions and Function --

    # todo CTM: using as stub
    simsir = Function(uid=UidBox("B:simsir"),
                      type=None,
                      name=UidOp("sim_sir-a"),  # todo
                      ports=[UidPort("P:simsir.in.s"),
                             UidPort("P:simsir.out.s")],

                      # contents
                      wires=[UidWire("W:simsir.in.s>sir.in.s"),  # todo update when updating simsir
                             UidWire("W:sir.out.s>simsir.out.s")  # todo update when updating simsir
                             ],
                      boxes=[UidBox("B:sir")],  # todo: update once outer loop complete
                      junctions=None,

                      metadata=None)

    # -- sir() --

    # Expression sir_s_n_exp
    # e1 = (* -1 beta i s) -> e1
    e1 = Expr(call=RefOp(UidOp('*')),
              args=[Literal(uid=None, type=UidType("Int"), value=Val("-1"),
                            name=None, metadata=None),
                    UidPort("P:sir_s_n_exp.beta"),
                    UidPort("P:sir_s_n_exp.s"),
                    UidPort("P:sir_s_n_exp.i")])
    # e2 = (+ e1 s) -> e2
    e2 = Expr(call=RefOp(UidOp('+')),
              args=[e1, UidPort("P:sir_s_n_exp.s")])
    sir_s_n_exp = Expression(uid=UidBox("B:sir_s_n_exp"),
                             type=None,
                             name=None,
                             ports=[UidPort("P:sir_s_n_exp.beta"),
                                    UidPort("P:sir_s_n_exp.s"),
                                    UidPort("P:sir_s_n_exp.i"),
                                    UidPort("P:sir_s_n_exp.s_n")],
                             tree=e2,
                             metadata=None)

    # Expression sir_i_n_exp
    # e3 = (* beta s i) -> e3
    e3 = Expr(call=RefOp(UidOp('*')),
              args=[UidPort("P:sir_i_n_exp.beta"),
                    UidPort("P:sir_i_n_exp.s"),
                    UidPort("P:sir_i_n_exp.i")])
    # e4 = (* -1 i gamma) -> e4
    e4 = Expr(call=RefOp(UidOp('*')),
              args=[Literal(uid=None, type=UidType("Int"), value=Val("-1"),
                            name=None, metadata=None),
                    UidPort("P:sir_i_n_exp.i"),
                    UidPort("P:sir_i_n_exp.gamma")])
    # e5 = (+ e3 e4 i)
    e5 = Expr(call=RefOp(UidOp('+')),
              args=[e3, e4, UidPort("P:sir_i_n_exp.i")])
    sir_i_n_exp = Expression(uid=UidBox("B:sir_i_n_exp"),
                             type=None,
                             name=None,
                             ports=[UidPort("P:sir_i_n_exp.beta"),
                                    UidPort("P:sir_i_n_exp.s"),
                                    UidPort("P:sir_i_n_exp.i"),
                                    UidPort("P:sir_i_n_exp.gamma"),
                                    UidPort("P:sir_i_n_exp.i_n")],
                             tree=e5,
                             metadata=None)

    # Expression sir_r_n_exp
    # e6 = (* gamma i r) -> e6
    e6 = Expr(call=RefOp(UidOp('*')),
              args=[UidPort("P:sir_r_n_exp.gamma"),
                    UidPort("P:sir_r_n_exp.i"),
                    UidPort("P:sir_r_n_exp.r")])
    # e7 = (+ e6 r) -> e7
    e7 = Expr(call=RefOp(UidOp('+')),
              args=[e6, UidPort("P:sir_r_n_exp.r")])
    sir_r_n_exp = Expression(uid=UidBox("B:sir_r_n_exp"),
                             type=None,
                             name=None,
                             ports=[UidPort("P:sir_r_n_exp.gamma"),
                                    UidPort("P:sir_r_n_exp.i"),
                                    UidPort("P:sir_r_n_exp.r"),
                                    UidPort("P:sir_r_n_exp.r_n")],
                             tree=e7,
                             metadata=None)

    # Expression sir_scale_exp
    # e8 = (+ s_n i_n r_n) -> e8
    e8 = Expr(call=RefOp(UidOp('+')),
              args=[UidPort("P:sir_scale_exp.s_n"),
                    UidPort("P:sir_scale_exp.i_n"),
                    UidPort("P:sir_scale_exp.r_n")])
    # e9 = (/ n e8)
    e9 = Expr(call=RefOp(UidOp('/')),
              args=[UidPort("P:sir_scale_exp.n"),
                    e8])
    sir_scale_exp = Expression(uid=UidBox("B:sir_scale_exp"),
                               type=None,
                               name=None,
                               ports=[UidPort("P:sir_scale_exp.n"),
                                      UidPort("P:sir_scale_exp.s_n"),
                                      UidPort("P:sir_scale_exp.i_n"),
                                      UidPort("P:sir_scale_exp.r_n"),
                                      UidPort("P:sir_scale_exp.scale")],
                               tree=e9,
                               metadata=None)

    # Expression sir_s_exp
    # e10 = (* s_n scale) -> e10
    e10 = Expr(call=RefOp(UidOp('*')),
               args=[UidPort("P:sir_s_exp.s_n"),
                     UidPort("P:sir_s_exp.scale")])
    sir_s_exp = Expression(uid=UidBox("B:sir_s_exp"),
                           type=None,
                           name=None,
                           ports=[UidPort("P:sir_s_exp.s_n"),
                                  UidPort("P:sir_s_exp.scale"),
                                  UidPort("P:sir_s_exp.s")],
                           tree=e10,
                           metadata=None)

    # Expression sir_i_exp
    # e11 = (* i_n scale) -> e11
    e11 = Expr(call=RefOp(UidOp('*')),
               args=[UidPort("P:sir_i_exp.i_n"),
                     UidPort("P:sir_i_exp.scale")])
    sir_i_exp = Expression(uid=UidBox("B:sir_i_exp"),
                           type=None,
                           name=None,
                           ports=[UidPort("P:sir_i_exp.i_n"),
                                  UidPort("P:sir_i_exp.scale"),
                                  UidPort("P:sir_i_exp.i")],
                           tree=e11,
                           metadata=None)

    # Expression sir_r_exp
    # e12 = (* r_n scale) -> e12
    e12 = Expr(call=RefOp(UidOp('*')),
               args=[UidPort("P:sir_r_exp.r_n"),
                     UidPort("P:sir_r_exp.scale")])
    sir_r_exp = Expression(uid=UidBox("B:sir_r_exp"),
                           type=None,
                           name=None,
                           ports=[UidPort("P:sir_r_exp.r_n"),
                                  UidPort("P:sir_r_exp.scale"),
                                  UidPort("P:sir_r_exp.r")],
                           tree=e12,
                           metadata=None)

    # Function sir
    sir = Function(uid=UidBox("B:sir"),
                   type=None,
                   name=UidOp("sir"),
                   ports=[UidPort("P:sir.n"),
                          UidPort("P:sir.in.beta"),
                          UidPort("P:sir.in.gamma"),
                          UidPort("P:sir.in.s"),
                          UidPort("P:sir.in.r"),
                          UidPort("P:sir.in.r"),
                          UidPort("P:sir.out.s"),
                          UidPort("P:sir.out.i"),
                          UidPort("P:sir.out.r")],

                   # contents
                   wires=[UidWire("W:sir.n>sir_scale_exp.n"),
                          UidWire("W:sir.beta>sir_s_n_exp.beta"),
                          UidWire("W:sir.beta>sir_i_n_exp.beta"),
                          UidWire("W:sir.gamma>sir_i_n_exp.gamma"),
                          UidWire("W:sir.gamma>sir_r_n_exp.gamma"),
                          UidWire("W:sir.s_in>sir_s_n_exp.s"),
                          UidWire("W:sir.s_in>sir_i_n_exp.s"),
                          UidWire("W:sir.i_in>sir_s_n_exp.i"),
                          UidWire("W:sir.i_in>sir_i_n_exp.i"),
                          UidWire("W:sir.i_in>sir_r_n_exp.i"),
                          UidWire("W:sir.r_in>sir_r_n_exp.r"),
                          UidWire("W:sir_s_n_exp.s_n>sir_scale_exp.s_n"),
                          UidWire("W:sir_s_n_exp.s_n>sir_s_exp.s_n"),
                          UidWire("W:sir_i_n_exp.i_n>sir_scale_exp.i_n"),
                          UidWire("W:sir_i_n_exp.i_n>sir_i_exp.i_n"),
                          UidWire("W:sir_r_n_exp.r_n>sir_scale_exp.r_n"),
                          UidWire("W:sir_r_n_exp.r_n>sir_r_exp.r_n"),
                          UidWire("W:sir_scale_exp.scale>sir_s_exp.scale"),
                          UidWire("W:sir_scale_exp.scale>sir_i_exp.scale"),
                          UidWire("W:sir_scale_exp.scale>sir_r_exp.scale"),
                          UidWire("W:sir_s_exp.s>sir.s_out"),
                          UidWire("W:sir_i_exp.i>sir.i_out"),
                          UidWire("W:sir_r_exp.r>sir.r_out")],
                   boxes=[UidBox("B:sir_s_n_exp"),
                          UidBox("B:sir_i_n_exp"),
                          UidBox("B:sir_r_n_exp"),
                          UidBox("B:sir_scale_exp"),
                          UidBox("B:sir_s_exp"),
                          UidBox("B:sir_i_exp"),
                          UidBox("B:sir_r_exp")],
                   junctions=None,

                   metadata=None)

    boxes = [simsir,
             sir,
             sir_s_n_exp, sir_i_n_exp, sir_r_n_exp,
             sir_scale_exp,
             sir_s_exp, sir_i_exp, sir_r_exp]

    _g = Gromet(
        uid=UidGromet("CHIME_SIR_01a"),
        name="CHIME_SIR_01a",
        type=UidType("FunctionNetwork"),
        root=UidBox("B:simsir"),  # TODO Update with latest root
        types=None,
        literals=None,
        junctions=None,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=[chime_model_description,
                  chime_model_interface
                  ]
    )

    return _g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
