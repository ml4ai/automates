from gromet_intersection_graph import *


# -----------------------------------------------------------------------------
# GroMEt instance
# -----------------------------------------------------------------------------

def generate_gig() -> GrometIntersectionGraph:

    common_nodes = [
        CommonNode(
            uid=UidCommonNode('S_in'),
            type='input',
            g1_variable=UidVariable('S'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('I_in'),
            type='input',
            g1_variable=UidVariable('I'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('R_in'),
            type='input',
            g1_variable=UidVariable('R'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('beta'),
            type='input',
            g1_variable=UidVariable('beta'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('gamma'),
            type='input',
            g1_variable=UidVariable('gamma'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('S_out'),
            type='output',
            g1_variable=UidVariable('S_2'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('I_out'),
            type='output',
            g1_variable=UidVariable('I_2'),
            # todo
            g2_variable=UidVariable()
        ),

        CommonNode(
            uid=UidCommonNode('R_out'),
            type='output',
            g1_variable=UidVariable('R_2'),
            # todo
            g2_variable=UidVariable()
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
            # todo
            g2_variables=[]
        ),
    ]

    noap_nodes = [

        NOAPNode(
            uid=UidCommonNode('NOAP_SimpleSIR_1'),
            gromet_name='SimpleSIR_metadata',
            variables=[UidVariable('dt')]
        ),

        NOAPNode(
            uid=UidCommonNode('NOAP_CHIME_1'),
            gromet_name='CHIME_SIR',
            # todo
            variables=[]
        ),

        NOAPNode(
            uid=UidCommonNode('NOAP_CHINE_2'),
            gromet_name='CHIME_SIR',
            # todo
            variables=[]
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
        g2_name='CHIME_SIR',
        g2_uid=UidGromet()  # todo
    )

    gig = GrometIntersectionGraph(
        uid=UidIntersectionGraph('GIG_SimpleSIR>CHIME'),
        gromet_ids=gromet_ids,
        common_nodes=common_nodes,
        oap_nodes=oap_nodes,
        noap_nodes=noap_nodes,
        edges=edges
    )

    return gig


# -----------------------------------------------------------------------------
# Script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    gig_to_json(generate_gig())
