import argparse
import json
import copy
import re


def read_json_file_as_dict(filepath):
    with open(filepath) as f:
        return json.load(f)


def write_json_dict_to_file(d, filepath):
    with open(filepath, "w") as f:
        return json.dump(d, f)


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


def check_gromet_var_grfn_var_match(gromet, grfn_var_id_map):
    matches = 0
    seen_gromet_vars = set()

    for box in gromet["boxes"]:
        gromet_scope = box["name"]

        for wire in box["wires"] if "wires" in box else []:
            port_uids = get_port_ids_for_wire(gromet, wire)

            for port_uid in port_uids:
                var_obj = get_var_using_port_as_state(gromet, port_uid)
                if var_obj == None or var_obj["uid"] in seen_gromet_vars:
                    continue
                seen_gromet_vars.add(var_obj["uid"])

                gromet_name = var_obj["name"]
                gromet_ver = -1
                m = re.search(r"\d+$", var_obj["uid"])
                if m is not None:
                    gromet_ver = int(m.group()) - 1

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
                        grfn_scope_without_namespace == gromet_scope
                        and gromet_name == grfn_name
                        and gromet_ver == int(grfn_ver)
                    ):
                        print(f"Match! {var_obj['uid']},{grfn_var_id}")
                        if len(grfn_var_id_map[grfn_var_id]["metadata"]) == 0:
                            print("     no metadata")
                        var_obj["metadata"] = grfn_var_id_map[grfn_var_id]["metadata"]
                        matches += 1
                        break
                    else:
                        var_obj["metadata"] = []
                        # if gromet_name == grfn_name:
                        #     print(
                        #         f"GrFN: {grfn_scope_without_namespace} {grfn_name} {grfn_ver}"
                        #     )
                        #     print(f"GroMEt: {gromet_scope} {gromet_name} {gromet_ver}")
                        #     print()
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
