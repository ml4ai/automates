import sys
import json


def main():
    grfn1 = json.load(open(sys.argv[1], "r"))
    grfn2 = json.load(open(sys.argv[2], "r"))
    outfile_name = sys.argv[3]

    defs1 = gather_vars_with_text_defs(grfn1["variables"])
    defs2 = gather_vars_with_text_defs(grfn2["variables"])
    print(defs1)
    print(defs2)

    out_data = [
        {
            "grfn_uid": grfn1["uid"],
            "variable_defs": defs1
        },
        {
            "grfn_uid": grfn2["uid"],
            "variable_defs": defs2
        }
    ]

    json.dump(out_data, open(outfile_name, "w"))


def gather_vars_with_text_defs(variables):
    def get_var_and_def(var_data):
        txt_id = var_data["metadata"][0]["attributes"][0]["text_identifier"]
        txt_def = var_data["metadata"][0]["attributes"][0]["text_definition"]
        code_id = var_data["identifier"].split("::")[2]
        return {
            "var_uid": var_data["uid"],
            "code_identifier": code_id,
            "text_definition": txt_def,
            "text_identifier": txt_id
        }

    return [get_var_and_def(v) for v in variables if "metadata" in v]


if __name__ == '__main__':
    main()
