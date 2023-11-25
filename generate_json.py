from sw_config import *
from bp_config import *
from gg_config import *


def generate_petrinet_json(row, column, json_name):
    sw_place_dict, sw_transition_dict = get_sw_subnet(row, column)
    bp_place_dict, bp_transition_dict = get_bp_subnet(row, column)
    gg_place_dict, gg_transition_dict = get_gg_subnet(row, column)
    all_place_dict = dict(sw_place_dict, **bp_place_dict, **gg_place_dict)
    all_transition_dict = dict(sw_transition_dict,  **bp_transition_dict, **gg_transition_dict)
    # all_place_dict = dict(sw_place_dict,  **gg_place_dict)
    # all_transition_dict = dict(sw_transition_dict, **gg_transition_dict)
    pn_dict = {"places": all_place_dict, "transitions": all_transition_dict}
    with open(json_name, "w") as f:
        json.dump(pn_dict, f)


if __name__ == '__main__':
    generate_petrinet_json(3, 3, 'R33.json')