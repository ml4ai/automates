import json
from collections import defaultdict


def load_gromet(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
        return data


def collect_variables(gromet):
    # group by src
    wires = gromet['wires']

    ports = dict()
    if gromet['ports']:
        for p in gromet['ports']:
            ports[p['uid']] = p
    junctions = dict()
    if gromet['junctions']:
        for j in gromet['junctions']:
            junctions[j['uid']] = j

    name_counter = dict()

    def name_index(s):
        if s in name_counter:
            name_counter[s] += 1
        else:
            name_counter[s] = 0
        return name_counter[s]

    groups = dict()

    def update_groups(w):
        wire_uid = w['uid']
        src = w['src']

        tgt = w['tgt']
        tgt_type = None
        if tgt in ports:
            tgt_type = ports[tgt]['type']

        if src in groups:
            group = groups[src]
            group['wire'].append(wire_uid)
            group['tgt'].append((tgt, tgt_type))
        else:
            groups[src] = {'wire': [wire_uid], 'tgt': [(tgt, tgt_type)]}

    for wire in wires:
        update_groups(wire)

    variables = list()
    for key, value in groups.items():
        if len(value['tgt']) == 1 and value['tgt'][0][1] == 'PortOutput':
            # print(f'{key}: {value} >>>> use tgt!')
            proxy_state = value['tgt'][0][0]
        else:
            # print(f'{key}: {value}')
            proxy_state = key
        states = [key] + value['wire'] + list(list(zip(*value['tgt']))[0])
        if proxy_state in ports:
            obj = ports[proxy_state]
        elif proxy_state in junctions:
            obj = junctions[proxy_state]
        name = obj['name']
        name_index_val = name_index(name)
        if name_index_val > 0:
            uid = f'V:{name}_{name_index_val}'
        else:
            uid = f'V:{name}'
        value_type = obj['value_type']
        variables.append({'uid': uid,
                          'proxy_state': proxy_state,
                          'name': name,
                          'type': value_type,
                          'states': states,
                          'metadata': None,
                          'syntax': 'Variable'})

    # print('\n-----')
    for var in variables:
        print(var)

    print(f'total variables: {len(variables)}')

    return variables


# MODEL = 'SimpleSIR_metadata_gromet_FunctionNetwork.json'
# MODEL = 'CHIME_SIR_01_gromet_FunctionNetwork.json'
MODEL = 'CHIME_SIR_01d_gromet_FunctionNetwork.json'

if __name__ == '__main__':
    gromet = load_gromet(MODEL)
    collect_variables(gromet)
