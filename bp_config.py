from sw_config import get_room_num
from sw_config import get_position_list
from sw_config import get_adjoining_info


def get_symbol_places(room_num):
    symbol_places = {}
    for room_idx in range(1, room_num+1):
        symbol_places["b%d~" % room_idx] = {"token_num": 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["b%d" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["b%d_" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["p%d~" % room_idx] = {"token_num": 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["p%d" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["p%d_" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["|p%d" % room_idx] = {"token_num": 0, "probability": 0.2, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["|p%d_" % room_idx] = {"token_num": 0, "probability": 0.8, "pre_arcs": {}, "post_arcs": {}}
    return symbol_places

def get_bp_subnet(row, column):
    symbol_places = get_symbol_places(get_room_num(row, column))
    adjoining_info = get_adjoining_info(row, column)
    rule_places = {}
    rule_num = 0
    rule_num += len(adjoining_info)
    for adjoining_room in adjoining_info.values():
        rule_num += len(adjoining_room)
    rule_idx = rule_num
    transitions_dict = {}
    for current_room in adjoining_info.keys():
        transitions_dict["t_b%d" % int(current_room)] = {"dual_transition": "t_b%d_" % int(current_room),
                                                         "pre_arcs": {"b%d~" % int(current_room): 1},
                                                         "post_arcs": {"b%d" % int(current_room): 1}}
        symbol_places["b%d~" % int(current_room)]["post_arcs"].update({"t_b%d" % int(current_room): 1})
        symbol_places["b%d" % int(current_room)]["pre_arcs"].update({"t_b%d" % int(current_room): 1})
        transitions_dict["t_b%d_" % int(current_room)] = {"dual_transition": "t_b%d" % int(current_room),
                                                          "pre_arcs": {"b%d~" % int(current_room): 1},
                                                          "post_arcs": {"b%d_" % int(current_room): 1}}
        symbol_places["b%d~" % int(current_room)]["post_arcs"].update({"t_b%d_" % int(current_room): 1})
        symbol_places["b%d_" % int(current_room)]["pre_arcs"].update({"t_b%d_" % int(current_room): 1})
        transitions_dict["t_p%d" % int(current_room)] = {"dual_transition": "t_p%d_" % int(current_room),
                                                         "pre_arcs": {"p%d~" % int(current_room): 1},
                                                         "post_arcs": {"p%d" % int(current_room): 1}}
        symbol_places["p%d~" % int(current_room)]["post_arcs"].update({"t_p%d" % int(current_room): 1})
        symbol_places["p%d" % int(current_room)]["pre_arcs"].update({"t_p%d" % int(current_room): 1})
        transitions_dict["t_p%d_" % int(current_room)] = {"dual_transition": "t_p%d" % int(current_room),
                                                          "pre_arcs": {"p%d~" % int(current_room): 1},
                                                          "post_arcs": {"p%d_" % int(current_room): 1}}
        symbol_places["p%d~" % int(current_room)]["post_arcs"].update({"t_p%d_" % int(current_room): 1})
        symbol_places["p%d_" % int(current_room)]["pre_arcs"].update({"t_p%d_" % int(current_room): 1})
        transitions_dict["t_|p%d" % int(current_room)] = {"pre_arcs": {"p%d~" % int(current_room): 1},
                                                          "post_arcs": {"|p%d" % int(current_room): 1}}
        symbol_places["p%d~" % int(current_room)]["post_arcs"].update({"t_|p%d" % int(current_room): 1})
        symbol_places["|p%d" % int(current_room)]["pre_arcs"].update({"t_|p%d" % int(current_room): 1})
        transitions_dict["t_|p%d_" % int(current_room)] = {"pre_arcs": {"p%d~" % int(current_room): 1},
                                                           "post_arcs": {"|p%d_" % int(current_room): 1}}
        symbol_places["p%d~" % int(current_room)]["post_arcs"].update({"t_|p%d_" % int(current_room): 1})
        symbol_places["|p%d_" % int(current_room)]["pre_arcs"].update({"t_|p%d_" % int(current_room): 1})
    for current_room, adjoining_rooms in adjoining_info.items():
        rule_idx += 1
        rule_places.update({"r%d" % rule_idx: {"token_num" : len(adjoining_rooms), "pre_arcs": {}, "post_arcs": {}}})
        transitions_dict["t_b%d" % int(current_room)]["pre_arcs"]["r%d" % rule_idx] = 1
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_b%d" % int(current_room): 1})
        for adjoining_room in adjoining_rooms:
            transitions_dict["t_p%d_" % int(adjoining_room)]["pre_arcs"]["r%d" % rule_idx] = 1
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_p%d_" % int(adjoining_room): 1})
            transitions_dict["t_|p%d_" % int(adjoining_room)]["pre_arcs"]["r%d" % rule_idx] = 1
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_|p%d_" % int(adjoining_room): 1})
        for adjoining_room in adjoining_rooms:
            rule_idx += 1
            rule_places["r%d" % rule_idx] = {"token_num" :1, "pre_arcs": {}, "post_arcs": {}}
            transitions_dict["t_b%d_" % int(current_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_b%d_" % int(current_room): 1})
            transitions_dict["t_p%d" % int(adjoining_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_p%d" % int(adjoining_room): 1})
            transitions_dict["t_|p%d" % int(adjoining_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_|p%d" % int(adjoining_room): 1})
    places_dict = dict(symbol_places, **rule_places)
    return places_dict, transitions_dict



