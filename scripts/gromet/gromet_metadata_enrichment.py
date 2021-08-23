import argparse
import json
import copy
import re

from collections import defaultdict


def read_json_file_as_dict(filepath):
    with open(filepath) as f:
        return json.load(f)


def write_json_dict_to_file(d, filepath):
    with open(filepath, "w") as f:
        return json.dump(d, f, indent=2)


def get_port_ids_for_wire(gromet, wire_uid):
    for wire_obj in gromet["wires"]:
        if wire_obj["uid"] == wire_uid:
            return (wire_obj["src"], wire_obj["tgt"])

    raise ValueError(f"Error: Unknown wire uid {wire_uid}")


def get_var_using_port_as_state(gromet, port_uid):
    for var_obj in gromet["variables"]:
        if port_uid in var_obj["states"]:
            return var_obj

    return None


def get_box_by_uid(gromet, uid):
    return [b for b in gromet["boxes"] if b["uid"] == uid][0]


def correct_gromet_scope(box, gromet_scope):
    if gromet_scope == None:
        return

    gromet_scope_corrected = gromet_scope
    if gromet_scope.startswith("simsir"):
        gromet_scope_corrected = gromet_scope_corrected.replace("simsir", "sim_sir")
    if box["syntax"] == "Loop":
        loop_ids = re.findall(r"(_\d)", gromet_scope_corrected)

        gromet_scope_corrected = gromet_scope_corrected.split(f"_loop{loop_ids[0]}")[0]

        # Note this generic increase of loop num doesnt work generally,
        # only because all loop ids in CHIME_SIR are 1 for some reason
        loop_num = 0
        for _ in loop_ids:
            # Should be the int of loop id
            gromet_scope_corrected += f".LOOP_{loop_num}"
            loop_num += 1

    return gromet_scope_corrected


def add_correct_gromet_var_versions_to_grfn_vers(gromet):
    # box_to_min_var = dict()
    box_to_vars = dict()
    seen_vars = set()
    for box in gromet["boxes"]:
        if "wires" in box:
            box_to_vars[box["uid"]] = list()

            for wire in box["wires"] if "wires" in box else []:
                port_uids = get_port_ids_for_wire(gromet, wire)
                for port_uid in port_uids:
                    var_obj = get_var_using_port_as_state(gromet, port_uid)
                    if var_obj["uid"] in seen_vars:
                        continue
                    seen_vars.add(var_obj["uid"])

                    ver = 0
                    m = re.search(r"\d+$", var_obj["uid"])
                    if m is not None:
                        ver = int(m.group())
                    # if (
                    #     box["uid"] not in box_to_min_var
                    #     or ver < box_to_min_var[box["uid"]]
                    # ):
                    #     box_to_min_var[box["uid"]] = 1 if ver < 1 else ver

                    box_to_vars[box["uid"]].append((var_obj, ver, var_obj["name"]))

    for box_uid, var_vers_and_names in box_to_vars.items():
        box = get_box_by_uid(gromet, box_uid)
        vars_to_vars_with_names = dict()
        for var, ver, name in var_vers_and_names:
            if name not in vars_to_vars_with_names:
                vars_to_vars_with_names[name] = list()
            vars_to_vars_with_names[name].append((var, ver))

        for name, var_list in vars_to_vars_with_names.items():
            var_list.sort(key=lambda var_and_ver: var_and_ver[1])
            starting_ver = 0 if box["syntax"] == "Loop" and len(var_list) > 1 else -1
            for var, _ in var_list:
                var["corrected_ver"] = starting_ver
                starting_ver += 1

    return


def check_gromet_var_grfn_var_match(gromet, grfn_var_id_map):
    matches = 0
    seen_gromet_vars = set()

    add_correct_gromet_var_versions_to_grfn_vers(gromet)

    for box in gromet["boxes"]:
        gromet_scope = (
            box["name"] if box["name"] is not None else box["uid"].split(":")[1]
        )

        if "wires" in box:
            gromet_scope_corrected = correct_gromet_scope(box, gromet_scope)

            for wire in box["wires"] if "wires" in box else []:
                port_uids = get_port_ids_for_wire(gromet, wire)

                for port_uid in port_uids:
                    var_obj = get_var_using_port_as_state(gromet, port_uid)
                    if var_obj == None or var_obj["uid"] in seen_gromet_vars:
                        continue
                    seen_gromet_vars.add(var_obj["uid"])

                    gromet_name = var_obj["name"]
                    gromet_ver_corrected = var_obj["corrected_ver"]

                    for grfn_var_id in grfn_var_id_map.keys():
                        (
                            _,
                            grfn_ns,
                            grfn_scope,
                            grfn_name,
                            grfn_ver,
                        ) = grfn_var_id.split("::")
                        grfn_scope_without_namespace = grfn_scope[len(f"{grfn_ns}.") :]

                        if (
                            gromet_scope_corrected.lower()
                            == grfn_scope_without_namespace.lower()
                            and gromet_name.lower() == grfn_name.lower()
                            and gromet_ver_corrected == int(grfn_ver)
                        ):
                            # print(f"Match! {var_obj['uid']},{grfn_var_id}")
                            if len(grfn_var_id_map[grfn_var_id]["metadata"]) == 0:
                                print("     no metadata")
                            var_obj["metadata"] = grfn_var_id_map[grfn_var_id][
                                "metadata"
                            ]
                            matches += 1
                            break

                    if var_obj["metadata"] == None:
                        print(f"{var_obj['uid']}")

    print(f"Match count: {matches}")


def add_metadata_to_gromet_variables(grfn_vars_with_metadata, gromet_dict):
    new_gromet_dict = copy.deepcopy(gromet_dict)

    grfn_identifiers_to_var_obj = {v["identifier"]: v for v in grfn_vars_with_metadata}

    check_gromet_var_grfn_var_match(new_gromet_dict, grfn_identifiers_to_var_obj)

    return new_gromet_dict


def run(args):
    gromet_dict = read_json_file_as_dict(args.gromet_file)
    grfn_dict = read_json_file_as_dict(args.grfn_with_metadata_file)

    grfn_vars = grfn_dict["variables"]
    updated_gromet_dict = add_metadata_to_gromet_variables(grfn_vars, gromet_dict)

    new_gromet_file = (
        f"{args.gromet_file.split('--GroMEt.json')[0]}-with-metadata--GroMEt.json"
    )
    write_json_dict_to_file(updated_gromet_dict, new_gromet_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gromet_file", help="GroMEt file to add metadata to.")
    parser.add_argument(
        "grfn_with_metadata_file", help="GrFN 3.0 file to take metadata from."
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()
