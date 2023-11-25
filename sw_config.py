import json


def get_room_num(row, column):
    room_num = row * column
    return room_num


def get_symbol_places(room_num):
    symbol_places = {}
    for room_idx in range(1, room_num+1):
        symbol_places["s%d~" % room_idx] = {"token_num": 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["s%d" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["s%d_" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["w%d~" % room_idx] = {"token_num": 1, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["w%d" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["w%d_" % room_idx] = {"token_num": 0, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["|w%d" % room_idx] = {"token_num": 0, "probability": 0.3, "pre_arcs": {}, "post_arcs": {}}
        symbol_places["|w%d_" % room_idx] = {"token_num": 0, "probability": 0.7, "pre_arcs": {}, "post_arcs": {}}
    return symbol_places


def get_position_list(row, column):
    position_list = []
    for row_idx in range(1, row + 1):
        for column_idx in range(1, column + 1):
            position_list.append([row_idx, column_idx])
    return position_list


def get_room_idx(room_position=[int, int], row=0):
    room_idx = (room_position[0]-1) * row + room_position[1]
    return room_idx


def get_adjoining_info(row, column):
    position_list = get_position_list(row, column)
    adjoining_info = {}
    for room_position in position_list:
        adjoining_room = []
        if 1 <= room_position[0]-1 <= row:
            adjoining_room.append(get_room_idx([room_position[0] - 1, room_position[1]], row))
        if 1 <= room_position[1]-1 <= column:
            adjoining_room.append(get_room_idx([room_position[0], room_position[1] - 1], row))
        if 1 <= room_position[1]+1 <= column:
            adjoining_room.append(get_room_idx([room_position[0], room_position[1] + 1], row))
        if 1 <= room_position[0]+1 <= row:
            adjoining_room.append(get_room_idx([room_position[0] + 1, room_position[1]], row))
        adjoining_info.update({str(get_room_idx(room_position, row)): adjoining_room})
    return adjoining_info


def get_sw_subnet(row, column):
    adjoining_info = get_adjoining_info(row, column)
    symbol_places = get_symbol_places(get_room_num(row, column))
    rule_places = {}
    rule_idx = 0
    transitions_dict = {}
    for current_room in adjoining_info.keys():
        transitions_dict["t_s%d" % int(current_room)] = {"dual_transition": "t_s%d_" % int(current_room),
                                                         "pre_arcs": {"s%d~" % int(current_room) : 1},
                                                         "post_arcs": {"s%d" % int(current_room) : 1}}
        symbol_places["s%d~" % int(current_room)]["post_arcs"].update({"t_s%d" % int(current_room): 1})
        symbol_places["s%d" % int(current_room)]["pre_arcs"].update({"t_s%d" % int(current_room): 1})
        transitions_dict["t_s%d_" % int(current_room)] = {"dual_transition": "t_s%d" % int(current_room),
                                                          "pre_arcs": {"s%d~" % int(current_room): 1},
                                                          "post_arcs": {"s%d_" % int(current_room): 1}}
        symbol_places["s%d~" % int(current_room)]["post_arcs"].update({"t_s%d_" % int(current_room): 1})
        symbol_places["s%d_" % int(current_room)]["pre_arcs"].update({"t_s%d_" % int(current_room): 1})
        transitions_dict["t_w%d" % int(current_room)] = {"dual_transition": "t_w%d_" % int(current_room),
                                                         "pre_arcs": {"w%d~" % int(current_room): 1},
                                                         "post_arcs": {"w%d" % int(current_room): 1}}
        symbol_places["w%d~" % int(current_room)]["post_arcs"].update({"t_w%d" % int(current_room): 1})
        symbol_places["w%d" % int(current_room)]["pre_arcs"].update({"t_w%d" % int(current_room): 1})
        transitions_dict["t_w%d_" % int(current_room)] = {"dual_transition": "t_w%d" % int(current_room),
                                                          "pre_arcs": {"w%d~" % int(current_room): 1},
                                                          "post_arcs": {"w%d_" % int(current_room): 1}}
        symbol_places["w%d~" % int(current_room)]["post_arcs"].update({"t_w%d_" % int(current_room): 1})
        symbol_places["w%d_" % int(current_room)]["pre_arcs"].update({"t_w%d_" % int(current_room): 1})
        transitions_dict["t_|w%d" % int(current_room)] = {"pre_arcs": {"w%d~" % int(current_room): 1},
                                                          "post_arcs": {"|w%d" % int(current_room): 1}}
        symbol_places["w%d~" % int(current_room)]["post_arcs"].update({"t_|w%d" % int(current_room): 1})
        symbol_places["|w%d" % int(current_room)]["pre_arcs"].update({"t_|w%d" % int(current_room): 1})
        transitions_dict["t_|w%d_" % int(current_room)] = {"pre_arcs": {"w%d~" % int(current_room): 1},
                                                           "post_arcs": {"|w%d_" % int(current_room): 1}}
        symbol_places["w%d~" % int(current_room)]["post_arcs"].update({"t_|w%d_" % int(current_room): 1})
        symbol_places["|w%d_" % int(current_room)]["pre_arcs"].update({"t_|w%d_" % int(current_room): 1})
    for current_room, adjoining_rooms in adjoining_info.items():
        rule_idx += 1
        rule_places.update({"r%d" % rule_idx:  {"token_num":len(adjoining_rooms), "pre_arcs": {}, "post_arcs": {}}})
        transitions_dict["t_s%d" % int(current_room)]["pre_arcs"]["r%d" % rule_idx] = 1
        rule_places["r%d" % rule_idx]["post_arcs"].update({"t_s%d" % int(current_room): 1})
        for adjoining_room in adjoining_rooms:
            transitions_dict["t_w%d_" % int(adjoining_room)]["pre_arcs"]["r%d" % rule_idx] = 1
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_w%d_" % int(adjoining_room): 1})
            transitions_dict["t_|w%d_" % int(adjoining_room)]["pre_arcs"]["r%d" % rule_idx] = 1
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_|w%d_" % int(adjoining_room): 1})
        for adjoining_room in adjoining_rooms:
            rule_idx += 1
            rule_places["r%d" % rule_idx] = {"token_num":1, "pre_arcs": {}, "post_arcs": {}}
            transitions_dict["t_s%d_" % int(current_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_s%d_" % int(current_room): 1})
            transitions_dict["t_w%d" % int(adjoining_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_w%d" % int(adjoining_room): 1})
            transitions_dict["t_|w%d" % int(adjoining_room)]["pre_arcs"].update({"r%d" % rule_idx: 1})
            rule_places["r%d" % rule_idx]["post_arcs"].update({"t_|w%d" % int(adjoining_room): 1})
    places_dict = dict(symbol_places, **rule_places)
    return places_dict, transitions_dict


def get_json(row, column, json_name):
    places_dict, transitions_dict = get_sw_subnet(row, column)
    sw_subnet_dict = {"places": places_dict, "transitions": transitions_dict}
    with open("../Wumpus_world/%s" % json_name, "w") as f:
        json.dump(sw_subnet_dict, f)
    return


if __name__ == "__main__":
    get_json(3,3,"33_sw_1")
    print("over")