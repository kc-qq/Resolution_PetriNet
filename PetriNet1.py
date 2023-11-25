import numpy as np


class Place1:
    def __init__(self, name, token_num, pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if post_arcs is None:
            post_arcs = {}
        self.__name = name
        self.__token_num = token_num
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
            raise ValueError

    def add_pre_arc(self, pre_transition, weight):
        self.get_pre_arcs().update({pre_transition: weight})

    def add_post_arc(self, post_transition, weight):
        self.get_post_arcs().update({post_transition: weight})

    def get_name(self):
        return self.__name

    def get_token_num(self):
        return self.__token_num

    def get_pre_arcs(self):
        return self.__pre_arcs

    def get_post_arcs(self):
        return self.__post_arcs

    def get_info(self):
        return self.__name, self.__token_num, self.__pre_arcs, self.__post_arcs


class Transition1:
    def __init__(self, name, pre_arcs=None, post_arcs=None):
        if pre_arcs is None:
            pre_arcs = {}
        if post_arcs is None:
            post_arcs = {}
        self.__name = name
        self.__pre_arcs = pre_arcs
        self.__post_arcs = post_arcs

    def add_pre_arc(self, pre_place, weight):
        self.get_pre_arcs().update({pre_place: weight})

    def add_post_arc(self, post_place, weight):
        self.get_post_arcs().update({post_place: weight})

    def get_name(self):
        return self.__name

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
        return [self.__name, self.__pre_arcs, self.__post_arcs]


class PetriNet1:
    def __init__(self):
        self.places = {}
        self.transitions = {}

    def add_place(self, place_name, token_num, place_pre_arcs=None, place_post_arcs=None):
        if place_pre_arcs is None:
            place_pre_arcs = {}
        if place_post_arcs is None:
            place_post_arcs = {}
        self.places[place_name] = Place1(name=place_name, token_num=token_num,
                                          pre_arcs=place_pre_arcs, post_arcs=place_post_arcs)
        for pre_transition in place_pre_arcs.keys():
            self.get_one_transition(pre_transition).get_post_arcs().update({place_name: place_pre_arcs[pre_transition]})
        for post_transition in place_post_arcs.keys():
            self.get_one_transition(post_transition).get_pre_arcs().update(
                {place_name: place_post_arcs[post_transition]})
        return

    def add_transition(self, tran_name, tran_pre_arcs=None, tran_post_arcs=None):
        if tran_post_arcs is None:
            tran_post_arcs = {}
        if tran_pre_arcs is None:
            tran_pre_arcs = {}
        self.transitions[tran_name] = Transition1(name=tran_name, pre_arcs=tran_pre_arcs, post_arcs=tran_post_arcs)
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

    def del_place(self, place_name):
        for pre_transition in self.get_one_place(place_name).get_pre_arcs().keys():
            del self.get_one_transition(pre_transition).get_post_arcs()[place_name]
        for post_transition in self.get_one_place(place_name).get_post_arcs().keys():
            del self.get_one_transition(post_transition).get_pre_arcs()[place_name]
        del self.places[place_name]
        return

    def del_transition(self, tran_name):
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

    def judge_transition_enable(self,transition_name):
        transition = self.get_one_transition(transition_name)
        pre_arcs = transition.get_pre_arcs()
        pre_token = []
        pre_weight = []
        for pre_place, weight in pre_arcs.items():
            pre_token.append(self.get_one_place(pre_place).get_token_num())
            pre_weight.append(weight)
        enable_flag = False
        if (np.array(pre_token) >= np.array(pre_weight)).all():
            enable_flag = True
        return enable_flag

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

    def get_mark(self):
        mark = []
        place_dict = self.places
        for place_name in place_dict.keys():
            mark.append(self.get_one_place(place_name).get_token_num())
        return mark

    def set_places_token(self, mark=None):
        if mark is None:
            mark = []
        idx = 0
        for place_info in self.places.values():
            place_info.set_token(mark[idx])
            idx += 1
        return