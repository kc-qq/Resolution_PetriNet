from PetriNet import *
import copy


if __name__ == "__main__":
    PNs = PetriNet("R33.json")
    PNs_1 = copy.deepcopy(PNs)
    PNs_1.transition_fired("t_w1_")
    PNs_1.transition_fired("t_s1_")
    PNs_1.transition_fired("t_w2_")
    PNs_1.transition_fired("t_w4_")
    PNs_1.transition_fired("t_s2")
    PNs_1.transition_fired("t_s4")
    PNs_1.pruning_for_probability("w7")
    a= PNs_1.get_reachable_graph()
    PNs_1.transition_fired("t_|w7")
    b= PNs_1.get_reachable_graph() / a

