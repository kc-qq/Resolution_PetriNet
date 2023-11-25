row = int(input("Please enter the number of rows on the map:"))
column = int(input("Please enter the number of columns on the map:"))


def get_room_num():
    room_num = row * column
    return room_num


def get_position_list():
    position_list = []
    for row_idx in range(1, row + 1):
        for column_idx in range(1, column + 1):
            position_list.append([row_idx, column_idx])
    return position_list


def get_room_idx(room_position=None):
    if room_position is None:
        room_position = [int, int]
    room_idx = (room_position[0]-1) * row + room_position[1]
    return room_idx


def get_adjoining_info():
    position_list = get_position_list()
    adjoining_info = {}
    for room_position in position_list:
        adjoining_room = []
        if 1 <= room_position[0]-1 <= row:
            adjoining_room.append(get_room_idx([room_position[0] - 1, room_position[1]]))
        if 1 <= room_position[1]-1 <= column:
            adjoining_room.append(get_room_idx([room_position[0], room_position[1] - 1]))
        if 1 <= room_position[1]+1 <= column:
            adjoining_room.append(get_room_idx([room_position[0], room_position[1] + 1]))
        if 1 <= room_position[0]+1 <= row:
            adjoining_room.append(get_room_idx([room_position[0] + 1, room_position[1]]))
        adjoining_info.update({str(get_room_idx(room_position)): adjoining_room})
    return adjoining_info

def get_semantic_constraint():
    adjoining_info = get_adjoining_info()
    semantic_constraint = {}
    sw_rule_idx = 1
    rule_num = len(adjoining_info)
    for adjoining_room in adjoining_info.values():
        rule_num += len(adjoining_room)
    bp_rule_idx = rule_num + 1
    gg_rule_idx = 2 * rule_num + 1
    for room_idx,adjoining_rooms in adjoining_info.items():
        semantic_constraint.update({"r%d" % sw_rule_idx: ["s%d" % int(room_idx)]})
        semantic_constraint.update({"r%d" % bp_rule_idx: ["b%d" % int(room_idx)]})
        semantic_constraint.update({"r%d" % gg_rule_idx: ["!g%d" % int(room_idx), "g%d_" % int(room_idx)]})
        gg_rule_idx += 1
        semantic_constraint.update({"r%d" % gg_rule_idx: ["!g%d_" % int(room_idx), "g%d" % int(room_idx)]})
        gg_rule_idx += 1
        for adjoining_room in adjoining_rooms:
            semantic_constraint["r%d" % sw_rule_idx].append("w%d_" % adjoining_room)
            semantic_constraint["r%d" % bp_rule_idx].append("p%d_" % adjoining_room)
        sw_rule_idx += 1
        bp_rule_idx += 1
        for adjoining_room in adjoining_rooms:
            semantic_constraint.update({"r%d" % sw_rule_idx: ["s%d_" % int(room_idx), "w%d" % adjoining_room]})
            semantic_constraint.update({"r%d" % bp_rule_idx: ["b%d_" % int(room_idx), "p%d" % adjoining_room]})
            sw_rule_idx += 1
            bp_rule_idx += 1
    return semantic_constraint

# 列表储存0型符号，字典储存1型和2型
def get_symbol_info():
    room_num = get_room_num()
    symbol0 = []
    symbol1 = {}
    symbol2 = {}
    for room_idx in range(1,room_num+1):
        symbol0.extend(["s%d" % room_idx,"w%d" % room_idx, "b%d" % room_idx,"p%d" % room_idx, "!g%d" % room_idx, "g%d" % room_idx])
        # symbol1.update({"p%d" % room_idx: 0.2})
        # if (room_idx - column) > 0:
        #     symbol2.update({"w%d" % room_idx: {"c": ["w%d" % (room_idx - column)],"p":[0.6,0.1]}})
        # else:
        #     symbol1.update({"w%d" % room_idx: 0.4})
    symbol_info = {"symbol0": symbol0, "symbol1": symbol1, "symbol2": symbol2}
    return symbol_info

def get_generalized_literals(symbol_info):
    generalized_literals = {}
    generalized_literal2symbol = {}
    symbol0 = symbol_info["symbol0"]
    symbol1 = symbol_info["symbol1"]
    symbol2 = symbol_info["symbol2"]
    for symbol in symbol0:
        generalized_literals.update({symbol:[symbol], symbol + "_": [symbol + "_"]})
        generalized_literal2symbol.update({symbol: symbol, symbol + "_": symbol})
    for symbol in symbol1.keys():
        generalized_literals.update({symbol:[symbol, "|" + symbol], symbol + "_":[symbol + "_", "|" + symbol + "_"]})
        generalized_literal2symbol.update({symbol: symbol, "|" + symbol:symbol, symbol + "_": symbol, "|" + symbol + "_":symbol})
    for symbol,symbol_cp in symbol2.items():
        positive_literals = [symbol]
        negative_literals = [symbol + "_"]
        generalized_literal2symbol.update({symbol: symbol, symbol + "_": symbol})
        c_symbol_num = len(symbol_cp["c"])
        for idx in range(2**c_symbol_num):
            positive_literals.append(symbol + "|" + str(idx))
            negative_literals.append(symbol + "|" + str(idx) + "_")
            generalized_literal2symbol.update({symbol + "|" + str(idx): symbol, symbol + "|" + str(idx) + "_": symbol})
        generalized_literals.update({symbol: positive_literals, symbol + "_": negative_literals})
    return generalized_literals, generalized_literal2symbol

def get_dual_generalized_literal(generalized_literal):
    if generalized_literal[-1] == "_":
        dual_generalized_literal = generalized_literal[:-1]
    else:
        dual_generalized_literal = generalized_literal + "_"
    return dual_generalized_literal


if __name__ == "__main__":
    sc = get_semantic_constraint()
    symbols = get_symbol_info()
    gls = get_generalized_literals(symbols)
    print(gls)
    print("over!")