import sys
import os
import subprocess
import json
import argparse

from automates.program_analysis.GCC2GrFN.gcc_ast_to_cast import GCC2CAST
from automates.program_analysis.CAST2GrFN.cast import CAST
from automates.program_analysis.CAST2GrFN.model.cast.module import Module


def main():

    cast_name = None
    if len(sys.argv) > 1:
        cast_name = sys.argv[1]
    else:
        raise Exception(f"Error: Please provide CAST file path as an argument")

    cast = CAST.from_json_file(cast_name)
    program_name = cast_name.split("--CAST.json")[0]

    air = cast.to_air_dict()
    sources = [
        source_ref.source_file_name
        for m in cast.nodes
        if isinstance(m, Module)
        for source_ref in m.source_refs
    ]
    with open(f"{program_name}--AIR.json", "w") as f:
        json.dump(
            {
                "entrypoint": air["entrypoint"],
                "containers": air["containers"],
                "variables": air["variables"],
                "types": [],
                "sources": sources,
                "source_comments": {},
            },
            f,
        )


if __name__ == "__main__":
    main()
