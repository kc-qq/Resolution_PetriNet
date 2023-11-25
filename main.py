from PetriNet import *
from KPNs import *
import time
import matplotlib.pyplot as plt
from generate_json import *
import matplotlib.colors as colors
import matplotlib.cm as cmx
import re
from action_moding import *
import random
import copy



# row = int(input("Please enter the number of rows on the map:"))
# column = int(input("Please enter the number of columns on the map:"))
time_interval = 0.02
# row = 3
# column = 3
# map_info = {"wumpus":7, "pit":3, "gold":9}
position_list = get_position_list(row, column)
adjoining_info = get_adjoining_info(row, column)
wumpus_list = []
pit_list = []
gold_list = []
agent_list = []



def draw_map():
    for i in range(column + 1):
        y = np.arange(0, row + 1, 1)
        x = [i] * (row + 1)
        plt.plot(x, y, color='black')
    for j in range(row + 1):
        x = np.arange(0, column + 1, 1)
        y = [j] * (column + 1)
        plt.plot(x, y, color='black')


def onclick(event, map_info):
    # map_info = {"wumpus":[],"pit":[],"gold":None,"agent":None}
    x = event.xdata
    y = event.ydata
    # wumpus_idx
    if event.button == 1:
        plt.scatter(x, y, color='r', s=100)
        wumpus_room_idx = int(x) + int(y) * column + 1
        wumpus_list.append(wumpus_room_idx)
        map_info.update({"wumpus": wumpus_list})
    # pit_idx
    if event.button == 3:
        plt.scatter(x, y, color='b', s=100)
        pit_room_idx = int(x) + int(y) * column + 1
        pit_list.append(pit_room_idx)
        map_info.update({"pit": pit_list})
    # gold_idx
    if event.button == 8:
        plt.scatter(x, y, color='g', s=100)
        gold_idx = int(x) + int(y) * column + 1
        gold_list.append(gold_idx)
        map_info.update({"gold": gold_list})
    # Agent_init_idx
    if event.button == 9:
        plt.scatter(x, y, marker='>', color='black', s=100)
        agent_init_room_idx = int(x) + int(y) * column + 1
        agent_list.append(agent_init_room_idx)
        map_info.update({"agent": agent_list})


def get_map_info():
    map_info = {}
    fig = plt.figure()
    draw_map()
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, map_info))
    plt.show()
    return map_info


def tell_agent_perception(map_info, current_room):
    get_perception = []
    adjoin_wumpus = False
    adjoin_pit = False
    is_gold = False
    for wumpus_room_idx in map_info["wumpus"]:
        if current_room in adjoining_info[str(wumpus_room_idx)]:
            adjoin_wumpus = True
            break
    if adjoin_wumpus:
            get_perception.append('s%d' % current_room)
    else:
        get_perception.append('s%d_' % current_room)
    for pit_room_idx in map_info["pit"]:
        if current_room in adjoining_info[str(pit_room_idx)]:
            adjoin_pit = True
            break
    if adjoin_pit:
        get_perception.append('b%d' % current_room)
    else:
        get_perception.append('b%d_' % current_room)
    for gold_room_idx in map_info["gold"]:
        if current_room == gold_room_idx:
            is_gold = True
    if is_gold:
        get_perception.append('!g%d' % current_room)
    else:
        get_perception.append('!g%d_' % current_room)
    return get_perception


def get_location(room_idx):
    if room_idx % column:
        room_x = room_idx % column - 0.5
        room_y = int(room_idx / column) + 0.5
    else:
        room_x = column - 0.5
        room_y = room_idx / column - 0.5
    return room_x, room_y


def draw_background(room_list,color):
    for room_idx in room_list:
        x, y = get_location(room_idx)
        area_x = np.array([x - 0.5, x + 0.5])
        area_y1 = np.array([y - 0.5, y - 0.5])
        area_y2 = np.array([y + 0.5, y + 0.5])
        plt.fill_between(area_x,area_y1,area_y2, where=(area_y2 > area_y1), facecolor=color, interpolate=True)


def draw_map_information(map_info,safe_room,close_room,dangerous_room,doubtful_room):
    draw_map()
    for wumpus_room_idx in map_info["wumpus"]:
        wumpus_x, wumpus_y = get_location(wumpus_room_idx)
        plt.text(wumpus_x - 0.4, wumpus_y, r'wumpus', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    for pit_room_idx in map_info["pit"]:
        pit_x, pit_y = get_location(pit_room_idx)
        plt.text(pit_x - 0.2, pit_y, r'pit', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    for gold_room_idx in map_info["gold"]:
        gold_x, gold_y = get_location(gold_room_idx)
        plt.text(gold_x - 0.3, gold_y, r'gold', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    # agent_x, agent_y = get_location(map_info["agent"])
    # wumpus = plt.scatter(wumpus_x, wumpus_y, color='r', s=100)
    # pit = plt.scatter(pit_x, pit_y, color='b', s=100)
    # gold = plt.scatter(gold_x, gold_y, color='g', s=100)
    # plt.text(row/2,column+0.5,'red circle: monster, blue circle: pit, green circle:gold',fontsize=15,
    #          verticalalignment="center", horizontalalignment="center")
    # plt.legend((wumpus,pit,gold),('wumpus', 'pit', 'gold'))
    # plt.legend(bbox_to_anchor=(0.6,0.95))
    x = np.arange(column+1)
    y1 = np.zeros((row+1,), dtype = np.int)
    y2 = np.array([row]*(column+1))
    plt.fill_between(x, y1, y2, where=(y2 > y1), facecolor=(0.8, 0.8, 0.8), interpolate=True)
    draw_background(safe_room, (0.73, 1, 1)) # 	69 139 116  (0.27, 0.54, 0.45)
    draw_background(close_room, (0.3, 1, 0.6))
    draw_background(dangerous_room, (0.5, 0.55, 0.1))
    draw_background(doubtful_room, (0.9, 0.6, 0.9))
    # plt.text(row / 2, -0.7, 'percepts:$s_1$', fontdict={'size':12}, color='g', verticalalignment="center", horizontalalignment="center")


def draw_route(search_room_list, map_info):  #,safe_room,close_room,dangerous_room
    # draw_background(safe_room,(0.73, 1, 1)) # 	69 139 116  (0.27, 0.54, 0.45)
    # draw_background(close_room,(0.3, 1, 0.6))
    # draw_background(dangerous_room,(0.5, 0.25, 0.1))
    # 随机箭头颜色
    cmap = plt.cm.jet
    cNorm = colors.Normalize(vmin=0, vmax=len(search_room_list)-1)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    # 绘制地图信息
    draw_map()
    for wumpus_room_idx in map_info["wumpus"]:
        wumpus_x, wumpus_y = get_location(wumpus_room_idx)
        plt.text(wumpus_x - 0.4, wumpus_y, r'wumpus', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    for pit_room_idx in map_info["pit"]:
        pit_x, pit_y = get_location(pit_room_idx)
        plt.text(pit_x - 0.2, pit_y, r'pit', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    for gold_room_idx in map_info["gold"]:
        gold_x, gold_y = get_location(gold_room_idx)
        plt.text(gold_x - 0.3, gold_y, r'gold', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    for agent_init_room_idx in map_info["agent"]:
        agent_x, agent_y = get_location(agent_init_room_idx)
        plt.text(agent_x - 0.3, agent_y, r'agent', fontdict={'size': str(17 - 0.5 * (row + column)), 'color': 'black'})
    # wumpus_x, wumpus_y = get_location(map_info["wumpus"])
    # pit_x, pit_y = get_location(map_info["pit"])
    # gold_x, gold_y = get_location(map_info["gold"])
    # agent_x, agent_y = get_location(map_info["agent"])
    # plt.scatter(wumpus_x, wumpus_y, color='r', s=100)
    # plt.scatter(pit_x, pit_y, color='b', s=100)
    # plt.scatter(gold_x, gold_y, color='g', s=100)
    # plt.scatter(agent_x, agent_y, marker='^' ,color='black', s=100)
    # plt.text(wumpus_x-0.4, wumpus_y, r'wumpus', fontdict={'size': str(17-0.5*(row+column)), 'color': 'r'})
    # plt.text(pit_x-0.2, pit_y, r'pit', fontdict={'size': str(17-0.5*(row+column)), 'color': 'r'})
    # plt.text(gold_x-0.3, gold_y, r'gold', fontdict={'size': str(17-0.5*(row+column)), 'color': 'r'})
    # plt.text(agent_x-0.3, agent_y, r'agent', fontdict={'size': str(17-0.5*(row+column)), 'color': 'r'})
    current_room_x, current_room_y = get_location(search_room_list[0])
    for idx in range(1, len(search_room_list)):
        colorVal = scalarMap.to_rgba(idx)
        next_room_x, next_room_y = get_location(search_room_list[idx])
        plt.arrow(current_room_x, current_room_y, next_room_x - current_room_x, next_room_y - current_room_y,
                      width=0.08, color=colorVal, length_includes_head=True,overhang=0.5)
        current_room_x = next_room_x
        current_room_y = next_room_y
    plt.show()


def draw_state(direction,x,y):
    if direction == 'R':
        plt.scatter(x, y, marker='>', color='black', s=100)
        plt.pause(time_interval)
    if direction == 'F':
        plt.scatter(x, y, marker='^', color='black', s=100)
        plt.pause(time_interval)
    if direction == 'L':
        plt.scatter(x, y, marker='<', color='black', s=100)
        plt.pause(time_interval)
    if direction == 'B':
        plt.scatter(x, y, marker='v', color='black', s=100)
        plt.pause(time_interval)
    return

def state_change(state_sequence,safe_room,close_room,dangerous_room,doubtful_room):
    draw_map_information(map_info,safe_room,close_room,dangerous_room,doubtful_room)
    map_info
    init_state = state_sequence[0]
    init_direction = init_state[0]
    init_x, init_y = get_location(int(init_state[1:]))
    draw_state(init_direction,init_x,init_y)
    # plt.text(row/2, -0.7, 'percepts:' + str(perception), fontdict={'size': 12}, color='g', verticalalignment="center",
    #          horizontalalignment="center")
    # plt.pause(0.1)
    for state_idx in range(len(state_sequence)-1):
        ### 在房间内转向
        if state_sequence[state_idx+1][0] == state_sequence[state_idx][0]:
            x0, y0 = get_location(int(state_sequence[state_idx][1:]))
            x1, y1 = get_location(int(state_sequence[state_idx+1][1:]))
            x_array = np.linspace(x0, x1, 8)
            y_array = np.linspace(y0, y1, 8)
            for idx in range(len(x_array)):
                plt.cla()
                draw_map_information(map_info,safe_room,close_room,dangerous_room,doubtful_room)
                draw_state(state_sequence[state_idx+1][0],x_array[idx],y_array[idx])
                plt.pause(time_interval)
        ### 跨越房间
        else:
            plt.cla()
            draw_map_information(map_info,safe_room,close_room,dangerous_room,doubtful_room)
            x,y = get_location(int(state_sequence[state_idx + 1][1:]))
            draw_state(state_sequence[state_idx + 1][0],x,y)
            plt.pause(time_interval)



def perform(map_info):
    print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
          format("Percepts", "N(resolu pairs)", "N(ctrl p)", "N(new sem-p)",
                 "N(ls sem-p)", "N(sem-p in FKPNs)", "k", "Time(s)"))
    print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
          format(print_info[0][0], print_info[0][1], print_info[0][2], print_info[0][3], print_info[0][4],
                 print_info[0][5], print_info[0][6], print_info[0][7],))
    print_idx = 1
    generate_petrinet_json(row, column, 'reasoning.json')
    PNs = PetriNet('reasoning.json')
    # Agent 初始位置在 Room 1
    PNs.transition_fired("t_w1_")
    PNs.transition_fired("t_p1_")
    PNs_certain_transitions, PNs_uncertain_transitions = PNs.get_different_transitions()
    get_state_subnet(row, column, "state.json")
    PNs_state = PetriNet("state.json")
    cost = PNs_state.set_transition_cost()
    # map_info = get_map_info()
    start = time.process_time()
    current_room = map_info["agent"][0]
    PNs_state.get_one_place("R%d" % current_room).add_token(1)
    # print("current_room: %d" % current_room)
    close_room = [current_room]
    open_room = []
    dangerous_room = []
    uncertain_room = []
    reason_info = []
    perception_idx = 1
    perception = tell_agent_perception(map_info, current_room)
    for i in range(len(perception)):
        PNs.add_place('p%d^' % perception_idx, 0)
        PNs.add_arc( 'p%d^' % perception_idx, PNs.get_one_transition('t_' + perception[i]).get_dual_transition(), 1)
        perception_idx += 1
    node_list, edge_list = PNs.execute_certain(PNs_certain_transitions)
    reason_info = node_list[-1]
    while ('g' + str(current_room)) not in reason_info:
        for adjoining_room in adjoining_info[str(current_room)]:
            if ('w%d_' % adjoining_room in reason_info) and ('p%d_' % adjoining_room in reason_info) and (
                     adjoining_room not in close_room) and (adjoining_room not in open_room):
                open_room.append(adjoining_room)
        for room_idx in range(1, row*column+1):
            if (('w%d' % room_idx in reason_info) or ('p%d' % room_idx in reason_info)) and room_idx not in dangerous_room:
                dangerous_room.append(room_idx)
        certain_room = open_room + dangerous_room + close_room
        uncertain_room = [room_idx for room_idx in uncertain_room if room_idx not in certain_room]
        for adjoining_room in adjoining_info[str(current_room)]:
            if (adjoining_room  not in open_room) and (adjoining_room not in dangerous_room) and (adjoining_room not in close_room) and (adjoining_room not in uncertain_room):
                uncertain_room.append(adjoining_room)
        # print("These are uncertain rooms:",uncertain_room)
        if open_room:
            print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
                  format(print_info[print_idx][0], print_info[print_idx][1], print_info[print_idx][2], print_info[print_idx][3], print_info[print_idx][4],
                         print_info[print_idx][5], print_info[print_idx][6], print_info[print_idx][7], ))
            print_idx += 1
            # 随机选取一个安全房间进行探索
            # current_room = choice(open_room)
            # *************************************
            # 先探索房间号小的房间
            # open_room.sort()
            # current_room = open_room[0]
            # 先探索后放进open_room的房间
            safe_room = close_room + open_room
            safe_room.sort()
            PNs_state_subnet = action_subnet("state.json", safe_room)
            current_place = PNs_state.get_current_state(current_room)
            PNs_state_subnet.get_one_place(current_place).add_token(1)
            # target_place, state_sequence = PNs_state_subnet.get_state_sequence(open_room)#可达树搜索
            target_place, state_sequence = PNs_state_subnet.get_search_result(open_room)#一致代价搜索
            # print(state_sequence)
            doubtful_room=[]
            state_change(state_sequence,safe_room,close_room,dangerous_room,doubtful_room)
            # graph,safe_places = PNs_state.get_graph(safe_room)
            # current_place = PNs_state.get_current_state(current_room)
            # vertex = get_vertex(current_place, safe_places)
            # target_places_cost = dijkstra(graph,vertex,safe_places,open_room)
            # target_place = min(target_places_cost, key=target_places_cost.get)
            PNs_state.get_one_place(current_place).del_token(1)
            PNs_state.get_one_place(target_place).add_token(1)
            current_room = int(re.sub("\D", "", target_place))
            # print("current_room: %d" % current_room)
            open_room.remove(current_room)
            close_room.append(current_room)
        else:
            print("There is no safe room!")
            target_vars = []
            for room_idx in uncertain_room:
                if "w%d" % int(room_idx) in reason_info or "w%d_" % int(room_idx) in reason_info:
                    target_vars.append("p%d" % int(room_idx))
                elif "p%d" % int(room_idx) in reason_info or "p%d_" % int(room_idx) in reason_info:
                    target_vars.append("w%d" % int(room_idx))
                else:
                    target_vars.append("p%d" % int(room_idx))
                    target_vars.append("w%d" % int(room_idx))
            print(target_vars)
            uncertain_room_dict = {}
            for room_idx in uncertain_room:
                uncertain_room_dict[room_idx] = {}
                if "w%d" % int(room_idx) in target_vars:
                    PNs_copy = copy.deepcopy(PNs)
                    PNs_copy.pruning_for_probability("w%d" % int(room_idx))
                    all_probability = PNs_copy.get_reachable_graph()
                    PNs_copy.transition_fired("t_|w%d" % int(room_idx))
                    uncertain_room_dict[room_idx].update({"w%d" % int(room_idx): PNs_copy.get_reachable_graph() / all_probability})
                if "p%d" % int(room_idx) in target_vars:
                    PNs_copy = copy.deepcopy(PNs)
                    PNs_copy.pruning_for_probability("p%d" % int(room_idx))
                    all_probability = PNs_copy.get_reachable_graph()
                    PNs_copy.transition_fired("t_|p%d" % int(room_idx))
                    uncertain_room_dict[room_idx].update({"p%d" % int(room_idx): PNs_copy.get_reachable_graph() / all_probability})
            print(uncertain_room_dict)
            uncertain_room_probability = {}
            for room_idx in uncertain_room_dict.keys():
                final_probability = 0
                for probability in uncertain_room_dict[room_idx].values():
                    final_probability +=  probability
                uncertain_room_probability[room_idx] = final_probability
            print(uncertain_room_probability)
            min_probability = min(uncertain_room_probability.values())
            more_safe_rooms = [room_idx for room_idx in uncertain_room_probability if uncertain_room_probability[room_idx] == min_probability]
            choose_one_more_safe_room = random.choice(more_safe_rooms)
            print(choose_one_more_safe_room)
            open_room = [int(choose_one_more_safe_room)]
            doubtful_room = [int(choose_one_more_safe_room)]
            safe_room = open_room + close_room
            safe_room.sort()
            PNs_state_subnet = action_subnet("state.json", safe_room)
            current_place = PNs_state.get_current_state(current_room)
            PNs_state_subnet.get_one_place(current_place).add_token(1)
            # target_place, state_sequence = PNs_state_subnet.get_state_sequence(open_room)#可达树搜索
            target_place, state_sequence = PNs_state_subnet.get_search_result(open_room)  # 一致代价搜索
            print(state_sequence)
            safe_room = list(set(safe_room) - set(doubtful_room))
            state_change(state_sequence, safe_room, close_room, dangerous_room,doubtful_room)
            # graph,safe_places = PNs_state.get_graph(safe_room)
            # current_place = PNs_state.get_current_state(current_room)
            # vertex = get_vertex(current_place, safe_places)
            # target_places_cost = dijkstra(graph,vertex,safe_places,open_room)
            # target_place = min(target_places_cost, key=target_places_cost.get)
            PNs_state.get_one_place(current_place).del_token(1)
            PNs_state.get_one_place(target_place).add_token(1)
            current_room = int(re.sub("\D", "", target_place))
            print(current_room)
            open_room.remove(current_room)
            close_room.append(current_room)
            if choose_one_more_safe_room in map_info["wumpus"] or choose_one_more_safe_room in map_info["pit"]:
                print("The agent was killed!")
                print("mission failed!")
                break
            else:
                doubtful_room = []
                PNs.add_place('p%d^' % perception_idx, 0)
                PNs.add_arc('p%d^' % perception_idx, "t_w%d" %choose_one_more_safe_room,
                            1)
                perception_idx += 1
                PNs.add_place('p%d^' % perception_idx, 0)
                PNs.add_arc('p%d^' % perception_idx, "t_p%d" % choose_one_more_safe_room,
                            1)
                perception_idx += 1
        perception = tell_agent_perception(map_info, current_room)
        # plt.text(row / 2, -0.7, 'percepts:'+str(perception), fontdict={'size': 12}, color='g', verticalalignment="center",
        #          horizontalalignment="center")
        for i in range(len(perception)):
            PNs.add_place('p%d^' % perception_idx, 0)
            PNs.add_arc( 'p%d^' % perception_idx,PNs.get_one_transition('t_' + perception[i]).get_dual_transition(),1)
            perception_idx += 1
        node_list, edge_list = PNs.execute_certain(PNs_certain_transitions)
        reason_info = node_list[-1]
        # print(reason_info)
    print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
          format(print_info[print_idx][0], print_info[print_idx][1], print_info[print_idx][2], print_info[print_idx][3],
                 print_info[print_idx][4],
                 print_info[print_idx][5], print_info[print_idx][6], print_info[print_idx][7], ))
    plt.pause(0.02)
    plt.close()
    end = time.process_time()
    # print(str(end - start))
    draw_route(close_room, map_info)


if __name__ == "__main__":
    map_info = get_map_info()
    all_resolution()
    perform(map_info)




