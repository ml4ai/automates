from gromet_intersection_graph import *


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gig() -> GrometIntersectionGraph:

    common_nodes = [
        CommonNode(
            uid=UidCommonNode('S_in'),
            # type='input',
            g1_variable=[UidVariable('S')],
            g2_variable=[UidVariable('V:sir.s_in')]
        ),

        CommonNode(
            uid=UidCommonNode('I_in'),
            # type='input',
            g1_variable=[UidVariable('I')],
            g2_variable=[UidVariable('V:sir.i_in')]
        ),

        CommonNode(
            uid=UidCommonNode('R_in'),
            # type='input',
            g1_variable=[UidVariable('R')],
            g2_variable=[UidVariable('V:sir.r_in')]
        ),

        CommonNode(
            uid=UidCommonNode('beta'),
            # type='input',
            g1_variable=[UidVariable('beta')],
            g2_variable=[UidVariable('V:sir.beta')]
        ),

        CommonNode(
            uid=UidCommonNode('gamma'),
            # type='input',
            g1_variable=[UidVariable('gamma')],
            g2_variable=[UidVariable('V:sir.gamma')]
        ),

        CommonNode(
            uid=UidCommonNode('S_out'),
            # type='output',
            g1_variable=[UidVariable('S_2')],
            g2_variable=[UidVariable('V:sir.s_out')]
        ),

        CommonNode(
            uid=UidCommonNode('I_out'),
            # type='output',
            g1_variable=[UidVariable('I_2')],
            g2_variable=[UidVariable('V:sir.i_out')]
        ),

        CommonNode(
            uid=UidCommonNode('R_out'),
            # type='output',
            g1_variable=[UidVariable('R_2')],
            g2_variable=[UidVariable('V:sir.r_out')]
        ),
    ]

    oap_nodes = [
        OAPNode(
            uid=UidCommonNode('OAP_1'),
            g1_variables=[
                UidVariable('infected'),
                UidVariable('recovered'),
                UidVariable('dt')
            ],
            g2_variables=[
                UidVariable('V:sir.n'),
                UidVariable('V:sir.s_n'),
                UidVariable('V:sir.i_n'),
                UidVariable('V:sir.r_n'),
                UidVariable('V:sir.scale'),
            ]
        ),
    ]

    edges = [
        Edge(
            type='no_overlap',
            src=UidCommonNode('S_in'),
            dst=UidCommonNode('OAP_1')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('I_in'),
            dst=UidCommonNode('OAP_1')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('R_in'),
            dst=UidCommonNode('OAP_1')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('beta'),
            dst=UidCommonNode('OAP_1')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('gamma'),
            dst=UidCommonNode('OAP_1')
        ),

        Edge(
            type='no_overlap',
            src=UidCommonNode('OAP_1'),
            dst=UidCommonNode('S_out')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('OAP_1'),
            dst=UidCommonNode('I_out')
        ),
        Edge(
            type='no_overlap',
            src=UidCommonNode('OAP_1'),
            dst=UidCommonNode('R_out')
        )
    ]

    gromet_ids = GrometIds(
        g1_name='SimpleSIR_metadata',
        g1_uid=UidGromet('SimpleSIR_FN'),
        g2_name='CHIME_SIR_v01',
        g2_uid=UidGromet('CHIME_SIR')
    )

    gig = GrometIntersectionGraph(
        uid=UidIntersectionGraph('GIG.Simple_SIR>CHIME_SIR_v01'),
        gromet_ids=gromet_ids,
        common_nodes=common_nodes,
        oap_nodes=oap_nodes,
        noap_nodes=None,
        edges=edges
    )

    return gig


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gig_to_json(generate_gig())
