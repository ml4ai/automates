from gromet import gromet_to_json
import example_call_ex1
import example_cond_ex1
import example_emmaaSBML_PetriNetClassic
import example_SimpleSIR_Bilayer
import example_SimpleSIR_FN
import example_SimpleSIR_PetriNetClassic
import example_SimpleSIR_PrTNet
import example_toy1


ROOT_DATA = 'examples'


gromet_to_json(example_call_ex1.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_cond_ex1.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_emmaaSBML_PetriNetClassic.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_SimpleSIR_Bilayer.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_SimpleSIR_FN.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_SimpleSIR_PetriNetClassic.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_SimpleSIR_PrTNet.generate_gromet(), tgt_root=ROOT_DATA)
gromet_to_json(example_toy1.generate_gromet(), tgt_root=ROOT_DATA)
