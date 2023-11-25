from sw_config import *

def get_state_places(room_num):
    state_places = {}
    for room_idx in range(1, room_num+1):
        state_places["F%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        state_places["R%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        state_places["B%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
        state_places["L%d" % room_idx] = {"token_num" : 0, "pre_arcs": {}, "post_arcs": {}}
    return state_places

def get_in_room_transitions(room_num):
    state_places = get_state_places(room_num)
    in_room_transitions = {}
    for room_idx in range(1, room_num+1):
        in_room_transitions["t_F%dR%d" % (room_idx, room_idx)] = {"pre_arcs": {"F%d" % room_idx: 1},
                                                               "post_arcs": {"R%d" %  room_idx: 1}}
        state_places["F%d" % room_idx]["post_arcs"].update({"t_F%dR%d" % (room_idx, room_idx): 1})
        state_places["R%d" %  room_idx]["pre_arcs"].update({"t_F%dR%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_R%dF%d" % (room_idx, room_idx)] = {"pre_arcs": {"R%d" % room_idx: 1},
                                                                "post_arcs": {"F%d" % room_idx: 1}}
        state_places["R%d" % room_idx]["post_arcs"].update({"t_R%dF%d" % (room_idx, room_idx): 1})
        state_places["F%d" % room_idx]["pre_arcs"].update({"t_R%dF%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_R%dB%d" % (room_idx, room_idx)] = {"pre_arcs": {"R%d" % room_idx: 1},
                                                                "post_arcs": {"B%d" % room_idx: 1}}
        state_places["R%d" % room_idx]["post_arcs"].update({"t_R%dB%d" % (room_idx, room_idx): 1})
        state_places["B%d" % room_idx]["pre_arcs"].update({"t_R%dB%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_B%dR%d" % (room_idx, room_idx)] = {"pre_arcs": {"B%d" % room_idx: 1},
                                                                "post_arcs": {"R%d" % room_idx: 1}}
        state_places["B%d" % room_idx]["post_arcs"].update({"t_B%dR%d" % (room_idx, room_idx): 1})
        state_places["R%d" % room_idx]["pre_arcs"].update({"t_B%dR%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_F%dL%d" % (room_idx, room_idx)] = {"pre_arcs": {"F%d" % room_idx: 1},
                                                                "post_arcs": {"L%d" % room_idx: 1}}
        state_places["F%d" % room_idx]["post_arcs"].update({"t_F%dL%d" % (room_idx, room_idx): 1})
        state_places["L%d" % room_idx]["pre_arcs"].update({"t_F%dL%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_L%dF%d" % (room_idx, room_idx)] = {"pre_arcs": {"L%d" % room_idx: 1},
                                                                "post_arcs": {"F%d" % room_idx: 1}}
        state_places["L%d" % room_idx]["post_arcs"].update({"t_L%dF%d" % (room_idx, room_idx): 1})
        state_places["F%d" % room_idx]["pre_arcs"].update({"t_L%dF%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_L%dB%d" % (room_idx, room_idx)] = {"pre_arcs": {"L%d" % room_idx: 1},
                                                                "post_arcs": {"B%d" % room_idx: 1}}
        state_places["L%d" % room_idx]["post_arcs"].update({"t_L%dB%d" % (room_idx, room_idx): 1})
        state_places["B%d" % room_idx]["pre_arcs"].update({"t_L%dB%d" % (room_idx, room_idx): 1})
        in_room_transitions["t_B%dL%d" % (room_idx, room_idx)] = {"pre_arcs": {"B%d" % room_idx: 1},
                                                                "post_arcs": {"L%d" % room_idx: 1}}
        state_places["B%d" % room_idx]["post_arcs"].update({"t_B%dL%d" % (room_idx, room_idx): 1})
        state_places["L%d" % room_idx]["pre_arcs"].update({"t_B%dL%d" % (room_idx, room_idx): 1})
    return state_places, in_room_transitions


def get_state_subnet(row, column, json_name):
    room_num = get_room_num(row, column)
    state_places, in_room_transitions = get_in_room_transitions(room_num)
    out_room_transitions = {}
    adjoining_info = get_adjoining_info(row, column)
    for current_room,adjoining_rooms in adjoining_info.items():
        current_room_idx = int(current_room)
        for adjoining_room_idx in adjoining_rooms:
            if adjoining_room_idx == current_room_idx - 1:
                out_room_transitions["t_L%dL%d" % (current_room_idx, adjoining_room_idx)] = \
                    {"pre_arcs": {"L%d" % current_room_idx: 1},"post_arcs": {"L%d" % adjoining_room_idx: 1}}
                state_places["L%d" % current_room_idx]["post_arcs"].update({"t_L%dL%d" % (current_room_idx, adjoining_room_idx): 1})
                state_places["L%d" % adjoining_room_idx]["pre_arcs"].update({"t_L%dL%d" % (current_room_idx, adjoining_room_idx): 1})
            if adjoining_room_idx == current_room_idx + 1:
                out_room_transitions["t_R%dR%d" % (current_room_idx, adjoining_room_idx)] = \
                    {"pre_arcs": {"R%d" % current_room_idx: 1},"post_arcs": {"R%d" % adjoining_room_idx: 1}}
                state_places["R%d" % current_room_idx]["post_arcs"].update(
                    {"t_R%dR%d" % (current_room_idx, adjoining_room_idx): 1})
                state_places["R%d" % adjoining_room_idx]["pre_arcs"].update(
                    {"t_R%dR%d" % (current_room_idx, adjoining_room_idx): 1})
            if adjoining_room_idx == current_room_idx - column:
                out_room_transitions["t_B%dB%d" % (current_room_idx, adjoining_room_idx)] = \
                    {"pre_arcs": {"B%d" % current_room_idx: 1},"post_arcs": {"B%d" % adjoining_room_idx: 1}}
                state_places["B%d" % current_room_idx]["post_arcs"].update(
                    {"t_B%dB%d" % (current_room_idx, adjoining_room_idx): 1})
                state_places["B%d" % adjoining_room_idx]["pre_arcs"].update(
                    {"t_B%dB%d" % (current_room_idx, adjoining_room_idx): 1})
            if adjoining_room_idx == current_room_idx + column:
                out_room_transitions["t_F%dF%d" % (current_room_idx, adjoining_room_idx)] = \
                    {"pre_arcs": {"F%d" % current_room_idx: 1},"post_arcs": {"F%d" % adjoining_room_idx: 1}}
                state_places["F%d" % current_room_idx]["post_arcs"].update(
                    {"t_F%dF%d" % (current_room_idx, adjoining_room_idx): 1})
                state_places["F%d" % adjoining_room_idx]["pre_arcs"].update(
                    {"t_F%dF%d" % (current_room_idx, adjoining_room_idx): 1})
    transitions_dict = dict(in_room_transitions, **out_room_transitions)
    state_subnet_dict = {"places": state_places, "transitions": transitions_dict}
    with open("../Wumpus_world/%s" % json_name, "w") as f:
        json.dump(state_subnet_dict, f)
    return





