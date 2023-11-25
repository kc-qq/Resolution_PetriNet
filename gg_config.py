from sw_config import get_room_num
from sw_config import get_adjoining_info


def get_symbol_places(room_num):
    symbol_places = {}
    for room_idx in range(1, room_num + 1):
        symbol_places["!g%d~" % room_idx] = {"token_num" : 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["!g%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["!g%d_" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["g%d~" % room_idx] = {"token_num" : 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["g%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["g%d_" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
    return symbol_places


def get_rule_places(room_num, rule_init_idx):
    rule_idx = rule_init_idx
    rule_places = {}
    for room_idx in range(1, room_num*2 + 1):
        rule_idx += 1
        rule_places.update({"r%d" % rule_idx: {"token_num" :1, "pre_arcs": {}, "post_arcs": {}}})
    return rule_places


def get_gg_subnet(row, column):
    transitions_dict = {}
    adjoining_info = get_adjoining_info(row, column)
    room_num = get_room_num(row, column)
    symbol_places = get_symbol_places(room_num)
    rule_num = 0
    rule_num += len(adjoining_info)
    for adjoining_room in adjoining_info.values():
        rule_num += len(adjoining_room)
    rule_init_idx = 2 * rule_num
    rule_idx = rule_init_idx
    rule_places = get_rule_places(room_num, rule_init_idx)
    for room_idx in range(1, room_num + 1):
        rule_idx += 1
        transitions_dict.update({"t_!g%d" % room_idx: {"dual_transition": "t_!g%d_" % room_idx,
                                "pre_arcs": {"!g%d~" % room_idx: 1, "r%d" % rule_idx: 1},
                                 "post_arcs": {"!g%d" % room_idx: 1}}})
        symbol_places["!g%d~" % room_idx]["post_arcs"].update({"t_!g%d" % room_idx: 1})
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_!g%d" % room_idx: 1})
        symbol_places["!g%d" % room_idx]["pre_arcs"].update({"t_!g%d" % room_idx: 1})
        transitions_dict.update({"t_g%d_" % room_idx: {"dual_transition": "t_g%d" % room_idx,
                                 "pre_arcs": {"g%d~" % room_idx: 1, "r%d" % rule_idx: 1},
                                 "post_arcs": {"g%d_" % room_idx: 1}}})
        symbol_places["g%d~" % room_idx]["post_arcs"].update({"t_g%d_" % room_idx: 1})
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_g%d_" % room_idx: 1})
        symbol_places["g%d_" % room_idx]["pre_arcs"].update({"t_g%d_" % room_idx: 1})
        rule_idx += 1
        transitions_dict.update({"t_!g%d_" % room_idx: {"dual_transition": "t_!g%d" % room_idx,
                                "pre_arcs": {"!g%d~" % room_idx: 1, "r%d" % rule_idx: 1},
                                 "post_arcs": {"!g%d_" % room_idx: 1}}})
        symbol_places["!g%d~" % room_idx]["post_arcs"].update({"t_!g%d_" % room_idx: 1})
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_!g%d_" % room_idx: 1})
        symbol_places["!g%d_" % room_idx]["pre_arcs"].update({"t_!g%d_" % room_idx: 1})
        transitions_dict.update({"t_g%d" % room_idx: {"dual_transition": "t_g%d_" % room_idx,
                                "pre_arcs": {"g%d~" % room_idx: 1, "r%d" % rule_idx: 1},
                                 "post_arcs": {"g%d" % room_idx: 1}}})
        symbol_places["g%d~" % room_idx]["post_arcs"].update({"t_g%d" % room_idx: 1})
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_g%d" % room_idx: 1})
        symbol_places["g%d" % room_idx]["pre_arcs"].update({"t_g%d" % room_idx: 1})
    places_dict = dict(symbol_places, **rule_places)
    return places_dict, transitions_dict


