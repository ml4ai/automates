from gromet import *  # never do this :)


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gromet() -> Gromet:

    variables = []

    wires = [
        # sir
        Wire(uid=UidWire("W:sir.S.JS"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.S"),
             tgt=UidJunction("J:S")),
        Wire(uid=UidWire("W:sir.I.JI"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.I"),
             tgt=UidJunction("J:I")),
        Wire(uid=UidWire("W:sir.R.JR"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.R"),
             tgt=UidJunction("J:R")),

        Wire(uid=UidWire("W:sir.beta.inf_beta"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.beta"),
             tgt=UidPort("P:event_inf.beta")),
        Wire(uid=UidWire("W:sir.gamma.rec_gamma"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:sir.gamma"),
             tgt=UidPort("P:event_rec.gamma")),

        Wire(uid=UidWire("W:sir.JS.inf_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:S"),
             tgt=UidPort("P:event_inf.S")),
        Wire(uid=UidWire("W:sir.JI.inf_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidPort("P:event_inf.I")),
        Wire(uid=UidWire("W:sir.JI.rec_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:I"),
             tgt=UidPort("P:event_rec.I")),
        Wire(uid=UidWire("W:sir.JR.inf_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:R"),
             tgt=UidPort("P:event_inf.R")),
        Wire(uid=UidWire("W:sir.JR.rec_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidJunction("J:R"),
             tgt=UidPort("P:event_rec.R")),

        # event_infection
        Wire(uid=UidWire("W:event_inf_S.enable_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.S"),
             tgt=UidPort("P:event_inf_enable.S")),
        Wire(uid=UidWire("W:event_inf_S.rate_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.S"),
             tgt=UidPort("P:event_inf_rate.S")),
        Wire(uid=UidWire("W:event_inf_S.effect_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.S"),
             tgt=UidPort("P:event_inf_effect.S")),

        Wire(uid=UidWire("W:event_inf_I.enable_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.I"),
             tgt=UidPort("P:event_inf_enable.I")),
        Wire(uid=UidWire("W:event_inf_I.rate_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.I"),
             tgt=UidPort("P:event_inf_rate.I")),
        Wire(uid=UidWire("W:event_inf_I.effect_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.I"),
             tgt=UidPort("P:event_inf_effect.I")),

        Wire(uid=UidWire("W:event_inf_R.rate_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.R"),
             tgt=UidPort("P:event_inf_rate.R")),

        Wire(uid=UidWire("W:event_inf_beta.rate_beta"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf.beta"),
             tgt=UidPort("P:event_inf_rate.beta")),

        # event_infection_enable
        Wire(uid=UidWire("W:event_inf_enable_S.cond_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_enable.S"),
             tgt=UidPort("P:event_inf_enable_S_cond.S")),
        Wire(uid=UidWire("W:event_inf_enable_I.cond_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_enable.I"),
             tgt=UidPort("P:event_inf_enable_I_cond.I")),

        # event_infection_rate
        Wire(uid=UidWire("W:event_inf_rate_S.exp_N_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.S"),
             tgt=UidPort("P:event_inf_rate_exp_N.S")),
        Wire(uid=UidWire("W:event_inf_rate_I.exp_N_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.I"),
             tgt=UidPort("P:event_inf_rate_exp_N.I")),
        Wire(uid=UidWire("W:event_inf_rate_R.exp_N_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.R"),
             tgt=UidPort("P:event_inf_rate_exp_N.R")),

        Wire(uid=UidWire("W:event_inf_rate_S.exp_rate_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.S"),
             tgt=UidPort("P:event_inf_rate_exp_rate.S")),
        Wire(uid=UidWire("W:event_inf_rate_I.exp_rate_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.I"),
             tgt=UidPort("P:event_inf_rate_exp_rate.I")),
        Wire(uid=UidWire("W:event_inf_rate_beta.exp_rate_beta"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate.beta"),
             tgt=UidPort("P:event_inf_rate_exp_rate.beta")),
        Wire(uid=UidWire("W:event_inf_rate_N.exp_rate_N"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_rate_exp_N.N"),
             tgt=UidPort("P:event_inf_rate_exp_rate.N")),

        # event_infection_effect
        Wire(uid=UidWire("W:event_inf_effect_S.expS_S"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_effect.S"),
             tgt=UidPort("P:event_inf_effect_expS.S")),
        Wire(uid=UidWire("W:event_inf_effect_I.expI_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_effect.I"),
             tgt=UidPort("P:event_inf_effect_expI.I")),
        Wire(uid=UidWire("W:event_inf_effect_S'.expS_S'"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_effect.S'"),
             tgt=UidPort("P:event_inf_effect_expS.S'")),
        Wire(uid=UidWire("W:event_inf_effect_I'.expI_I'"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_inf_effect.I'"),
             tgt=UidPort("P:event_inf_effect_expI.I'")),

        # event_recovered
        Wire(uid=UidWire("W:event_rec_I.enable_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec.I"),
             tgt=UidPort("P:event_rec_enable.I")),
        Wire(uid=UidWire("W:event_rec_I.rate_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec.I"),
             tgt=UidPort("P:event_rec_rate.I")),
        Wire(uid=UidWire("W:event_rec_I.effect_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec.I"),
             tgt=UidPort("P:event_rec_effect.I")),
        Wire(uid=UidWire("W:event_rec_R.effect_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec.R"),
             tgt=UidPort("P:event_rec_effect.R")),
        Wire(uid=UidWire("W:event_rec_gamma.rate_gamma"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec.gamma"),
             tgt=UidPort("P:event_rec_rate.gamma")),

        # event_recovered_enable
        Wire(uid=UidWire("W:event_rec_enable_I.cond_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_enable.I"),
             tgt=UidPort("P:event_rec_enable_I_cond.I")),

        # event_recovered_rate
        Wire(uid=UidWire("W:event_rec_rate_I.exp_rate_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_rate.I"),
             tgt=UidPort("P:event_rec_rate_exp_rate.I")),
        Wire(uid=UidWire("W:event_rec_rate_gamma.exp_rate_gamma"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_rate.gamma"),
             tgt=UidPort("P:event_rec_rate_exp_rate.gamma")),

        # event_recovered_effect
        Wire(uid=UidWire("W:event_rec_effect_I.expI_I"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_effect.I"),
             tgt=UidPort("P:event_rec_effect_expI.I")),
        Wire(uid=UidWire("W:event_rec_effect_R.expR_R"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_effect.R"),
             tgt=UidPort("P:event_rec_effect_expR.R")),
        Wire(uid=UidWire("W:event_rec_effect_I'.expI_I'"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_effect.I'"),
             tgt=UidPort("P:event_rec_effect_expI.I'")),
        Wire(uid=UidWire("W:event_rec_effect_R'.expR_R'"),
             type=UidType("T:Undirected"),
             value_type=UidType("Real"),
             name=None, value=None, metadata=None,
             src=UidPort("P:event_rec_effect.R'"),
             tgt=UidPort("P:event_rec_effect_expR.R'")),
    ]

    ports = [
        # sir
        Port(uid=UidPort("P:sir.S"), box=UidBox("B:sir"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:sir.I"), box=UidBox("B:sir"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:sir.R"), box=UidBox("B:sir"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:sir.beta"), box=UidBox("B:sir"),
             name="beta", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:sir.gamma"), box=UidBox("B:sir"),
             name="gamma", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection
        Port(uid=UidPort("P:event_inf.S"), box=UidBox("B:event_infection"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf.I"), box=UidBox("B:event_infection"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf.R"), box=UidBox("B:event_infection"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf.beta"), box=UidBox("B:event_infection"),
             name="beta", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_enable
        Port(uid=UidPort("P:event_inf_enable.S"), box=UidBox("B:event_infection_enable"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_enable.I"), box=UidBox("B:event_infection_enable"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_enable_S_cond
        Port(uid=UidPort("P:event_inf_enable_S_cond.S"),
             box=UidBox("B:event_inf_enable_S_cond"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_infection_enable_I_cond
        Port(uid=UidPort("P:event_inf_enable_I_cond.I"),
             box=UidBox("B:event_inf_enable_I_cond"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_rate
        Port(uid=UidPort("P:event_inf_rate.S"), box=UidBox("B:event_infection_rate"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate.I"), box=UidBox("B:event_infection_rate"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate.R"), box=UidBox("B:event_infection_rate"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate.beta"), box=UidBox("B:event_infection_rate"),
             name="beta", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_rate_exp_N
        Port(uid=UidPort("P:event_inf_rate_exp_N.S"), box=UidBox("B:event_infection_rate_exp_N"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_N.I"), box=UidBox("B:event_infection_rate_exp_N"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_N.R"), box=UidBox("B:event_infection_rate_exp_N"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_N.N"), box=UidBox("B:event_infection_rate_exp_N"),
             name="N", type=UidType("T:Output"),  # the output of the Expression
             value_type=UidType("Real"), value=None, metadata=None),
        # event_infection_rate_exp_rate
        Port(uid=UidPort("P:event_inf_rate_exp_rate.S"), box=UidBox("B:event_infection_rate_exp_rate"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_rate.I"), box=UidBox("B:event_infection_rate_exp_rate"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_rate.N"), box=UidBox("B:event_infection_rate_exp_rate"),
             name="N", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_rate_exp_rate.beta"), box=UidBox("B:event_infection_rate_exp_rate"),
             name="beta", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_effect
        Port(uid=UidPort("P:event_inf_effect.S"), box=UidBox("B:event_infection_effect"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_effect.I"), box=UidBox("B:event_infection_effect"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_effect.S'"), box=UidBox("B:event_infection_effect"),
             name="S'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_effect.I'"), box=UidBox("B:event_infection_effect"),
             name="I'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_infection_effect_exp_S
        Port(uid=UidPort("P:event_inf_effect_expS.S"), box=UidBox("B:event_infection_effect_exp_S"),
             name="S", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_effect_expS.S'"), box=UidBox("B:event_infection_effect_exp_S"),
             name="S'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_infection_effect_exp_I
        Port(uid=UidPort("P:event_inf_effect_expI.I"), box=UidBox("B:event_infection_effect_exp_I"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_inf_effect_expI.I'"), box=UidBox("B:event_infection_effect_exp_I"),
             name="I'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_recovered
        Port(uid=UidPort("P:event_rec.I"), box=UidBox("B:event_recovered"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec.R"), box=UidBox("B:event_recovered"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec.gamma"), box=UidBox("B:event_recovered"),
             name="gamma", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_recovered_enable
        Port(uid=UidPort("P:event_rec_enable.I"), box=UidBox("B:event_recovered_enable"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_recovered_enable_I_cond
        Port(uid=UidPort("P:event_rec_enable_I_cond.I"),
             box=UidBox("B:event_rec_enable_I_cond"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_recovered_rate
        Port(uid=UidPort("P:event_rec_rate.I"), box=UidBox("B:event_recovered_rate"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_rate.gamma"), box=UidBox("B:event_recovered_rate"),
             name="gamma", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_recovered_rate_exp_rate
        Port(uid=UidPort("P:event_rec_rate_exp_rate.I"), box=UidBox("B:event_recovered_rate_exp_rate"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_rate_exp_rate.gamma"), box=UidBox("B:event_recovered_rate_exp_rate"),
             name="gamma", type=UidType("T:Parameter"),
             value_type=UidType("Real"), value=None, metadata=None),

        # event_recovered_effect
        Port(uid=UidPort("P:event_rec_effect.I"), box=UidBox("B:event_recovered_effect"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_effect.R"), box=UidBox("B:event_recovered_effect"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_effect.I'"), box=UidBox("B:event_recovered_effect"),
             name="I'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_effect.R'"), box=UidBox("B:event_recovered_effect"),
             name="R'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_recovered_effect_exp_I
        Port(uid=UidPort("P:event_rec_effect_expI.I"), box=UidBox("B:event_recovered_effect_exp_I"),
             name="I", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_effect_expI.I'"), box=UidBox("B:event_recovered_effect_exp_I"),
             name="I'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        # event_recovered_effect_exp_R
        Port(uid=UidPort("P:event_rec_effect_expR.R"), box=UidBox("B:event_recovered_effect_exp_R"),
             name="R", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None),
        Port(uid=UidPort("P:event_rec_effect_expR.R'"), box=UidBox("B:event_recovered_effect_exp_R"),
             name="R'", type=UidType("T:Variable"),
             value_type=UidType("Real"), value=None, metadata=None)
    ]

    junctions = [
        Junction(uid=UidJunction("J:S"),
                 name="S", type=UidType("T:State"),
                 value_type=UidType("Real"), value=None,
                 metadata=None),
        Junction(uid=UidJunction("J:I"),
                 name="I", type=UidType("T:State"),
                 value_type=UidType("Real"), value=None,
                 metadata=None),
        Junction(uid=UidJunction("J:R"),
                 name="R", type=UidType("T:State"),
                 value_type=UidType("Real"), value=None,
                 metadata=None)
    ]

    # ==== Event Infected ====

    # -- event_infection_enable --

    # Expressions event_inf_enable
    # S condition
    e1 = Expr(call=RefOp(UidOp(">")),
              args=[UidPort("P:event_inf_enable_S_cond.S"),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType("Real"), value=Val("0"))])
    event_infection_enable_exp_S_cond = Expression(
        uid=UidBox("B:event_inf_enable_S_cond"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_enable_S_cond.S")],
        tree=e1,
        metadata=None)
    # I condition
    e2 = Expr(call=RefOp(UidOp(">")),
              args=[UidPort("P:event_inf_enable_I_cond.I"),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType("Real"), value=Val("0"))])
    event_infection_enable_exp_I_cond = Expression(
        uid=UidBox("B:event_inf_enable_I_cond"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_enable_I_cond.I")],
        tree=e2,
        metadata=None)

    event_infection_enable = Relation(
        uid=UidBox("B:event_infection_enable"),
        type=UidType("T:Enable"),
        name="Event_infection_enable",
        ports=[UidPort("P:event_inf_enable.S"), UidPort("P:event_inf_enable.I")],
        boxes=[UidBox("B:event_inf_enable_S_cond"),
               UidBox("B:event_inf_enable_I_cond")],
        wires=[UidWire("W:event_inf_enable_S.cond_S"),
               UidWire("W:event_inf_enable_I.cond_I")],
        junctions=None,
        metadata=None
    )

    # -- event_infection_rate --

    # Expressions event_inf_rate
    # N
    e3 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:event_inf_rate_exp_N.S"),
                    UidPort("P:event_inf_rate_exp_N.I"),
                    UidPort("P:event_inf_rate_exp_N.R")])
    event_infection_rate_exp_N = Expression(
        uid=UidBox("B:event_infection_rate_exp_N"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_rate_exp_N.S"),
               UidPort("P:event_inf_rate_exp_N.I"),
               UidPort("P:event_inf_rate_exp_N.R"),
               UidPort("P:event_inf_rate_exp_N.N")],
        tree=e3,
        metadata=None
    )
    # rate
    e4 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort("P:event_inf_rate_exp_rate.S"),
                    UidPort("P:event_inf_rate_exp_rate.I"),
                    UidPort("P:event_inf_rate_exp_rate.beta")])
    e5 = Expr(call=RefOp(UidOp("/")),
              args=[e4, UidPort("P:event_inf_rate_exp_rate.N")])
    event_infection_rate_exp_rate = Expression(
        uid=UidBox("B:event_infection_rate_exp_rate"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_rate_exp_rate.S"),
               UidPort("P:event_inf_rate_exp_rate.I"),
               UidPort("P:event_inf_rate_exp_rate.N"),
               UidPort("P:event_inf_rate_exp_rate.beta")],
        tree=e5,
        metadata=None
    )

    event_infection_rate = Relation(
        uid=UidBox("B:event_infection_rate"),
        type=UidType("T:Rate"),
        name="Event_infection_rate",
        ports=[UidPort("P:event_inf_rate.S"), UidPort("P:event_inf_rate.I"), UidPort("P:event_inf_rate.R"),
               UidPort("P:event_inf_rate.beta")],
        wires=[UidWire("W:event_inf_rate_S.exp_N_S"),
               UidWire("W:event_inf_rate_I.exp_N_I"),
               UidWire("W:event_inf_rate_R.exp_N_R"),
               UidWire("W:event_inf_rate_S.exp_rate_S"),
               UidWire("W:event_inf_rate_I.exp_rate_I"),
               UidWire("W:event_inf_rate_beta.exp_rate_beta"),
               UidWire("W:event_inf_rate_N.exp_rate_N")],
        junctions=None,
        boxes=[UidBox("B:event_infection_rate_exp_N"),
               UidBox("B:event_infection_rate_exp_rate")],
        metadata=None
    )

    # -- event_infection_effect --

    # Expressions event_inf_effect
    # S
    e6 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:event_inf_effect_expS.S"),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType("Integer"), value=Val("-1"))])
    event_inf_effect_exp_S = Expression(
        uid=UidBox("B:event_infection_effect_exp_S"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_effect_expS.S"),
               UidPort("P:event_inf_effect_expS.S'")],
        tree=e6,
        metadata=None
    )
    # I
    e7 = Expr(call=RefOp(UidOp("+")),
              args=[UidPort("P:event_inf_effect_expI.I"),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType("Integer"), value=Val("1"))])
    event_inf_effect_exp_I = Expression(
        uid=UidBox("B:event_infection_effect_exp_I"),
        type=None, name=None,
        ports=[UidPort("P:event_inf_effect_expI.I"),
               UidPort("P:event_inf_effect_expI.I'")],
        tree=e7,
        metadata=None
    )

    event_infection_effect = Relation(
        uid=UidBox("B:event_infection_effect"),
        type=UidType("T:Effect"),
        name="Event_infection_effect",
        ports=[UidPort("P:event_inf_effect.S"),
               UidPort("P:event_inf_effect.I"),
               UidPort("P:event_inf_effect.S'"),
               UidPort("P:event_inf_effect.I'")],
        wires=[UidWire("W:event_inf_effect_S.expS_S"),
               UidWire("W:event_inf_effect_I.expI_I"),
               UidWire("W:event_inf_effect_S'.expS_S'"),
               UidWire("W:event_inf_effect_I'.expI_I'")],
        junctions=None,
        boxes=[UidBox("B:event_infection_effect_exp_S"),
               UidBox("B:event_infection_effect_exp_I")],
        metadata=None
    )

    # -- event_infection --

    event_infection = Relation(
        uid=UidBox("B:event_infection"),
        type=UidType("T:Event"),
        name="Event_infection",
        ports=[UidPort("P:event_inf.S"), UidPort("P:event_inf.I"), UidPort("P:event_inf.R"),
               UidPort("P:event_inf.beta")],
        wires=[UidWire("W:event_inf_S.enable_S"),
               UidWire("W:event_inf_S.rate_S"),
               UidWire("W:event_inf_S.effect_S"),
               UidWire("W:event_inf_I.enable_I"),
               UidWire("W:event_inf_I.rate_I"),
               UidWire("W:event_inf_I.effect_I"),
               UidWire("W:event_inf_R.rate_R"),
               UidWire("W:event_inf_beta.rate_beta")],
        junctions=None,
        boxes=[UidBox("B:event_infection_enable"),
               UidBox("B:event_infection_rate"),
               UidBox("B:event_infection_effect")],
        metadata=None
    )

    # ==== Event Recovered ====

    # -- event_recovered_enable --

    # Expressions event_rec_enable
    # I cond
    e8 = Expr(call=RefOp(UidOp(">")),
              args=[UidPort("P:event_inf_enable_I_cond.I"),
                    Literal(uid=None, name=None, metadata=None,
                            type=UidType("Real"), value=Val("0"))])
    event_recovered_enable_exp_I_cond = Expression(
        uid=UidBox("B:event_rec_enable_I_cond"),
        type=None, name=None,
        ports=[UidPort("P:event_rec_enable_I_cond.I")],
        tree=e8,
        metadata=None)

    event_recovered_enable = Relation(
        uid=UidBox("B:event_recovered_enable"),
        type=UidType("T:Enable"),
        name="Event_recovered_enable",
        ports=[UidPort("P:event_rec_enable.I")],
        wires=[UidWire("W:event_rec_enable_I.cond_I")],
        junctions=None,
        boxes=[UidBox("B:event_rec_enable_I_cond")],
        metadata=None)

    # -- event_recovered_rate --

    # Expression event_rec_rate
    # rate
    e9 = Expr(call=RefOp(UidOp("*")),
              args=[UidPort("P:event_rec_rate_exp_rate.I"),
                    UidPort("P:event_rec_rate_exp_rate.gamma")])
    event_recovered_rate_exp_rate = Expression(
        uid=UidBox("B:event_recovered_rate_exp_rate"),
        type=None, name=None,
        ports=[UidPort("P:event_rec_rate_exp_rate.I"),
               UidPort("P:event_rec_rate_exp_rate.gamma")],
        tree=e9,
        metadata=None
    )

    event_recovered_rate = Relation(
        uid=UidBox("B:event_recovered_rate"),
        type=UidType("T:Rate"),
        name="Event_recovered_rate",
        ports=[UidPort("P:event_rec_rate.I"),
               UidPort("P:event_rec_rate.gamma")],
        wires=[UidWire("W:event_rec_rate_I.exp_rate_I"),
               UidWire("W:event_rec_rate_gamma.exp_rate_gamma")],
        junctions=None,
        boxes=[UidBox("B:event_recovered_rate_exp_rate")],
        metadata=None
    )

    # -- event_recovered_effect --

    # Expression event_rec_effect
    # I
    e10 = Expr(call=RefOp(UidOp("+")),
               args=[UidPort("P:event_rec_effect_expI.I"),
                     Literal(uid=None, name=None, metadata=None,
                             type=UidType("Integer"), value=Val("-1"))])
    event_rec_effect_exp_I = Expression(
        uid=UidBox("B:event_recovered_effect_exp_I"),
        type=None, name = None,
        ports=[UidPort("P:event_rec_effect_expI.I"),
               UidPort("P:event_rec_effect_expI.I'")],
        tree=e10,
        metadata=None
    )
    # R
    e11 = Expr(call=RefOp(UidOp("+")),
               args=[UidPort("P:event_rec_effect_expR.R"),
                     Literal(uid=None, name=None, metadata=None,
                             type=UidType("Integer"), value=Val("1"))])
    event_rec_effect_exp_R = Expression(
        uid=UidBox("B:event_recovered_effect_exp_R"),
        type=None, name=None,
        ports=[UidPort("P:event_rec_effect_expR.R"),
               UidPort("P:event_rec_effect_expR.R'")],
        tree=e11,
        metadata=None
    )

    event_recovered_effect = Relation(
        uid=UidBox("B:event_recovered_effect"),
        type=UidType("T:Effect"),
        name="Event_recovered_effect",
        ports=[UidPort("P:event_rec_effect.I"),
               UidPort("P:event_rec_effect.R"),
               UidPort("P:event_rec_effect.I'"),
               UidPort("P:event_rec_effect.R'")],
        wires=[UidWire("W:event_rec_effect_I.expI_I"),
               UidWire("W:event_rec_effect_R.expR_R"),
               UidWire("W:event_rec_effect_I'.expI_I'"),
               UidWire("W:event_rec_effect_R'.expR_R'")],
        junctions=None,
        boxes=[UidBox("B:event_recovered_effect_exp_I"),
               UidBox("B:event_recovered_effect_exp_R")],
        metadata=None
    )

    event_recovered = Relation(
        uid=UidBox("B:event_recovered"),
        type=UidType("T:Event"),
        name="Event_recovered",
        ports=[UidPort("P:event_rec.I"), UidPort("P:event_rec.R"),
               UidPort("P:event_rec.gamma")],
        wires=[UidWire("W:event_rec_I.enable_I"),
               UidWire("W:event_rec_I.rate_I"),
               UidWire("W:event_rec_I.effect_I"),
               UidWire("W:event_rec_R.effect_R"),
               UidWire("W:event_rec_gamma.rate_gamma")],
        junctions=None,
        boxes=[UidBox("B:event_recovered_enable"),
               UidBox("B:event_recovered_rate"),
               UidBox("B:event_recovered_effect")],
        metadata=None
    )

    # ==== Top level SIR model ====

    sir = Relation(
        uid=UidBox("B:sir"),
        type=UidType("PrTNet"),
        name="SimpleSIR",
        ports=[UidPort("P:sir.S"), UidPort("P:sir.I"), UidPort("P:sir.R"),
               UidPort("P:sir.beta"), UidPort("P:sir.gamma")],
        wires=[UidWire("W:sir.S.JS"), UidWire("W:sir.I.JI"), UidWire("W:sir.R.JR"),
               UidWire("W:sir.beta.inf_beta"), UidWire("W:sir.gamma.rec_gamma"),
               UidWire("W:sir.JS.inf_S"),
               UidWire("W:sir.JI.inf_I"), UidWire("W:sir.JI.rec_I"),
               UidWire("W:sir.JR.inf_R"), UidWire("W:sir.JR.rec_R"),
               ],
        junctions=[UidJunction("J:S"), UidJunction("J:I"), UidJunction("J:R")],
        boxes=[UidBox("B:event_infection"), UidBox("B:event_recovered")],
        metadata=None
    )

    boxes = [sir,
             event_infection, event_infection_enable, event_infection_rate, event_infection_effect,
             event_infection_enable_exp_S_cond, event_infection_enable_exp_I_cond,
             event_infection_rate_exp_N, event_infection_rate_exp_rate,
             event_inf_effect_exp_S, event_inf_effect_exp_I,
             event_recovered, event_recovered_enable, event_recovered_rate, event_recovered_effect,
             event_recovered_enable_exp_I_cond,
             event_recovered_rate_exp_rate,
             event_rec_effect_exp_I, event_rec_effect_exp_R
             ]

    g = Gromet(
        uid=UidGromet("SimpleSIR_PrTNet"),
        name="SimpleSIR",
        type=UidType("PrTNet"),
        root=sir.uid,
        types=None,
        literals=None,
        junctions=junctions,
        ports=ports,
        wires=wires,
        boxes=boxes,
        variables=variables,
        metadata=None
    )

    return g


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gromet_to_json(generate_gromet())
