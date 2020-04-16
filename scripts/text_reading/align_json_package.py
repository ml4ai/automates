import json


def main():
    # ==========================================================================
    # Load data from the various resources for alignment
    # NOTE: @masha I will be doing this portion on the Python side
    # ==========================================================================
    grfn_json = json.load(open("PETPNO_GrFN.json", "r"))
    comment_data = grfn_json["source_comments"]
    variables = grfn_json["variables"]
    mention_data = json.load(open("PNO-mentions.json", "r"))
    equations = list()
    with open("PETPNO_equations.txt", "r") as infile:
        for line in infile:
            equations.append(line.strip())

    # create the output dict will all keys needed by the align pipeline
    output_dict = {
        "mentions": mention_data,
        "equations": equations,
        "source_code": {"variables": variables, "comments": comment_data},
    }

    output_filepath = "PNO-alignment-data.json"
    json.dump(output_dict, open(output_filepath, "w"))
    # NOTE: @masha I would then call /align with the arg `output_filepath`
    # ==========================================================================

    # Testing the ability of our output data to be reloaded with JSON
    loaded_data = json.load(open(output_filepath, "r"))
    assert isinstance(loaded_data, dict)

    assert "mentions" in loaded_data
    assert "equations" in loaded_data
    assert "source_code" in loaded_data

    assert isinstance(loaded_data["mentions"], dict)
    assert isinstance(loaded_data["equations"], list)
    assert isinstance(loaded_data["source_code"], dict)

    assert "documents" in loaded_data["mentions"]
    assert "mentions" in loaded_data["mentions"]
    assert "comments" in loaded_data["source_code"]
    assert "variables" in loaded_data["source_code"]

    assert isinstance(loaded_data["mentions"]["mentions"], list)
    assert isinstance(loaded_data["source_code"]["variables"], list)
    assert isinstance(loaded_data["source_code"]["comments"], dict)

    # Printing some sample values to evaluate the reloaded JSON
    print("INFO: printing a sample mention object")
    print(loaded_data["mentions"]["mentions"][0], "\n")

    print("INFO: printing a sample equation object")
    print(loaded_data["equations"][0], "\n")

    print("INFO: printing sample source code variable object")
    print(loaded_data["source_code"]["variables"][0], "\n")

    print("INFO: printing sample keys for source code comment object")
    print(list(loaded_data["source_code"]["comments"].keys()))


if __name__ == "__main__":
    main()
