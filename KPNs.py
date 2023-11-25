from PetriNet1 import *
from World import *
import copy
import time

known_symbols_list = []
node_list = []
edge_list = []
composed_num = 0
composed_num_without_tautological = 0
resolution_structures_num = 0

percepts_output_33 = ['s1_', 'b1_', '!g1_',
                      's2_', 'b2', '!g2_',
                      's4', 'b4_', '!g4_',
                      's5_', 'b5_', '!g5_',
                      's6_', 'b6', '!g6_',
                      's8', 'b8_', '!g8_',
                      's9_', 'b9_', '!g9']
percepts_output_66= ['s1_', 'b1_', '!g1_', 's2_', 'b2_', '!g2_', 's3', 'b3_', '!g3_', 's8_', 'b8_',
                    '!g8_', 's14_', 'b14_', '!g14_', 's20', 'b20_', '!g20_', 's15_', 'b15_', '!g15_',
                    's16_', 'b16_', '!g16_', 's17_', 'b17', '!g17_', 's22_', 'b22_', '!g22_',
                    's28_', 'b28_', '!g28_', 's34_', 'b34_', '!g34_', 's35_', 'b35_', '!g35']
percepts_output_1010 = ['s1_', 'b1_', '!g1_', 's2_', 'b2_', '!g2_', 's3_', 'b3_', '!g3_', 's4', 'b4_',
                       '!g4_', 's13_', 'b13_', '!g13_', 's23_', 'b23_', '!g23_', 's33_', 'b33_', '!g33_',
                       's43_', 'b43_', '!g43_', 's53', 'b53_', '!g53_', 's44_', 'b44_', '!g44_',
                       's45_', 'b45_', '!g45_', 's46_', 'b46_', '!g46_', 's47_', 'b47', '!g47_',
                       's56_', 'b56_', '!g56']

print_info = []

class C_Place(Place1):
    def __init__(self, name, token_num, post_arcs=None, constraint_symbols=None):
        if post_arcs is None:
            post_arcs = {}
        if constraint_symbols is None:
            constraint_symbols = {}
        Place1.__init__(self, name=name, token_num=token_num, post_arcs=post_arcs)
        self.constraint_symbols = constraint_symbols

    def get_constraint_symbols(self):
        return self.constraint_symbols

    def get_constraint_generalized_literals(self):
        return list(self.constraint_symbols.values())


class K_Place(Place1):
    def __init__(self, name, token_num, probability, pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if post_arcs is None:
            post_arcs = {}
        Place1.__init__(self, name=name, token_num=token_num, pre_arcs=pre_arcs, post_arcs=post_arcs)
        self.probability = probability

    def get_probability(self):
        return self.probability


class K_Transition(Transition1):
    def __init__(self, name, dual_transition, pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if post_arcs is None:
            post_arcs = {}
        Transition1.__init__(self, name=name, pre_arcs=pre_arcs, post_arcs=post_arcs)
        self.dual_transition = dual_transition

    def get_dual_transition(self):
        return self.dual_transition


# 无概率信息的符号, 3个库所："~" + symbol_name、symbol_name 和 symbol_name + "_"
class SPN_0(PetriNet1):
    def __init__(self, symbol_name):
        PetriNet1.__init__(self)
        p0 = Place1(name="~" + symbol_name, token_num=1,
                     post_arcs={"t_" + symbol_name: 1, "t_" + symbol_name + "_": 1})
        p1 = Place1(name=symbol_name, token_num=0, pre_arcs={"t_" + symbol_name: 1})
        p2 = Place1(name=symbol_name + "_", token_num=0, pre_arcs={"t_" + symbol_name + "_": 1})
        t0 = K_Transition(name="t_" + symbol_name, dual_transition="t_" + symbol_name + "_",
                          pre_arcs={"~" + symbol_name: 1}, post_arcs={symbol_name: 1})
        t1 = K_Transition(name="t_" + symbol_name + "_", dual_transition="t_" + symbol_name,
                          pre_arcs={"~" + symbol_name: 1}, post_arcs={symbol_name + "_": 1})
        self.places = {p0.get_name(): p0, p1.get_name(): p1, p2.get_name(): p2}
        self.transitions = {t0.get_name(): t0, t1.get_name(): t1}
        self.transitions_certain = ["t_" + symbol_name, "t_" + symbol_name + "_"]

    def get_positive_correlated_places(self):
        tran_true = self.transitions_certain[0]
        positive_correlated_places = []
        for pre_place in self.get_one_transition(tran_true).get_pre_arcs().keys():
            if pre_place[0] == "r":
                positive_correlated_places.append(pre_place)
        return positive_correlated_places

    def get_negative_correlated_places(self):
        tran_true = self.transitions_certain[1]
        negative_correlated_places = []
        for pre_place in self.get_one_transition(tran_true).get_pre_arcs().keys():
            if pre_place[0] == "r":
                negative_correlated_places.append(pre_place)
        return negative_correlated_places

    def get_r_enable_transition(self):
        tran_true = self.transitions_certain[0]
        tran_false = self.transitions_certain[1]
        if self.judge_transition_enable(tran_true):
            if not self.judge_transition_enable(tran_false):
                return tran_true
        elif self.judge_transition_enable(tran_false):
            return tran_false
        return False


# 具有先验概率的符号, pp = prior probability
# 5个库所："~" + symbol_name、symbol_name、symbol_name + "_"、"|" + symbol_name 和 "|" + symbol_name + "_"
class SPN_1(SPN_0):
    def __init__(self, symbol_name, pp):
        SPN_0.__init__(self, symbol_name)
        p3 = K_Place(name="|" + symbol_name, token_num=0, probability=pp, pre_arcs={"t_|" + symbol_name: 1})
        p4 = K_Place(name="|" + symbol_name + "_", token_num=0, probability=1 - pp,
                     pre_arcs={"t_|" + symbol_name + "_": 1})
        t2 = Transition(name="t_|" + symbol_name, pre_arcs={"~" + symbol_name: 1}, post_arcs={"|" + symbol_name: 1})
        t3 = Transition(name="t_|" + symbol_name + "_", pre_arcs={"~" + symbol_name: 1},
                        post_arcs={"|" + symbol_name + "_": 1})
        self.places["~" + symbol_name].get_post_arcs().update({"t_|" + symbol_name: 1, "t_|" + symbol_name + "_": 1})
        self.places.update({p3.get_name(): p3, p4.get_name(): p4})
        self.transitions.update({t2.get_name(): t2, t3.get_name(): t3})
        self.transitions_uncertain = ["t_|" + symbol_name, "t_|" + symbol_name + "_"]


# 具有条件概率的符号，cp = condition probability,
# p的索引顺序与二进制码升序相同，如前置符号有两个, p[0]对应00,表示前置符号都为假的条件下该符号为真的概率
# cp_info = {"c":["p1"],"p":[0.1,0,6]};
# cp_info ={"c":["p1","p2"],"p":[0.1,0.3,0.5,0.4]};
# 3+ (2^n)*2个库所："~" + symbol_name、symbol_name、symbol_name + "_"、
# symbol_name + "|" + idx 和 symbol_name + "|" + idx + "_"
class SPN_2(SPN_0):
    def __init__(self, symbol_name, cp_info):
        SPN_0.__init__(self, symbol_name)
        pre_symbol_num = len(cp_info["c"])
        places_dict = {}
        transitions_dict = {}
        for pre_symbol_name in cp_info["c"]:
            places_dict.update({"*" + pre_symbol_name: Place_1(name="*" + pre_symbol_name, token_num=0)})
            places_dict.update({"*" + pre_symbol_name + "_": Place_1(name="*" + pre_symbol_name + "_", token_num=0)})
        combine_idx = 0
        while combine_idx < 2 ** pre_symbol_num:
            idx2bin = bin(combine_idx)[2:]
            while len(idx2bin) < pre_symbol_num:
                idx2bin = "0" + idx2bin
            places_dict.update({symbol_name + "|" + str(combine_idx):
                                    K_Place(name=symbol_name + "|" + str(combine_idx), token_num=0,
                                            probability=cp_info["p"][combine_idx],
                                            pre_arcs={"t_" + symbol_name + "|" + str(combine_idx): 1})})
            places_dict.update({symbol_name + "|" + str(combine_idx) + "_":
                                    K_Place(name=symbol_name + "|" + str(combine_idx) + "_", token_num=0,
                                            probability=1 - cp_info["p"][combine_idx],
                                            pre_arcs={"t_" + symbol_name + "|" + str(combine_idx) + "_": 1})})
            transitions_dict.update({"t_" + symbol_name + "|" + str(combine_idx):
                                         Transition(name="t_" + symbol_name + "|" + str(combine_idx),
                                                    pre_arcs={"~" + symbol_name: 1},
                                                    post_arcs={symbol_name + "|" + str(combine_idx): 1})})
            transitions_dict.update({"t_" + symbol_name + "|" + str(combine_idx) + "_":
                                         Transition(name="t_" + symbol_name + "|" + str(combine_idx) + "_",
                                                    pre_arcs={"~" + symbol_name: 1},
                                                    post_arcs={symbol_name + "|" + str(combine_idx) + "_": 1})})
            self.places["~" + symbol_name].add_post_arc("t_" + symbol_name + "|" + str(combine_idx), 1)
            self.places["~" + symbol_name].add_post_arc("t_" + symbol_name + "|" + str(combine_idx) + "_", 1)
            for pre_symbol_idx in range(pre_symbol_num):
                if idx2bin[pre_symbol_idx] == '0':
                    places_dict["*" + cp_info["c"][pre_symbol_idx] + "_"]. \
                        add_post_arc("t_" + symbol_name + "|" + str(combine_idx), 1)
                    places_dict["*" + cp_info["c"][pre_symbol_idx] + "_"]. \
                        add_post_arc("t_" + symbol_name + "|" + str(combine_idx) + "_", 1)
                    transitions_dict["t_" + symbol_name + "|" + str(combine_idx)] \
                        .add_pre_arc("*" + cp_info["c"][pre_symbol_idx] + "_", 1)
                    transitions_dict["t_" + symbol_name + "|" + str(combine_idx) + "_"] \
                        .add_pre_arc("*" + cp_info["c"][pre_symbol_idx] + "_", 1)
                else:
                    places_dict["*" + cp_info["c"][pre_symbol_idx]] \
                        .add_post_arc("t_" + symbol_name + "|" + str(combine_idx), 1)
                    places_dict["*" + cp_info["c"][pre_symbol_idx]] \
                        .add_post_arc("t_" + symbol_name + "|" + str(combine_idx) + "_", 1)
                    transitions_dict["t_" + symbol_name + "|" + str(combine_idx)] \
                        .add_pre_arc("*" + cp_info["c"][pre_symbol_idx], 1)
                    transitions_dict["t_" + symbol_name + "|" + str(combine_idx) + "_"] \
                        .add_pre_arc("*" + cp_info["c"][pre_symbol_idx], 1)
            combine_idx += 1
        self.places.update(places_dict)
        self.transitions.update(transitions_dict)
        self.transitions_uncertain = list(set(self.transitions.keys()) - set(self.transitions_certain))


class KPNs(PetriNet1):
    def __init__(self, symbol_info, semantic_constraint=None):
        PetriNet1.__init__(self)
        if semantic_constraint is None:
            semantic_constraint = {}
        generalized_literals, generalized_literal2symbol = get_generalized_literals(symbol_info)
        self.generalized_literals = generalized_literals
        self.generalized_literal2symbol = generalized_literal2symbol
        self.spn_set = {"spn0_set": {}, "spn1_set": {}, "spn2_set": {}, }
        self.monitor_set = {}
        self.monitor_num = 0
        self.transitions_certain = []
        self.transitions_uncertain = []
        self.k = {}
        # 0型符号Petri网
        for symbol0 in symbol_info["symbol0"]:
            spn0 = SPN_0(symbol0)
            self.spn_set["spn0_set"].update({symbol0: spn0})
            self.places.update(self.spn_set["spn0_set"][symbol0].places)
            self.transitions.update(self.spn_set["spn0_set"][symbol0].transitions)
            self.k.update({"t_" + symbol0: 0, "t_" + symbol0 + "_": 0})
        # 1型符号Petri网
        for symbol1, pp_info in symbol_info["symbol1"].items():
            spn1 = SPN_1(symbol1, pp_info)
            self.spn_set["spn1_set"].update({symbol1: spn1})
            self.places.update(self.spn_set["spn1_set"][symbol1].places)
            self.transitions.update(self.spn_set["spn1_set"][symbol1].transitions)
        # 用于后续计算条件变量作为条件的次数，从而设置条件库所的前置弧上的权值 c表示condition
        c_symbols = []
        # 2型符号Petri网
        for symbol2, cp_info in symbol_info["symbol2"].items():
            spn2 = SPN_2(symbol2, cp_info)
            self.spn_set["spn2_set"].update({symbol2: spn2})
            self.places.update(self.spn_set["spn2_set"][symbol2].places)
            self.transitions.update(self.spn_set["spn2_set"][symbol2].transitions)
            c_symbols.extend(cp_info["c"])
        # 语义约束的监控库所
        for rule, rule_info in semantic_constraint.items():
            self.design_monitor(rule, rule_info)
        # 条件库所的前置弧
        for c_symbol in list(set(c_symbols)):
            arc_weight = c_symbols.count(c_symbol)
            for literal in generalized_literals[c_symbol]:
                self.places["*" + c_symbol].add_pre_arc("t_" + literal, arc_weight)
                self.transitions["t_" + literal].add_post_arc("*" + c_symbol, arc_weight)
            for literal in generalized_literals[c_symbol + "_"]:
                self.places["*" + c_symbol + "_"].add_pre_arc("t_" + literal, arc_weight)
                self.transitions["t_" + literal].add_post_arc("*" + c_symbol + "_", arc_weight)
        # 确定变迁和概率变迁
        for transition_name in self.transitions.keys():
            if hasattr(self.get_one_transition(transition_name), "dual_transition"):
                self.transitions_certain.append(transition_name)
            else:
                self.transitions_uncertain.append(transition_name)

    def get_all_spn(self):
        all_spn = {}
        for spn_set in self.spn_set.values():
            all_spn.update(spn_set)
        return all_spn

    def get_one_spn(self, symbol_name):
        return self.get_all_spn()[symbol_name]

    def update_transitions(self):
        self.transitions_certain = []
        self.transitions_uncertain = []
        for transition_name in self.transitions.keys():
            if hasattr(self.get_one_transition(transition_name), "dual_transition"):
                self.transitions_certain.append(transition_name)
            else:
                self.transitions_uncertain.append(transition_name)
        return

    # def get_monitor_num(self):
    #     return len(self.monitor_set)

    def design_monitor(self, rule_name, constraint_generalized_literals):
        token = len(constraint_generalized_literals) - 1
        post_arcs = {}
        constraint_symbols = {}
        for generalized_literal in constraint_generalized_literals:
            for literal in self.generalized_literals[generalized_literal]:
                post_arcs.update({"t_" + literal: 1})
                self.transitions["t_" + literal].add_pre_arc(rule_name, 1)
                self.k["t_" + literal] += 1
            constraint_symbols.update({self.generalized_literal2symbol[generalized_literal]: generalized_literal})
        self.monitor_set.update({rule_name: C_Place(name=rule_name, token_num=token, post_arcs=post_arcs,
                                                    constraint_symbols=constraint_symbols)})
        self.places.update({rule_name: self.monitor_set[rule_name]})
        self.monitor_num += 1
        # constraint_generalized_literals = self.get_one_place(rule_name).get_constraint_generalized_literals()
        # constraint_generalized_literals.sort()
        return

    def pruning_monitor(self, monitor_name):
        self.del_place(monitor_name)
        del self.monitor_set[monitor_name]
        # print(monitor_name)
        return

    def check_redundant_monitor(self, monitor_name):
        is_redundancy = False
        # 找到子句库所约束的广义文字，将该归结库所与这些广义文字对应的变迁上的监控库所对比，判断是否为冗余子句库所。
        # 这样就可以避免遍历监控库所，降低计算复杂性
        constraint_generalized_literals = self.get_one_place(monitor_name).get_constraint_generalized_literals()
        for constraint_generalized_literal in constraint_generalized_literals:
            transition = self.get_one_transition("t_" + constraint_generalized_literal)
            for pre_place in transition.get_pre_arcs().keys():
                if pre_place[0] == "r" and pre_place != monitor_name and set(
                        self.get_one_place(pre_place).get_constraint_generalized_literals()).issubset(
                    set(constraint_generalized_literals)):
                    is_redundancy = True
                    break
            if is_redundancy:
                break
        return is_redundancy

    def search_redundant_monitors_for_new_monitor(self, new_monitor_name):
        redundant_monitors = []
        constraint_generalized_literals = self.get_one_place(new_monitor_name).get_constraint_generalized_literals()
        for constraint_generalized_literal in constraint_generalized_literals:
            transition = self.get_one_transition("t_" + constraint_generalized_literal)
            for pre_place in transition.get_pre_arcs().keys():
                if pre_place[0] == "r" and pre_place != new_monitor_name and set(
                        constraint_generalized_literals).issubset(set(
                    self.get_one_place(pre_place).get_constraint_generalized_literals())):
                    redundant_monitors.append(pre_place)
        redundant_monitors = list(set(redundant_monitors))
        return redundant_monitors

    def pruning_redundant_monitors_in_pn(self):
        monitor_list = list(self.monitor_set.keys())
        for monitor in monitor_list:
            if self.check_redundant_monitor(monitor):
                # print(monitor)
                self.pruning_monitor(monitor)
        return

    def get_resolution_structure_for_new_monitor(self, new_monitor_name):
        resolution_structure_for_new_monitor = {}
        true_forever_resolution_structures = []
        global composed_num
        global composed_num_without_tautological
        constraint_symbols = self.get_one_place(new_monitor_name).get_constraint_symbols()
        for constraint_symbol in constraint_symbols.keys():
            if constraint_symbols[constraint_symbol][-1] == "_":
                positive_correlated_places = self.get_one_spn(constraint_symbol).get_positive_correlated_places()
                compose2list = [(x, new_monitor_name) for x in positive_correlated_places]
            else:
                negative_correlated_places = self.get_one_spn(constraint_symbol).get_negative_correlated_places()
                compose2list = [(x, new_monitor_name) for x in negative_correlated_places]
            for idx in range(len(compose2list)):
                if int(compose2list[idx][0][1:]) > int(compose2list[idx][1][1:]):
                    compose2list[idx] = (compose2list[idx][1], compose2list[idx][0])
                if compose2list[idx] not in resolution_structure_for_new_monitor:
                    resolution_structure_for_new_monitor[compose2list[idx]] = constraint_symbol
                else:
                    true_forever_resolution_structures.append(compose2list[idx])
        # 删除永真归结结构
        for structure in set(true_forever_resolution_structures):
            del resolution_structure_for_new_monitor[structure]
        composed_num = composed_num + len(resolution_structure_for_new_monitor) \
                       + len(set(true_forever_resolution_structures))
        composed_num_without_tautological = composed_num_without_tautological + len(resolution_structure_for_new_monitor)
        # print(composed_num)
        # print(resolution_structure_for_new_monitor)
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        return resolution_structure_for_new_monitor

    def check_redundant_control_place(self, structure, constraint_generalized_literals):
        is_redundancy = False
        for resolution_place_constraint_generalized_literal in constraint_generalized_literals:
            transition = self.get_one_transition("t_" + resolution_place_constraint_generalized_literal)
            for pre_place in transition.get_pre_arcs().keys():
                if pre_place[0] != structure[0] and pre_place[0] != structure[1] and pre_place[0] == "r" and set(
                        self.get_one_place(pre_place).get_constraint_generalized_literals()).issubset(
                    set(constraint_generalized_literals)):
                    is_redundancy = True
                    break
            if is_redundancy:
                break
        return is_redundancy

    # def resolution_expand_old(self,new_clause_places):
    #     start = time.process_time()
    #     compose2dict = {}
    #     while new_clause_places:
    #         for clause_place in new_clause_places:
    #             constraint_symbols = self.get_one_place(clause_place).get_constraint_symbols()
    #             for symbol in constraint_symbols.keys():
    #                 if constraint_symbols[symbol][-1] == "_":
    #                     positive_correlated_places = self.get_one_spn(
    #                         symbol).get_positive_correlated_places()
    #                     compose2list = [(x, clause_place) for x in positive_correlated_places]
    #                 else:
    #                     negative_correlated_places = self.get_one_spn(
    #                         symbol).get_negative_correlated_places()
    #                     compose2list = [(x, clause_place) for x in negative_correlated_places]
    #                 resolution_symbol = [symbol] * len(compose2list)
    #                 compose2dict.update(dict(zip(compose2list, resolution_symbol)))
    #         new_clause_places = []
    #         for compose,symbol in compose2dict.items():
    #             resolution_place_constraint_generalized_literals = list(set(self.get_one_place(
    #                 compose[0]).get_constraint_generalized_literals() \
    #                                                                         + self.get_one_place(
    #                 compose[1]).get_constraint_generalized_literals()))
    #             correlated_symbols = [self.generalized_literal2symbol[literal] for literal in resolution_place_constraint_generalized_literals]
    #             if len(correlated_symbols) > len(set(correlated_symbols))+1:
    #                 continue
    #             resolution_place_constraint_generalized_literals.remove(symbol)
    #             resolution_place_constraint_generalized_literals.remove(symbol + "_")
    #             is_redundancy = False
    #             for resolution_place_constraint_generalized_literal in resolution_place_constraint_generalized_literals:
    #                 transition = self.get_one_transition("t_" + resolution_place_constraint_generalized_literal)
    #                 for pre_place in transition.get_pre_arcs().keys():
    #                     if pre_place[0] == "r" and set(
    #                             self.get_one_place(pre_place).get_constraint_generalized_literals()).issubset(
    #                         set(resolution_place_constraint_generalized_literals)):
    #                         is_redundancy = True
    #                         break
    #                 if is_redundancy:
    #                     break
    #             if not is_redundancy:
    #                 rule_idx = len(self.monitor_set) + 1
    #                 rule_name = "r" + str(rule_idx)
    #                 new_clause_places.append(rule_name)
    #                 self.design_monitor(rule_name, resolution_place_constraint_generalized_literals)
    #         print(new_clause_places)
    #     end = time.process_time()
    #     print("&&&&&&&&&&&&")
    #     print(str(end - start))
    #     return
    #
    # def resolution_in_pn_old(self):
    #     new_clause_places = []
    #     compose2dict = {}
    #     for spn_set in self.spn_set.values():
    #         for symbol, spn in spn_set.items():
    #             positive_correlated_places = spn.get_positive_correlated_places()
    #             negative_correlated_places = spn.get_negative_correlated_places()
    #             compose2list = [(x, y) for x in positive_correlated_places for y in negative_correlated_places]
    #             resolution_symbol = [symbol]*len(compose2list)
    #             compose2dict.update(dict(zip(compose2list,resolution_symbol)))
    #     print(len(compose2dict))
    #     for compose,symbol in compose2dict.items():
    #         correlated_symbols = list(self.get_one_place(
    #             compose[0]).get_constraint_symbols().keys()) \
    #                                                            + list(self.get_one_place(
    #             compose[1]).get_constraint_symbols().keys())
    #         if len(correlated_symbols) > len(set(correlated_symbols)) + 1:
    #             continue
    #         resolution_place_constraint_generalized_literals = list(set(self.get_one_place(
    #                 compose[0]).get_constraint_generalized_literals() \
    #                                                                + self.get_one_place(
    #                 compose[1]).get_constraint_generalized_literals()))
    #         resolution_place_constraint_generalized_literals.remove(symbol)
    #         resolution_place_constraint_generalized_literals.remove(symbol + "_")
    #         is_redundancy = False
    #         for resolution_place_constraint_generalized_literal in resolution_place_constraint_generalized_literals:
    #             transition = self.get_one_transition("t_" + resolution_place_constraint_generalized_literal)
    #             for pre_place in transition.get_pre_arcs().keys():
    #                 if pre_place[0] == "r" and set(
    #                         self.get_one_place(pre_place).get_constraint_generalized_literals()).issubset(
    #                         set(resolution_place_constraint_generalized_literals)):
    #                     is_redundancy = True
    #                     break
    #             if is_redundancy:
    #                 break
    #         if not is_redundancy:
    #             rule_idx = len(self.monitor_set) + 1
    #             rule_name = "r" + str(rule_idx)
    #             new_clause_places.append(rule_name)
    #             self.design_monitor(rule_name, resolution_place_constraint_generalized_literals)
    #     end = time.process_time()
    #     print(new_clause_places)
    #     print("&&&&&&&&&&&&")
    #     print(str(end - start))
    #     return new_clause_places
    #
    # def resolution_old(self):
    #     new_clause_places = self.resolution_in_pn_old()
    #     self.resolution_expand_old(new_clause_places)
    #     return
    #
    # def get_resolution_structure_expand(self, new_clause_places):
    #     resolution_structure = {}
    #     true_forever_resolution_structure = []
    #     global composed_num
    #     for clause_place in new_clause_places:
    #         constraint_symbols = self.get_one_place(clause_place).get_constraint_symbols()
    #         for constraint_symbol in constraint_symbols.keys():
    #             if constraint_symbols[constraint_symbol][-1] == "_":
    #                 positive_correlated_places = self.get_one_spn(constraint_symbol).get_positive_correlated_places()
    #                 compose2list = [(x, clause_place) for x in positive_correlated_places]
    #             else:
    #                 negative_correlated_places = self.get_one_spn(constraint_symbol).get_negative_correlated_places()
    #                 compose2list = [(x, clause_place) for x in negative_correlated_places]
    #             composed_num += len(compose2list)
    #             for idx in range(len(compose2list)):
    #                 if int(compose2list[idx][0][1:]) > int(compose2list[idx][1][1:]):
    #                     compose2list[idx] = (compose2list[idx][1], compose2list[idx][0])
    #                 if compose2list[idx] not in resolution_structure:
    #                     resolution_structure[compose2list[idx]] = constraint_symbol
    #                 else:
    #                     true_forever_resolution_structure.append(compose2list[idx])
    #     # 删除永真归结结构
    #     for structure in set(true_forever_resolution_structure):
    #         del resolution_structure[structure]
    #     return resolution_structure

    def get_resolution_structures_in_pn(self):
        self.pruning_redundant_monitors_in_pn()
        resolution_structures = {}
        true_forever_resolution_structures = []
        global composed_num
        global composed_num_without_tautological
        for spn_set in self.spn_set.values():
            for symbol, spn in spn_set.items():
                positive_correlated_places = spn.get_positive_correlated_places()
                negative_correlated_places = spn.get_negative_correlated_places()
                compose2list = [(x, y) for x in positive_correlated_places for y in negative_correlated_places]
                # 根据子句库所的id顺序储存,从而删除永真归结结构
                for idx in range(len(compose2list)):
                    if int(compose2list[idx][0][1:]) > int(compose2list[idx][1][1:]):
                        compose2list[idx] = (compose2list[idx][1], compose2list[idx][0])
                    if compose2list[idx] not in resolution_structures:
                        resolution_structures[compose2list[idx]] = symbol
                    else:
                        true_forever_resolution_structures.append(compose2list[idx])
        # 删除永真归结结构
        for structure in set(true_forever_resolution_structures):
            del resolution_structures[structure]
        composed_num = composed_num + len(resolution_structures) + len(set(true_forever_resolution_structures))
        composed_num_without_tautological = composed_num_without_tautological + len(resolution_structures)
        # print(composed_num)
        # print("##################################")
        # print(resolution_structures)
        # print("##################################")
        return resolution_structures

    def resolution(self, resolution_structures):
        global resolution_structures_num
        while resolution_structures:
            resolution_structures_num += 1
            structures = list(resolution_structures.keys())
            structure = structures[0]
            symbol = resolution_structures[structure]
            del resolution_structures[structure]
            resolution_place_constraint_generalized_literals = list(set(self.get_one_place(
                    structure[0]).get_constraint_generalized_literals() \
                                                                   + self.get_one_place(
                    structure[1]).get_constraint_generalized_literals()))
            resolution_place_constraint_generalized_literals.remove(symbol)
            resolution_place_constraint_generalized_literals.remove(symbol + "_")
            is_redundancy = self.check_redundant_control_place(structure, resolution_place_constraint_generalized_literals)
            if not is_redundancy:
                rule_idx = self.monitor_num + 1
                rule_name = "r" + str(rule_idx)
                self.design_monitor(rule_name, resolution_place_constraint_generalized_literals)
                redundant_monitors = self.search_redundant_monitors_for_new_monitor(rule_name)
                for monitor in redundant_monitors:
                    redundant_resolution_structures = self.get_resolution_structure_for_new_monitor(monitor).keys()
                    resolution_structures_set = set(resolution_structures.keys())
                    for redundant_resolution_structure in redundant_resolution_structures:
                        if redundant_resolution_structure in resolution_structures_set:
                            del resolution_structures[redundant_resolution_structure]
                            # print("***************************")
                            # print(redundant_resolution_structure)
                for monitor in redundant_monitors:
                    self.pruning_monitor(monitor)
                resolution_structures_for_new_monitor = self.get_resolution_structure_for_new_monitor(rule_name)
                resolution_structures.update(resolution_structures_for_new_monitor)
        # print("=============")
        # print(resolution_structures_num)
        # print("+++++++++++++")
        return


    # 单独写一个归结操作的函数，在进行归结时需要遍历归结结构，在归结结构较多时，计算复杂度高；
    # 在判断永真归结库所的时候遍历了归结结构，考虑将判断冗余归结库所和归结操作一块放在判断永真归结库所的循环体里，降低计算复杂度
    def resolution_try(self, resolution_structures):
        global resolution_structures_num
        resolution_structures_constraints = {}
        for resolution_structure, symbol in resolution_structures.items():
            constraint_generalized_literals = list(set(self.get_one_place(
                resolution_structure[0]).get_constraint_generalized_literals() \
                                                                        + self.get_one_place(
                resolution_structure[1]).get_constraint_generalized_literals()))
            constraint_generalized_literals.remove(symbol)
            constraint_generalized_literals.remove(symbol + "_")
            resolution_structures_constraints.update({resolution_structure: constraint_generalized_literals})
        while resolution_structures_constraints:
            resolution_structures_num += 1
            structure = min(resolution_structures_constraints.items(), key=lambda x: len(x[1]))[0]
            # structures = list(resolution_structures.keys())
            # structure = structures[0]
            # del resolution_structures[structure]
            is_redundancy = self.check_redundant_control_place(structure, resolution_structures_constraints[structure])
            if not is_redundancy:
                rule_idx = self.monitor_num + 1
                rule_name = "r" + str(rule_idx)
                self.design_monitor(rule_name, resolution_structures_constraints[structure])
                del resolution_structures_constraints[structure]
                redundant_monitors = self.search_redundant_monitors_for_new_monitor(rule_name)
                for monitor in redundant_monitors:
                    redundant_resolution_structures = self.get_resolution_structure_for_new_monitor(monitor).keys()
                    resolution_structures_set = set(resolution_structures_constraints.keys())
                    for redundant_resolution_structure in redundant_resolution_structures:
                        if redundant_resolution_structure in resolution_structures_set:
                            # del resolution_structures[redundant_resolution_structure]
                            del resolution_structures_constraints[redundant_resolution_structure]
                            print("***************************")
                            print(redundant_resolution_structure)
                for monitor in redundant_monitors:
                    self.pruning_monitor(monitor)
                resolution_structures_for_new_monitor = self.get_resolution_structure_for_new_monitor(rule_name)
                # resolution_structures.update(resolution_structures_for_new_monitor)
                for resolution_structure_,symbol in resolution_structures_for_new_monitor.items():
                    constraint_generalized_literals = list(set(self.get_one_place(
                        resolution_structure_[0]).get_constraint_generalized_literals() \
                                                               + self.get_one_place(
                        resolution_structure_[1]).get_constraint_generalized_literals()))
                    constraint_generalized_literals.remove(symbol)
                    constraint_generalized_literals.remove(symbol + "_")
                    resolution_structures_constraints.update({resolution_structure_: constraint_generalized_literals})
            else:
                del resolution_structures_constraints[structure]
        print("=============")
        print(resolution_structures_num)
        print("+++++++++++++")
        return

    def get_resolution_structures_expand(self, new_clause_places):
        resolution_structures = {}
        for monitor_name, constraint_generalized_literals in new_clause_places.items():
            self.design_monitor(monitor_name, constraint_generalized_literals)
            is_redundancy = self.check_redundant_monitor(monitor_name)
            if is_redundancy:
                self.pruning_monitor(monitor_name)
            else:
                redundant_monitors = self.search_redundant_monitors_for_new_monitor(monitor_name)
                for monitor in redundant_monitors:
                    redundant_resolution_structures = self.get_resolution_structure_for_new_monitor(monitor).keys()
                    resolution_structures_set = set(resolution_structures.keys())
                    for redundant_resolution_structure in redundant_resolution_structures:
                        if redundant_resolution_structure in resolution_structures_set:
                            del resolution_structures[redundant_resolution_structure]
                for monitor in redundant_monitors:
                    self.pruning_monitor(monitor)
                resolution_structures_for_new_monitor = self.get_resolution_structure_for_new_monitor(monitor_name)
                resolution_structures.update(resolution_structures_for_new_monitor)
        return resolution_structures

    def get_resolution_structures_expand_new(self, new_clause_places):
        resolution_structures = {}
        for monitor_name in new_clause_places:
            redundant_monitors = self.search_redundant_monitors_for_new_monitor(monitor_name)
            for monitor in redundant_monitors:
                self.pruning_monitor(monitor)
        self.update_k()
        for monitor_name in new_clause_places:
            resolution_structures_for_new_monitor = self.get_resolution_structure_for_new_monitor(monitor_name)
            resolution_structures.update(resolution_structures_for_new_monitor)
        return resolution_structures

    def resolution_in_pn(self):
        resolution_structures = self.get_resolution_structures_in_pn()
        self.resolution(resolution_structures)
        print(composed_num)
        return

    def resolution_expand(self, new_clause_places):
        resolution_structures = self.get_resolution_structures_expand(new_clause_places)
        self.resolution(resolution_structures)
        # print(composed_num)
        return

    def update_k(self):
        for transition in self.transitions.keys():
            self.k[transition] = len(self.get_one_transition(transition).get_pre_arcs())-1

    def resolution_expand_new(self, new_clause_places):
        resolution_structures = self.get_resolution_structures_expand_new(new_clause_places)
        self.resolution(resolution_structures)
        # print(composed_num)
        return

    def get_r_enabled_transitions(self):
        r_enabled_transitions = []
        enabled_transitions = self.get_enabled_transitions()
        for transition_name in enabled_transitions:
            if transition_name in self.transitions_certain:
                transition = self.get_one_transition(transition_name)
                if transition.get_dual_transition() not in enabled_transitions:
                    r_enabled_transitions.append(transition_name)
        return r_enabled_transitions

    def fire_r_enable_transitions(self):
        r_enabled_transitions = self.get_r_enabled_transitions()
        certain_reason = []
        for transition_name in r_enabled_transitions:
            self.transition_fired(transition_name)
            certain_reason.append(transition_name[2:])
        return certain_reason

    def execute_certain(self):
        r_enabled_transitions = self.get_r_enabled_transitions()
        # print(r_enabled_transitions)
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
                    # node_list.append(known_symbols_list.copy())
                    edge_list.append(transition_name)
                node_list.append(known_symbols_list.copy())
            r_enabled_transitions = self.get_r_enabled_transitions()
            # print(r_enabled_transitions)
        return node_list, edge_list

    def pruning_spn0(self, symbol_name):
        for place in self.get_one_spn(symbol_name).get_places().keys():
            self.del_place(place)
        for transition in self.get_one_spn(symbol_name).get_transitions().keys():
            self.del_transition(transition)
        del self.spn_set["spn0_set"][symbol_name]
        return

    def pruning_for_probability(self, target_var):
        # 删除0型符号Petri网
        spn0_list = list(self.spn_set["spn0_set"].keys())
        for spn0 in spn0_list:
            self.pruning_spn0(spn0)
        # 删除含概率的变量的确定变迁
        symbol_uncertain = list(self.spn_set["spn1_set"].keys()) + list(self.spn_set["spn2_set"].keys())
        symbol_uncertain_transitions_certain = []
        for symbol in symbol_uncertain:
            symbol_uncertain_transitions_certain.append("t_" + symbol)
            symbol_uncertain_transitions_certain.append("t_" + symbol + "_")
        for transition in symbol_uncertain_transitions_certain:
            self.del_transition(transition)
        # 删除永远不使能的变迁
        for transition in list(self.transitions.keys()):
            if transition not in self.get_enabled_transitions():
                pre_places = list(self.get_one_transition(transition).get_pre_arcs().keys())
                for pre_place in pre_places:
                    if pre_place[0] == "~" and self.get_one_place(pre_place).get_token_num() == 0:
                        self.del_transition(transition)
        # 删除没起约束的监控库所，通过托肯与约束符号判断
        for place in list(self.monitor_set.keys()):
            post_transitions = self.get_one_place(place).get_post_arcs().keys()
            transition2symbols = []
            for post_transition in post_transitions:
                # 是否为确定变迁，若是，则属于0型符号Petri网
                if hasattr(self.get_one_transition(post_transition), "dual_transition"):
                    for symbol, spn0 in self.spn_set["spn0_set"].items():
                        if post_transition in spn0.transitions.keys():
                            transition2symbols.append(symbol)
                            break
                # 判断是否为1型符号Petri网中的变迁
                elif post_transition[2] == "|":
                    for symbol, spn1 in self.spn_set["spn1_set"].items():
                        if post_transition in spn1.transitions.keys():
                            transition2symbols.append(symbol)
                            break
                # 为2型符号Petri网中的变迁
                else:
                    for symbol, spn2 in self.spn_set["spn2_set"].items():
                        if post_transition in spn2.transitions.keys():
                            transition2symbols.append(symbol)
                            break
            constraint_symbols = list(set(transition2symbols))
            if len(constraint_symbols) <= self.get_one_place(place).get_token_num():
                self.del_place(place)
                del self.monitor_set[place]
        # 删除没起约束的监控库所，通过监控库所与监控库所判断
        monitor_list = list(self.monitor_set.keys())
        for monitor_id in range(len(monitor_list)):
            monitor_post_transitions = self.get_one_place(monitor_list[monitor_id]).get_post_arcs().keys()
            for other_monitor_id in range(monitor_id + 1, len(monitor_list)):
                if set(self.get_one_place(monitor_list[other_monitor_id]).get_post_arcs().keys()).issubset(
                        set(monitor_post_transitions)):
                    monitor_constraint_symbols = list(
                        set([self.generalized_literal2symbol[x[2:]] for x in monitor_post_transitions]))
                    other_monitor_constraint_symbols = list(
                        set([self.generalized_literal2symbol[x[2:]] for x in
                             self.get_one_place(monitor_list[other_monitor_id]).get_post_arcs().keys()]))
                    if self.get_one_place(monitor_list[monitor_id]).get_token_num() - self.get_one_place(
                            monitor_list[other_monitor_id]).get_token_num() \
                            == len(monitor_constraint_symbols) - len(other_monitor_constraint_symbols):
                        self.del_place(monitor_list[monitor_id])
                        del self.monitor_set[monitor_list[monitor_id]]
                        break
                elif set(monitor_post_transitions).issubset(
                        set(self.get_one_place(monitor_list[other_monitor_id]).get_post_arcs().keys())):
                    monitor_constraint_symbols = list(
                        set([self.generalized_literal2symbol[x[2:]] for x in monitor_post_transitions]))
                    other_monitor_constraint_symbols = list(
                        set([self.generalized_literal2symbol[x[2:]] for x in
                             self.get_one_place(monitor_list[other_monitor_id]).get_post_arcs().keys()]))
                    if self.get_one_place(monitor_list[other_monitor_id]).get_token_num() - self.get_one_place(
                            monitor_list[monitor_id]).get_token_num() \
                            == len(other_monitor_constraint_symbols) - len(monitor_constraint_symbols):
                        self.del_place(monitor_list[monitor_id])
                        del self.monitor_set[monitor_list[monitor_id]]
                        break
        # 找与目标变量关联的库所集
        target_places = []
        for place in self.places.keys():
            if target_var in place and place[0] != "*":
                target_places.append(place)
        # open表储存待扩展库所
        open_places = target_places
        # close表储存已扩展库所
        close_places = []
        while open_places:
            place = open_places[0]
            # 在变迁的后置库所中删除条件库所
            for pre_transition in self.get_one_place(place).get_pre_arcs().keys():
                pre_places = list(self.get_one_transition(pre_transition).get_pre_arcs().keys())
                post_places = list(self.get_one_transition(pre_transition).get_post_arcs().keys())
                post_places_del_condition_places = list(filter(lambda x: x[0] != "*", post_places))
                extend_place = list(set(pre_places + post_places_del_condition_places) - set(close_places))
                open_places = list(set(open_places + extend_place))
            for post_transition in self.get_one_place(place).get_post_arcs().keys():
                pre_places = list(self.get_one_transition(post_transition).get_pre_arcs().keys())
                post_places = list(self.get_one_transition(post_transition).get_post_arcs().keys())
                post_places_del_condition_places = list(filter(lambda x: x[0] != "*", post_places))
                extend_place = list(set(pre_places + post_places_del_condition_places) - set(close_places))
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
            if self.get_one_transition(transition).get_post_arcs() == {} and self.get_one_transition(
                    transition).get_pre_arcs() == {}:
                self.del_transition(transition)
        return

    def get_reachable_graph(self):
        self.update_transitions()
        m0 = self.get_mark()
        # 定义一个列表来存储节点信息，每一个节点包括标识、是否为新节点、达到该标识所激发的变迁集、变迁对应父节点集、是否为叶节点、到达叶子节点的概率
        reachable_graph = [[None, None, [], [], None, int]]
        reachable_graph[0] = [m0, True, [], [], True, 0]
        # node_num = 1
        # print(node_num)
        # i = 1
        # print(i)
        new_node = [None, None, None, None, None, None]  # 表示节点
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
                        # 仅激发使能的概率变迁
                        if enabled_transition in self.transitions_uncertain:
                            self.transition_fired(enabled_transition)
                            r_enabled_transitions = self.get_r_enabled_transitions()
                            # 将当前标识下推理使能的确定变迁都激发，直至无推理使能的确定变迁
                            while len(r_enabled_transitions) > 0:
                                for r_enabled_transition in r_enabled_transitions:
                                    self.transition_fired(r_enabled_transition)
                                r_enabled_transitions = self.get_r_enabled_transitions()
                        mark = self.get_mark()
                        is_new = True  # 用于判断是否为新标识
                        for k in range(len(reachable_graph)):  # 与可达图中已有节点进行比较
                            if mark == reachable_graph[k][0]:
                                reachable_graph[k][2].append(enabled_transition)
                                reachable_graph[k][3].append(node_idx)
                                is_new = False
                                break
                        if is_new:
                            # i = i + 1
                            # print(i)
                            new_node[0] = mark
                            new_node[1] = True
                            new_node[2] = [enabled_transition]
                            new_node[3] = [node_idx]
                            new_node[4] = True
                            new_node[5] = 0
                            reachable_graph.append(new_node.copy())
                        self.set_places_token(reachable_graph[node_idx][0])
                        # node_num += 1
            have_new = False  # 用于判断可达图中是否存在new标识
            for node_index in range(len(reachable_graph)):
                if reachable_graph[node_index][1]:
                    have_new = True
                    break
        # print(node_num)
        all_probability = 0
        leaf_nodes = {}
        # leaf_node_num = 0
        for node_idx in range(len(reachable_graph)):
            if reachable_graph[node_idx][4]:
                reachable_graph[node_idx][5] = 1
                self.set_places_token(reachable_graph[node_idx][0])
                for place_name in self.places.keys():
                    if self.get_one_place(place_name).get_token_num() == 1 and hasattr(self.get_one_place(place_name),
                                                                                       "probability"):
                        reachable_graph[node_idx][5] = reachable_graph[node_idx][5] * self.get_one_place(place_name). \
                            get_probability()
                all_probability = all_probability + reachable_graph[node_idx][5]
                leaf_node_mark = str(reachable_graph[node_idx][0])
                leaf_nodes.update({leaf_node_mark: reachable_graph[node_idx][5]})
                # leaf_node_num += 1
        self.set_places_token(m0)
        # print(leaf_node_num)
        # 运行整个例子时，输出改为 all_probability
        # return all_probability
        return all_probability, leaf_nodes


# if __name__ == "__main__":
def all_resolution():
    global composed_num
    global composed_num_without_tautological
    global resolution_structures_num
    print("Computation of the full KPN for an original KB ...")
        # print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
        #       format(str(percepts_print), composed_num, resolution_structures_num,
        #              int(KPNs_in_world.monitor_num - last_monitors_record_num),
        #              resolution_structures_num +3 + last_monitors_num - len(KPNs_in_world.monitor_set),
        #              len(KPNs_in_world.monitor_set), max(KPNs_in_world.k.values()), current_time - last_time))
    KPNs_in_world = KPNs(get_symbol_info(), get_semantic_constraint())
    start = time.process_time()
    resolution_structures = KPNs_in_world.get_resolution_structures_in_pn()
    KPNs_in_world.resolution(resolution_structures)
    current_time = time.process_time()
    print_0 = ["non", composed_num, resolution_structures_num,
                 int(KPNs_in_world.monitor_num - 2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)-2*row*column),
                 int(2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)+2*row*column+resolution_structures_num - len(KPNs_in_world.monitor_set)),
                 len(KPNs_in_world.monitor_set), max(KPNs_in_world.k.values()), current_time - start]
    print_info.append(print_0)
    # print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
    #       format("Percepts", "N(resolu pairs)", "N(ctrl p)","N(new sem-p)",
    #              "N(ls sem-p)", "N(sem-p in FKPNs)","k","Time(s)"))
    # print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
    #       format("non", composed_num, resolution_structures_num,
    #              int(KPNs_in_world.monitor_num - 2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)-2*row*column),
    #              int(2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)+2*row*column+resolution_structures_num - len(KPNs_in_world.monitor_set)),
    #              len(KPNs_in_world.monitor_set), max(KPNs_in_world.k.values()), current_time - start))
    # a = current_time - start
    # print("Cost time for Resolution in KPN: %f" % (current_time - start))
    # print("The number of semantic places in full KPN: %d" % len(KPNs_in_world.monitor_set))
    # print("The number of redundant semantic places: %d" % int(2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)+2*row*column
    #                                                        + resolution_structures_num - len(KPNs_in_world.monitor_set)))
    # print("The number of resolution: %d" % resolution_structures_num)
    # print("The number of composes: %d" % composed_num)
    # print("The number of composes without tautological: %d" % composed_num_without_tautological)
    # print("The number of control places without less-strict at first: %d" %
    #       int(KPNs_in_world.monitor_num - 2*(4*3+(2*row+2*column-8)*4+(row-2)*(column-2)*5)-2*row*column))
    # # print(KPNs_in_world.k)
    # print("k: %d" % max(KPNs_in_world.k.values()))
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    last_time = current_time
    percepts_33_1 = ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2_', 't_!g2', 't_s4_', 't_b4', 't_!g4', 't_s5', 't_b5',
                     't_!g5', 't_s6', 't_b6_', 't_!g6', 't_s8_', 't_b8', 't_!g8', 't_s9', 't_b9', 't_!g9_']
    percepts_66_1= ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2', 't_!g2', 't_s3_', 't_b3', 't_!g3', 't_s8', 't_b8',
                    't_!g8', 't_s14', 't_b14', 't_!g14', 't_s20_', 't_b20', 't_!g20', 't_s15', 't_b15', 't_!g15',
                    't_s16', 't_b16', 't_!g16', 't_s17', 't_b17_', 't_!g17', 't_s22', 't_b22', 't_!g22',
                    't_s28', 't_b28', 't_!g28', 't_s34', 't_b34', 't_!g34', 't_s35', 't_b35', 't_!g35_']
    percepts_1010_4 = ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2', 't_!g2', 't_s3', 't_b3', 't_!g3', 't_s4_', 't_b4',
                       't_!g4', 't_s13', 't_b13', 't_!g13', 't_s23', 't_b23', 't_!g23', 't_s33', 't_b33', 't_!g33',
                       't_s43', 't_b43', 't_!g43', 't_s53_', 't_b53', 't_!g53', 't_s44', 't_b44', 't_!g44',
                       't_s45', 't_b45', 't_!g45', 't_s46', 't_b46', 't_!g46', 't_s47', 't_b47_', 't_!g47',
                       't_s56', 't_b56', 't_!g56_']
    # percepts_55_1 = ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2_', 't_!g2', 't_s6', 't_b6', 't_!g6', 't_s7', 't_b7',
    #                  't_!g7', 't_s8', 't_b8_', 't_!g8', 't_s11', 't_b11', 't_!g11', 't_s12', 't_b12','t_!g12', 't_s13',
    #                  't_b13_', 't_!g13', 't_s16_', 't_b16', 't_!g16', 't_s17', 't_b17', 't_!g17', 't_s18', 't_b18',
    #                  't_!g18_']
    # percepts_55_2 = ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2_', 't_!g2', 't_s6', 't_b6', 't_!g6', 't_s7', 't_b7',
    #                  't_!g7', 't_s8', 't_b8_', 't_!g8', 't_s11', 't_b11', 't_!g11', 't_s12', 't_b12', 't_!g12',
    #                  't_s13', 't_b13_', 't_!g13', 't_s16_', 't_b16', 't_!g16', 't_s17', 't_b17', 't_!g17', 't_s18',
    #                  't_b18', 't_!g18', 't_s19', 't_b19_', 't_!g19', 't_s22_', 't_b22', 't_!g22', 't_s23', 't_b23',
    #                  't_!g23_']
    # percepts_55_3 = ['t_s1', 't_b1', 't_!g1', 't_s2', 't_b2_', 't_!g2', 't_s6', 't_b6', 't_!g6', 't_s7', 't_b7',
    #                  't_!g7', 't_s8', 't_b8_', 't_!g8', 't_s11', 't_b11', 't_!g11', 't_s12', 't_b12', 't_!g12',
    #                  't_s13', 't_b13_', 't_!g13', 't_s16_', 't_b16', 't_!g16', 't_s17', 't_b17', 't_!g17', 't_s18',
    #                  't_b18', 't_!g18', 't_s19', 't_b19_', 't_!g19', 't_s22_', 't_b22', 't_!g22', 't_s23', 't_b23',
    #                  't_!g23', 't_s24', 't_b24', 't_!g24', 't_s25', 't_b25', 't_!g25_']
    # percepts_1010_1 = ['t_s1', 't_s2', 't_s11', 't_s12', 't_s13', 't_s21', 't_s22', 't_s23', 't_s31_', 't_s32',
    #                    't_s33', 't_s34', 't_s42_', 't_s43', 't_s44', 't_s45_', 't_s35', 't_s25', 't_s36_', 't_s26',
    #                    't_b1', 't_b2_', 't_b11', 't_b12', 't_b13_', 't_b21', 't_b22', 't_b23_', 't_b31', 't_b32',
    #                    't_b33', 't_b34_', 't_b42', 't_b43', 't_b44', 't_b45', 't_b35', 't_b25_', 't_b36', 't_b26',
    #                    't_!g1', 't_!g2', 't_!g11', 't_!g12', 't_!g13', 't_!g21', 't_!g22', 't_!g23', 't_!g31',
    #                    't_!g32', 't_!g33', 't_!g34', 't_!g42', 't_!g43', 't_!g44', 't_!g45', 't_!g35', 't_!g25',
    #                    't_!g36', 't_!g26_']
    # percepts_1010_2 = ['t_s1', 't_s2', 't_s11', 't_s12', 't_s13', 't_s21', 't_s22', 't_s23', 't_s31_', 't_s32',
    #                    't_s33', 't_s34', 't_s42_', 't_s43', 't_s53', 't_s54', 't_s55', 't_s65', 't_s66', 't_s67',
    #                    't_b1', 't_b2_', 't_b11', 't_b12', 't_b13_', 't_b21', 't_b22', 't_b23_', 't_b31', 't_b32',
    #                    't_b33', 't_b34_', 't_b42', 't_b43', 't_b53','t_b54', 't_b55', 't_b65', 't_b66', 't_b67',
    #                    't_!g1', 't_!g2', 't_!g11', 't_!g12', 't_!g13', 't_!g21', 't_!g22', 't_!g23', 't_!g31',
    #                    't_!g32', 't_!g33', 't_!g34', 't_!g42', 't_!g43', 't_!g53', 't_!g54', 't_!g55', 't_!g65',
    #                    't_!g66', 't_!g67_']
    # percepts_1010_3 = ['t_s1', 't_s2', 't_s11', 't_s12', 't_s13', 't_s21', 't_s22', 't_s23', 't_s31_', 't_s32',
    #                    't_s33', 't_s34', 't_s42_', 't_s43', 't_s53', 't_s54', 't_s55','t_s65','t_s66', 't_s67',
    #                    't_s68', 't_s77', 't_s78', 't_s79', 't_s89', 't_s99',
    #                    't_b1', 't_b2_', 't_b11', 't_b12', 't_b13_', 't_b21', 't_b22', 't_b23_', 't_b31', 't_b32',
    #                    't_b33', 't_b34_', 't_b42','t_b43', 't_b53', 't_b54', 't_b55', 't_b65', 't_b66', 't_b67',
    #                    't_b68_', 't_b77', 't_b78', 't_b79', 't_b89', 't_b99',
    #                    't_!g1', 't_!g2', 't_!g11', 't_!g12', 't_!g13', 't_!g21', 't_!g22', 't_!g23', 't_!g31', 't_!g32',
    #                    't_!g33', 't_!g34', 't_!g42', 't_!g43', 't_!g53', 't_!g54', 't_!g55', 't_!g65', 't_!g66', 't_!g67',
    #                    't_!g68', 't_!g77', 't_!g78', 't_!g79', 't_!g89', 't_!g99_']
    # for percept in percepts_33_1:
    # for percept in percepts_55_1:
    # for percept in percepts_55_2:
    # for percept in percepts_55_3:
    # for percept in percepts_1010_1:
    percepts = percepts_1010_4
    percepts_output = percepts_output_1010
    for idx in range(int(len(percepts)/3)):
        last_monitors_num = len(KPNs_in_world.monitor_set)
        last_monitors_record_num = KPNs_in_world.monitor_num
        composed_num = 0
        composed_num_without_tautological = 0
        resolution_structures_num = 0
        new_clause_places = []
        percepts_print_list = []
        percept_idx = 3 * idx
        for percept in percepts[3*idx:3*(idx+1):1]:
            KPNs_in_world.monitor_num += 1
            post_arcs = {percept: 1}
            rule_name = "r" + str(KPNs_in_world.monitor_num)
            new_clause_places.append(rule_name)
            constraint_symbols = {KPNs_in_world.generalized_literal2symbol[percept[2:]]: percept[2:]}
            KPNs_in_world.transitions[percept].add_pre_arc(rule_name, 1)
            KPNs_in_world.monitor_set.update({rule_name: C_Place(name=rule_name, token_num=0, post_arcs=post_arcs,
                                                        constraint_symbols=constraint_symbols)})
            KPNs_in_world.places.update({rule_name: KPNs_in_world.monitor_set[rule_name]})
            percepts_print_list.append(percepts_output[percept_idx])
            percept_idx += 1
            # print(percept)
        percepts_print = str(percepts_print_list).replace("'", "").replace("[", "").replace("]", "")
        KPNs_in_world.resolution_expand_new(new_clause_places)
        current_time = time.process_time()
        print_list = [str(percepts_print), composed_num, resolution_structures_num,
                     int(KPNs_in_world.monitor_num - last_monitors_record_num),
                     resolution_structures_num +3 + last_monitors_num - len(KPNs_in_world.monitor_set),
                     len(KPNs_in_world.monitor_set), max(KPNs_in_world.k.values()), current_time - last_time]
        print_info.append(print_list)
        # print("|{:^17}|{:^15}|{:^12}|{:^12}|{:^12}|{:^17}|{:^10}|{:^11}|".
        #       format(str(percepts_print), composed_num, resolution_structures_num,
        #              int(KPNs_in_world.monitor_num - last_monitors_record_num),
        #              resolution_structures_num +3 + last_monitors_num - len(KPNs_in_world.monitor_set),
        #              len(KPNs_in_world.monitor_set), max(KPNs_in_world.k.values()), current_time - last_time))
        # print("Cost time for %d-th percept: %f" % (idx+1, (current_time - last_time)))
        # print("The number of semantic places in full KPN: %d" % len(KPNs_in_world.monitor_set))
        # print("The number of redundant semantic places: %d" % (resolution_structures_num +3 + last_monitors_num - len(KPNs_in_world.monitor_set)))
        # print("The number of resolution: %d" % resolution_structures_num)
        # print("The number of composes: %d" % composed_num)
        # print("The number of composes without tautological: %d" % composed_num_without_tautological)
        # print("The number of control places without less-strict at first: %d" %
        #       int(KPNs_in_world.monitor_num - last_monitors_record_num - 3))
        # # print(KPNs_in_world.k)
        # print("k: %d" % max(KPNs_in_world.k.values()))
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        last_time = current_time
    # for percept in percepts_1010_3:
    #     KPNs_in_world.monitor_num += 1
    #     post_arcs = {percept: 1}
    #     rule_name = "r" + str(KPNs_in_world.monitor_num)
    #     constraint_symbols = {KPNs_in_world.generalized_literal2symbol[percept[2:]]: percept[2:]}
    #     KPNs_in_world.transitions[percept].add_pre_arc(rule_name, 1)
    #     KPNs_in_world.monitor_set.update({rule_name: C_Place(name=rule_name, token_num=0, post_arcs=post_arcs,
    #                                                 constraint_symbols=constraint_symbols)})
    #     KPNs_in_world.places.update({rule_name: KPNs_in_world.monitor_set[rule_name]})
        # redundant_monitors = KPNs_in_world.search_redundant_monitors_for_new_monitor(rule_name)
        # 在搜索解析对前已经去冗余了
        # for monitor in redundant_monitors:
        #     KPNs_in_world.pruning_monitor(monitor)
    # resolution_structures = KPNs_in_world.get_resolution_structures_in_pn()
    # KPNs_in_world.resolution(resolution_structures)
    # print(KPNs_in_world.monitor_num)
    # print(len(KPNs_in_world.monitor_set))
    # print(KPNs_in_world.monitor_set)
    # KPNs_in_world.pruning_for_probability("w7")
    end = time.process_time()
    # print(end - start)
    # print("over!")

if __name__ == "__main__":
    all_resolution()
    print(print_info)