import sys

from automates.model_assembly.networks import (
    GroundedFunctionNetwork,
)
from automates.model_assembly.model_dynamics import extract_model_dynamics

program_name = sys.argv[1]
grfn = GroundedFunctionNetwork.from_json(f"./{program_name}--GrFN.json")
dynamics = extract_model_dynamics(grfn)

print(f"Found {len(dynamics)} potential model dynamics")
for i in range(len(dynamics)):
    json_file = f"./{program_name}-model-dynamics-{i}--GrFN.json"
    print(f"Writing grfn dynamics to {json_file}")
    dynamics[i].to_json_file(json_file)

    pdf_file = f"./{program_name}-model-dynamics-{i}--GrFN.pdf"
    print(f"Writing grfn dynamics AGraph to {pdf_file}")
    A = dynamics[i].to_AGraph()
    A.draw(pdf_file, prog="dot")