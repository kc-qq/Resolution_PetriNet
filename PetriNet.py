import numpy as np
import json
import os
import re
from graphviz import Digraph
import sys
from sw_config import *


MAX = sys.maxsize
known_symbols_list = []
node_list = []
edge_list = []

class Place:
    def __init__(self, name, token_num, probability=0, pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if post_arcs is None:
            post_arcs = {}
        self.__name = name
        self.__token_num = token_num
        self.__probability = probability
        self.__pre_arcs = pre_arcs
        self.__post_arcs = post_arcs

    def set_token(self, number):
        self.__token_num = number

    def add_token(self, number):
        self.__token_num += number

    def del_token(self, number):
        if self.__token_num >= number:
            self.__token_num -= number
        else:
            print(self.get_name())
            raise ValueError

    def get_name(self):
        return self.__name

    def get_token_num(self):
        return self.__token_num

    def get_probability(self):
        return self.__probability

    def get_place_probability(self):
        return self.__token_num * self.__probability

    def get_pre_arcs(self):
        return self.__pre_arcs

    def get_post_arcs(self):
        return self.__post_arcs

    def get_info(self):
        return self.__name, self.__token_num, self.__probability, self.__pre_arcs, self.__post_arcs


class Transition:
    def __init__(self, name, dual_transition="", pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if pre_arcs is None:
            pre_arcs = {}
        self.__name = name
        self.__dual_transition = dual_transition
        self.__pre_arcs = pre_arcs
        self.__post_arcs = post_arcs

    def get_name(self):
        return self.__name

    def get_dual_transition(self):
        return self.__dual_transition

    def get_pre_arcs(self):
        return self.__pre_arcs

    def get_pre_dict(self):
        pre_arcs = self.get_pre_arcs()
        pre_place_list = []
        pre_weight_list = []
        for pre_arc in pre_arcs:
            pre_place_list.append(pre_arc["place_name"])
            pre_weight_list.append(pre_arc["weight"])
        pre_dict = dict.fromkeys(pre_place_list, pre_weight_list)
        return pre_dict

    def get_post_arcs(self):
        return self.__post_arcs

    def get_info(self):
        return [self.__name, self.__dual_transition, self.__pre_arcs, self.__post_arcs]


class PetriNet:
    def __init__(self, json_path):
        # self.__name = name
        self.places = {}
        self.transitions = {}
        if os.path.isfile(json_path):
            with open(json_path, 'r', encoding='utf-8') as file:  # 读取配置文件
                data_dict = json.load(file)
            if "places" in data_dict:
                for place_name, place_info in data_dict['places'].items():
                    if 'probability' in place_info.keys():
                        self.places[place_name] = Place(name=place_name, token_num=place_info['token_num'],
                                                        probability=place_info['probability'], pre_arcs= place_info['pre_arcs'], post_arcs= place_info['post_arcs'])
                    else:
                        self.places[place_name] = Place(name=place_name, token_num=place_info['token_num'],
                                                        pre_arcs= place_info['pre_arcs'], post_arcs= place_info['post_arcs'])
            if 'transitions' in data_dict:
                for transition_name, transition_info in data_dict['transitions'].items():
                    tran_name = transition_name
                    tran_pre_arcs = transition_info['pre_arcs']
                    tran_post_arcs = transition_info['post_arcs']
                    if 'dual_transition' in transition_info.keys():
                        tran_dual_transition = transition_info['dual_transition']
                        self.transitions[tran_name] = Transition(name=tran_name, dual_transition=tran_dual_transition,
                                                              pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
                    else:
                        self.transitions[tran_name] = Transition(name=tran_name, pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
        else:
            print("请输入JSON文件的路径！")

    def add_place(self, place_name, token_num,  probability=0, place_pre_arcs=None, place_post_arcs=None):
        if place_pre_arcs is None:
            place_pre_arcs = {}
        if place_post_arcs is None:
            place_post_arcs = {}
        self.places[place_name] = Place(name=place_name, token_num=token_num, probability=probability, pre_arcs= place_pre_arcs, post_arcs= place_post_arcs)
        for pre_transition in place_pre_arcs.keys():
            self.get_one_transition(pre_transition).get_post_arcs().update({place_name: place_pre_arcs[pre_transition]})
        for post_transition in place_post_arcs.keys():
            self.get_one_transition(post_transition).get_pre_arcs().update({place_name: place_post_arcs[post_transition]})
        return

    def add_transition(self, tran_name, tran_dual_transition="", tran_pre_arcs=None, tran_post_arcs=None):
        if tran_post_arcs is None:
            tran_post_arcs = {}
        if tran_pre_arcs is None:
            tran_pre_arcs = {}
        self.transitions[tran_name] = Transition(name=tran_name, dual_transition=tran_dual_transition,
                                                  pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
        for pre_place in tran_pre_arcs.keys():
            self.get_one_place(pre_place).get_post_arcs().update({tran_name: tran_pre_arcs[pre_place]})
        for post_place in tran_post_arcs.keys():
            self.get_one_place(post_place).get_pre_arcs().update({tran_name: tran_post_arcs[post_place]})
        return

    def add_arc(self, start, target, weight):
        if start in self.places.keys() and target in self.transitions.keys():
            self.places[start].get_post_arcs().update({target: weight})
            self.transitions[target].get_pre_arcs().update({start: weight})
        elif start in self.transitions.keys() and target in self.places.keys():
            self.places[target].get_pre_arcs().update({start: weight})
            self.transitions[start].get_post_arcs().update({target: weight})
        return

    def del_place(self,place_name):
        for pre_transition in self.get_one_place(place_name).get_pre_arcs().keys():
            del self.get_one_transition(pre_transition).get_post_arcs()[place_name]
        for post_transition in self.get_one_place(place_name).get_post_arcs().keys():
            del self.get_one_transition(post_transition).get_pre_arcs()[place_name]
        del self.places[place_name]
        return

    def del_transition(self,tran_name):
        for pre_place in self.get_one_transition(tran_name).get_pre_arcs().keys():
            del self.get_one_place(pre_place).get_post_arcs()[tran_name]
        for post_place in self.get_one_transition(tran_name).get_post_arcs().keys():
            del self.get_one_place(post_place).get_pre_arcs()[tran_name]
        del self.transitions[tran_name]
        return

    def get_places(self):
        return self.places

    def get_transitions(self):
        return self.transitions

    # def get_place_dict(self):
    #     place_dict = {}
    #     for place_idx in range(len(self.__place)):
    #         place_name = self.__place[place_idx].get_name()
    #         token_num = self.__place[place_idx].get_token_num()
    #         place_dict.update({place_name: token_num})
    #     return place_dict

    def get_one_place(self, name, place=None):
        if place is None:
            place = {}
        place = self.places[name]
        return place

    def get_one_transition(self, name, transition=None):
        if transition is None:
            transition = {}
        transition = self.transitions[name]
        return transition

    def get_different_transitions(self):
        transitions_certain = []
        transitions_uncertain = []
        for transition_idx in self.transitions.keys():
            if self.get_one_transition(transition_idx).get_dual_transition() == "":
                transitions_uncertain.append(transition_idx)
            else:
                transitions_certain.append(transition_idx)
        return transitions_certain, transitions_uncertain

    def transition_fired(self, transition_name):
        for pre_place, weight in self.get_one_transition(transition_name).get_pre_arcs().items():
            # try:
            self.get_one_place(pre_place).del_token(weight)
        #     except ValueError:
        #         conflict_flag = True
        #         break
        # if conflict_flag:
        #     break
        for post_place, weight in self.get_one_transition(transition_name).get_post_arcs().items():
            self.get_one_place(post_place).add_token(weight)
        return

    def get_enabled_transitions(self):
        enabled_transitions = []
        for transition_idx, transition in self.transitions.items():
            pre_arcs = transition.get_pre_arcs()
            pre_token = []
            pre_weight = []
            for pre_place, weight in pre_arcs.items():
                pre_token.append(self.get_one_place(pre_place).get_token_num())
                pre_weight.append(weight)
            if (np.array(pre_token) >= np.array(pre_weight)).all():
                enabled_transitions.append(self.transitions[transition_idx].get_name())
        return enabled_transitions

    def get_r_enabled_transitions(self, certain_transitions):
        r_enabled_transitions = []
        enabled_transitions = self.get_enabled_transitions()
        for transition_name in enabled_transitions:
            if transition_name in certain_transitions:
                transition = self.get_one_transition(transition_name)
                if transition.get_dual_transition() not in enabled_transitions:
                    r_enabled_transitions.append(transition_name)
        return r_enabled_transitions

    # def get_known_symbols(self):
    #     known_symbols = []
    #     for key, value in self.get_place().items():
    #         if ('s' in key or 'w' in key) and (value == 1):
    #             known_symbols.append(key)
    #     return known_symbols

    def execute_certain(self, certain_transitions):
        r_enabled_transitions = self.get_r_enabled_transitions(certain_transitions)
        # reason_num = 0
        global known_symbols_list
        global node_list
        global edge_list
        while r_enabled_transitions:
            for transition_name in r_enabled_transitions:
                # reason_num += 1
                transition = self.get_one_transition(transition_name)
                for pre_place, weight in transition.get_pre_arcs().items():
                    # try:
                    self.get_one_place(pre_place).del_token(weight)
                #     except ValueError:
                #         conflict_flag = True
                #         break
                # if conflict_flag:
                #     break
                for post_place, weight in transition.get_post_arcs().items():
                    self.get_one_place(post_place).add_token(weight)
                    known_symbols_list.append(post_place)
                    #node_list.append(known_symbols_list.copy())
                    edge_list.append(transition_name)
                node_list.append(known_symbols_list.copy())
            r_enabled_transitions = self.get_r_enabled_transitions(certain_transitions)
        return node_list, edge_list

    def get_mark(self):
        mark = []
        place_dict = self.places
        for place_name in place_dict.keys():
            mark.append(self.get_one_place(place_name).get_token_num())
        return mark

    def set_places_token(self, mark=[]):
        idx = 0
        for place_info in self.places.values():
            place_info.set_token(mark[idx])
            idx += 1
        return 0

    def get_reachable_graph(self):
        m0 = self.get_mark()
        # 定义一个列表来存储节点信息，每一个节点包括标识、是否为新节点、达到该标识所激发的变迁集、变迁对应父节点集、是否为叶节点、到达叶子节点的概率
        reachable_graph = [[None, None, None, None, None, None]]
        reachable_graph[0]=[m0, True, [], [], True, 0]
        #i = 1
        new_node = [None, None,  None, None, None, None]  # 表示节点
        have_new = True  # 标志位，用于判断是否存在 new 节点
        while have_new:
            for node_idx in range(len(reachable_graph)):
                if reachable_graph[node_idx][1]:  # 判断是否为new
                    reachable_graph[node_idx][1] = False  # 为new，则选择这个节点，并将其置为old
                    self.set_places_token(reachable_graph[node_idx][0])
                    enabled_transitions = self.get_enabled_transitions()
                    if enabled_transitions:
                        reachable_graph[node_idx][4] = False
                    for enabled_transition in enabled_transitions:
                        self.transition_fired(enabled_transition)
                        mark = self.get_mark()
                        is_new = True  # 用于判断是否为新标识
                        for k in range(len(reachable_graph)):  # 与可达图中已有节点进行比较
                            if mark == reachable_graph[k][0]:
                                reachable_graph[k][2].append(enabled_transition)
                                reachable_graph[k][3].append(node_idx)
                                is_new = False
                                break
                        if is_new:
                            #i = i + 1
                            #print(i)
                            new_node[0] = mark
                            new_node[1] = True
                            new_node[2] = [enabled_transition]
                            new_node[3] = [node_idx]
                            new_node[4] = True
                            new_node[5] = 0
                            reachable_graph.append(new_node.copy())
                        self.set_places_token(reachable_graph[node_idx][0])
            have_new = False  # 用于判断可达图中是否存在new标识
            for node_index in range(len(reachable_graph)):
                if reachable_graph[node_index][1]:
                    have_new = True
                    break
        all_probability = 0
        leaf_nodes = {}
        for node_idx in range(len(reachable_graph)):
            if reachable_graph[node_idx][4]:
                reachable_graph[node_idx][5] = 1
                self.set_places_token(reachable_graph[node_idx][0])
                for place_name in self.places.keys():
                    if self.get_one_place(place_name).get_place_probability() > 0:
                        reachable_graph[node_idx][5] = reachable_graph[node_idx][5]*self.get_one_place(place_name).\
                            get_place_probability()
                all_probability = all_probability + reachable_graph[node_idx][5]
                leaf_node_mark = str(reachable_graph[node_idx][0])
                leaf_nodes.update({leaf_node_mark:reachable_graph[node_idx][5]})
        self.set_places_token(m0)
        # 运行整个例子时，输出改为 all_probability
        return all_probability
        # return all_probability, leaf_nodes

    def set_transition_cost(self, cost=None):
        if cost is None:
            cost = [2, 3]
        transition_cost = {}
        for transition in self.transitions.keys():
            room = re.findall(r"\d+\.?\d*", transition)
            if room[0] == room[1]:
                transition_cost[transition] = cost[0]
            else:
                transition_cost[transition] = cost[1]
        return transition_cost

    def get_current_state(self,current_room):
        current_state = ""
        current_room_places = get_current_room_places(current_room)
        for place_name in current_room_places:
            token_num = self.get_one_place(place_name).get_token_num()
            if token_num == 1:
                current_state = place_name
                break
        return current_state

    def pruning_for_probability(self, target_var):
        # 删除不含概率的变量的库所、变迁
        for transition in list(self.transitions.keys()):
            for post_place in list(self.get_one_transition(transition).get_post_arcs().keys()):
                if self.get_one_place(post_place).get_probability()==0:
                    # self.del_place(post_place)
                    self.del_transition(transition)
        # 删除不能使能的变迁
        for transition in list(self.transitions.keys()):
            if transition not in self.get_enabled_transitions():
                self.del_transition(transition)
        # 删除没起约束的监控库所
        for place in list(self.places.keys()):
            if len(self.get_one_place(place).get_post_arcs().keys()) and len(
                    self.get_one_place(place).get_post_arcs().keys()) <= self.get_one_place(place).get_token_num():
                self.del_place(place)
        # 找与目标变量关联的库所集
        target_places = []
        for place in self.places.keys():
             if target_var in place:
                 target_places.append(place)
        # open表储存待扩展库所
        open_places = target_places
        # close表储存已扩展库所
        close_places = []
        while open_places:
            place = open_places[0]
            for pre_transition in self.get_one_place(place).get_pre_arcs().keys():
                extend_place = list(set(list(self.get_one_transition(pre_transition).get_pre_arcs().keys()) +
                                        list(self.get_one_transition(pre_transition).get_post_arcs().keys())) - set(close_places))
                open_places = list(set(open_places + extend_place))
            for post_transition in self.get_one_place(place).get_post_arcs().keys():
                extend_place = list(set(list(self.get_one_transition(post_transition).get_pre_arcs().keys()) +
                                        list(self.get_one_transition(post_transition).get_post_arcs().keys())) - set(close_places))
                open_places = list(set(open_places + extend_place))
            open_places.remove(place)
            close_places.append(place)
        # 找到Petri网中与目标变量没有连通的库所
        disconnect_places = list(set(list(self.places.keys())) - set(close_places))
        for place in disconnect_places:
            self.del_place(place)
        # 删除没有连接变迁的库所
        for place in list(self.places.keys()):
            if self.get_one_place(place).get_post_arcs() == {} and self.get_one_place(place).get_pre_arcs() == {}:
                self.del_place(place)
        # 删除没有连接库所的变迁
        for transition in list(self.transitions.keys()):
            if self.get_one_transition(transition).get_post_arcs() == {} and self.get_one_transition(transition).get_pre_arcs() == {}:
                self.del_transition(transition)
        return

def get_safe_places(safe_room):
    safe_places = []
    for safe_room_idx in safe_room:
        safe_places.append("F%d" % safe_room_idx)
        safe_places.append("R%d" % safe_room_idx)
        safe_places.append("B%d" % safe_room_idx)
        safe_places.append("L%d" % safe_room_idx)
    return safe_places

def get_current_room_places(current_room):
    current_room_places = ["F%d" % current_room,"R%d" % current_room,"B%d" % current_room,"L%d" % current_room]
    return current_room_places

def get_target_places(open_room):
    target_places = []
    for safe_room_idx in open_room:
        target_places.append("F%d" % safe_room_idx)
        target_places.append("R%d" % safe_room_idx)
        target_places.append("B%d" % safe_room_idx)
        target_places.append("L%d" % safe_room_idx)
    return target_places


class action_subnet(PetriNet):
    def __init__(self, json_path, safe_room):
        self.safe_places = get_safe_places(safe_room)
        self.places = {}
        self.transitions = {}
        if os.path.isfile(json_path):
            with open(json_path, 'r', encoding='utf-8') as file:  # 读取配置文件
                data_dict = json.load(file)
            if "places" in data_dict:
                for place_name, place_info in data_dict['places'].items():
                    if place_name in self.safe_places:
                        if 'probability' in place_info.keys():
                            self.places[place_name] = Place(name=place_name, token_num=place_info['token_num'],
                                                            probability=place_info['probability'],
                                                            pre_arcs=place_info['pre_arcs'],
                                                            post_arcs=place_info['post_arcs'])
                        else:
                            self.places[place_name] = Place(name=place_name, token_num=place_info['token_num'],
                                                            pre_arcs=place_info['pre_arcs'],
                                                            post_arcs=place_info['post_arcs'])
            if 'transitions' in data_dict:
                for transition_name, transition_info in data_dict['transitions'].items():
                    pre_places = transition_info['pre_arcs'].keys()
                    post_places = transition_info['post_arcs'].keys()
                    if set(pre_places) <= set(self.safe_places) and set(post_places) <= set(self.safe_places):
                        tran_name = transition_name
                        tran_pre_arcs = transition_info['pre_arcs']
                        tran_post_arcs = transition_info['post_arcs']
                        if 'dual_transition' in transition_info.keys():
                            tran_dual_transition = transition_info['dual_transition']
                            self.transitions[tran_name] = Transition(name=tran_name, dual_transition=tran_dual_transition,
                                                                  pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
                        else:
                            self.transitions[tran_name] = Transition(name=tran_name, pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
        else:
            print("请输入JSON文件的路径！")

    def get_state_place(self,current_mark):
        for place_idx in range(len(current_mark)):
            if current_mark[place_idx] == 1:
                state_place = self.safe_places[place_idx]
                break
        return state_place

    def dijkstra_search(self, open_room):
        transition_cost = self.set_transition_cost()
        target_places = get_target_places(open_room)
        m0 = self.get_mark()
        # 定义一个列表来存储数据，表示标识、到达该标识的最小代价、最小代价对应的父节点
        open_list = [[None, None, None]]
        close_list = []
        open_list[0] = [m0, 0, m0]
        current_state = self.get_state_place(open_list[0][0])
        while current_state not in target_places:
            m = open_list[0]
            close_list.append(open_list.pop(0))
            self.set_places_token(m[0])
            enabled_transitions = self.get_enabled_transitions()
            for enabled_transition in enabled_transitions:
                self.transition_fired(enabled_transition)
                m_ = self.get_mark()
                in_close_list = False
                for k in range(len(close_list)):  # 与close表中已有节点进行比较
                    if m_ == close_list[k][0]:
                        in_close_list = True
                        break
                if in_close_list:
                    self.set_places_token(m[0])
                    continue
                new_mark = True  # 用于判断是否为新标识
                for k in range(len(open_list)):  # 与open表中已有节点进行比较
                    if m_ == open_list[k][0]:
                        new_cost = m[1] + transition_cost[enabled_transition]
                        if new_cost < open_list[k][1]:
                            open_list[k][1] = new_cost
                            open_list[k][2] = m[0]
                        new_mark = False
                        break
                if new_mark:
                    open_list.append([m_,m[1] + transition_cost[enabled_transition],m[0]])
                self.set_places_token(m[0])
            open_list.sort(key = lambda node:(node[1]))
            current_state = self.get_state_place(open_list[0][0])
        close_list.append(open_list[0])
        self.set_places_token(m0)
        return close_list

    # Dijkstra 搜索
    def get_search_result(self,open_room):
        search_tree = self.dijkstra_search(open_room)
        state_dict = {}
        target_state = self.get_state_place(search_tree[-1][0])
        state_sequence = [target_state]
        for node in search_tree:
            state_dict[self.get_state_place(node[0])]={"cost":node[1],"father":self.get_state_place(node[2])}
        while state_dict[state_sequence[0]]["father"] !=state_sequence[0]:
            state_sequence.insert(0, state_dict[state_sequence[0]]["father"])
        return target_state, state_sequence

    # 可达树搜索
    def get_state_sequence(self,open_room):
        target_places = get_target_places(open_room)
        reachable_graph = self.get_reachable_graph(open_room)
        state_dict = {}
        state_info = {}
        mark_list = []
        for node in reachable_graph:
            for place_idx in range(len(node[0])):
                if node[0][place_idx] ==1:
                    state_info.clear()
                    state_info["cost"] = node[2]
                    state_dict[self.safe_places[place_idx]] = state_info.copy()
                    mark_list.append(self.safe_places[place_idx])
                    break
        for mark_idx in range(len(reachable_graph)):
            state_dict[mark_list[mark_idx]]["father"] = mark_list[reachable_graph[mark_idx][3]]
        state_sequence = []
        min_cost = MAX
        for state,state_info in state_dict.items():
            if state in target_places and state_info["cost"] < min_cost:
                min_cost = state_info["cost"]
                target_state = state
        state_sequence.append(target_state)
        while state_dict[state_sequence[0]]["father"] !=state_sequence[0]:
            state_sequence.insert(0,state_dict[state_sequence[0]]["father"])
        return target_state,state_sequence


if __name__ == "__main__":
    PNs = PetriNet("33_sw_1")

    # certain_transitions, uncertain_transitions = PNs.get_different_transitions()
    # PNs.add_place('p0^', 0)#1号房间无怪兽
    # PNs.add_place('p1^', 0)#1号房间无臭气
    # PNs.add_place('p2^', 0)#2号房间有臭气
    # PNs.add_place('p3^', 0)#2号房间有臭气
    # PNs.add_pre_arc('t_w1', 'p1^', 1)
    # PNs.add_pre_arc('t_s1', 'p1^', 1)
    # PNs.add_pre_arc('t_s2_', 'p2^', 1)
    # PNs.add_pre_arc('t_s4_', 'p3^', 1)
    # PNs.execute_certain(certain_transitions)
    # m_0 = PNs.get_mark()
    # #### 可达图跑的全概率
    # graph, p = PNs.get_reachable_graph(uncertain_transitions)
    # #### 恢复不确定库所的初始标识
    # PNs.set_places_token(m_0)
    # #### 设置5号房间有怪兽
    # PNs.transition_fired("t_|w7")
    # graph_1, p_1 = PNs.get_reachable_graph(uncertain_transitions)
    # #### 恢复不确定库所的初始标识
    # PNs.set_places_token(m_0)
    # #### 设置5号房间无怪兽
    # PNs.transition_fired("t_|w7_")
    # graph_2, p_2 = PNs.get_reachable_graph(uncertain_transitions)
    # p_w3_perceives = p_1 / p
    # p_w3__perceives = p_2 / p
    # print(p_w3_perceives, p_w3__perceives)


