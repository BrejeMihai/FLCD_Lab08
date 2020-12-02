from collections import defaultdict
from copy import deepcopy
from collections import deque

class Grammar(object):

    def __init__(self):
        self.terminals = []
        self.non_terminals = []
        self.productions = defaultdict(list)
        self.starting_symbol = ""

    def __str__(self):
        stringu = "The grammar is:\nSet of terminals= "
        for c in self.terminals:
            stringu += c + " "
        stringu += "\nSet of non terminals= "
        for c in self.non_terminals:
            stringu += c + " "
        stringu += "\nThe productions:\n"
        for non_term in self.productions:
            prods = self.productions[non_term]
            stringu += str(non_term) + "-> "
            for element in prods:
                stringu += str(element) + " | "
            if len(prods) != 0:
                stringu = stringu[:-3]
            stringu += "\n"
        return stringu

    def get_productions_for_nonterminal(self, non_terminal):
        try:
            x = self.productions[non_terminal]
            return x
        except:
            raise Exception("No such non terminal exists")


    def read_from_file(self,path):
        with open(path, "r") as f:
            startingSymbol = f.readline().strip("\n\r")
            self.starting_symbol = startingSymbol

            line = f.readline()
            for c in line.split(" "):
                self.non_terminals.append(c.strip("\n\r"))
            if self.starting_symbol not in self.non_terminals:
                raise Exception("No start symbol given! Bad grammar!")

            line = f.readline()
            for c in line.split(" "):
                self.terminals.append(c.strip("\n\r"))
            lines = f.readlines()
            for line in lines:
                non_term, prods = line.split(" ", 1)
                for prod in prods.split(" "):
                    if "@" in prod:
                        prod = prod.replace("@", " ")
                    prod = prod.rstrip()
                    prod = "\"" + prod + "\""
                    self.productions[non_term].append(prod)



class Lr0Parser(object):
    def __init__(self, grammar):
        self.grammar = grammar
        self.terminals = grammar.terminals
        self.non_terminals = grammar.non_terminals
        self.productions = grammar.productions
        self.starting_symbol = grammar.starting_symbol
        self.augmented_grammar = None
        self.dotted_productions = None
        self.indexable_productions()
        self.start_magic()
        with open("out.txt", "w") as f:
            f.write(str(self.grammar))
            f.write("\n")

    def start_magic(self):
        self.augment_grammar()
        self.initial_closure = {"S\'" : self.dotted_productions['S\'']}
        self.closure(self.dotted_productions['S\''][0], self.initial_closure, self.dotted_productions)

    def augment_grammar(self):
        self.dotted_productions = defaultdict(list)

        self.dotted_productions['S\''].append(". " + self.grammar.starting_symbol)  # augmented start

        for non_terminal in self.productions:
            self.dotted_productions[non_terminal] = []
            for production in self.productions[non_terminal]:
                self.dotted_productions[non_terminal] \
                    .append(". "
                            + production.replace('\"', ""))  # eliminating double quotations

    def indexable_productions(self):
        self.indexable_productions = []
        for x in self.productions:
            for productions in self.productions[x]:
                self.indexable_productions.append([x] + [lmbd.strip("\"") for lmbd in productions.split(" ")])

    def closure(self, element, closure_history, transition_history):
        #element = element[0]
        dot_index = element.index('.')
        if "." == element[-1]:
            return

        next_space = element.find(" ", dot_index+2)
        if next_space == -1:
            element_after_dot = element[dot_index + 2: ]
        else:
            element_after_dot = element[dot_index + 2: next_space]

        if element_after_dot in self.non_terminals:
            non_terminal = element_after_dot

            if non_terminal not in closure_history:
                closure_history[non_terminal] = transition_history[non_terminal]
            else:
                closure_history[non_terminal] += transition_history[non_terminal]
            for transition in transition_history[non_terminal]:
                #if non_terminal not in closure_history.keys():
                self.closure(transition, closure_history, transition_history)

    def shift_dot(self, transition_ref):
        transition = deepcopy(transition_ref)
        dot_index = transition.index(".")

        if transition[-1] == ".":
            raise Exception("No more shifting available!")

        transition_after_dot = transition[dot_index + 1 if transition[dot_index+1] != " " else dot_index+2 : ]
        transition_before_dot = transition[: dot_index]

        find_space_after_dot = transition_after_dot.find(" ")
        if -1 != find_space_after_dot:
            first_element_after_dot = transition_after_dot[:find_space_after_dot]
            rest_after_dot = transition_after_dot[find_space_after_dot+1:]
        else:
            first_element_after_dot = transition_after_dot
            rest_after_dot = ""

        shifted_transition = transition_before_dot + " " + first_element_after_dot + " . " + rest_after_dot

        return shifted_transition.strip(" \n\r")

    def goto(self, initial_transition, key, state, parent=-1):

        shifted_transition = self.shift_dot(state)
        closure_history = {key: [shifted_transition]}

        self.closure(shifted_transition, closure_history, initial_transition)

        # space_before_dot = shifted_transition.index('.')-1#shifted_transition.rfind(" ", 0, shifted_transition.index(".")-1)
        # if -1 != space_before_dot:
        #     before_dot = shifted_transition[:space_before_dot]
        # else:
        #     before_dot = shifted_transition[:shifted_transition.index(".")-1]
        # parent_transition = before_dot
        dot_index = shifted_transition.index(".")
        space_before_dot = shifted_transition.rfind(" ", 0, dot_index-1)
        if -1 != space_before_dot:
            element_before_dot = shifted_transition[space_before_dot+1:dot_index-1]
        else:
            element_before_dot = shifted_transition[:dot_index-1]
        parent_transition = element_before_dot

        self.queue.append({
            "state": closure_history,
            "initial_dotted": initial_transition,
            "parent": parent,
            "parent_transition": parent_transition
        })

    def check_for_collision(self, value, where, new_value):
        if value is not None:
            raise Exception("Collision occured in the parsing table at: {}. Tried inserting {} over {}".format(where, new_value, value))

    def goto_all(self, state, initial_dotted, parent=-1, parent_transition="-1"):
        if state not in self.states:
            self.states.append(state)
            index = len(self.states) - 1
            self.state_parents[index] = {
                "parent_index": parent,
                "before_dot": parent_transition
            }
            self.pretty_print_map(state, "state {}".format(index))
            for key in state:
                for transition in state[key]:
                    if transition[-1] != '.':
                        self.goto(initial_dotted, key, transition, index)
        else:
            if parent in self.inner_table_values:
                if parent_transition in self.non_terminals:  # if in goto part of table
                    try:
                        self.check_for_collision(self.inner_table_values[parent][parent_transition],
                                             [parent, parent_transition], "{}".format(self.states.index(state)))
                    except KeyError:
                        pass
                    self.inner_table_values[parent][parent_transition] = "{}".format(self.states.index(state))
                else:                                        # if in action part of table
                    try:
                        self.check_for_collision(self.inner_table_values[parent][parent_transition],
                                             [parent, parent_transition], "s{}".format(self.states.index(state)))
                    except KeyError:
                        pass
                    self.inner_table_values[parent][parent_transition] = "s{}".format(self.states.index(state))
            else:
                if parent_transition in self.non_terminals:  # if in goto part of table
                    self.inner_table_values[parent] = {parent_transition: "{}".format(self.states.index(state))}
                else:                                        # if in action part of table
                    self.inner_table_values[parent] = {parent_transition: "s{}".format(self.states.index(state))}

    def get_reduced(self):
        self.reduced = {}
        for state in self.states:
            state_key = list(state.keys())[0]
            if len(state) == 1 and len(state[state_key]) and len(state[state_key][0]) \
                    and state[state_key][0][-1] == ".":
                self.reduced[self.states.index(state)] = state
        return self.reduced

    def canonical_collection(self):
        self.inner_table_values = {}
        self.queue = [{
            "state": self.initial_closure,
            "initial_dotted": self.dotted_productions,
        }]
        self.states = []
        self.state_parents = {}
        while len(self.queue) > 0:
            self.goto_all(**self.queue.pop(0))
        reduced = self.get_reduced()
        for k in reduced:
            red_k = list(reduced[k].keys())
            if red_k[0] != "S'":
                trans = red_k + [lmbd for lmbd in reduced[k][red_k[0]][0][:-1].split(" ")]
                transClean = []
                for x in trans:
                    if x != '':
                        transClean.append(x)

                reduce_index = self.indexable_productions.index(transClean) + 1
#                reduce_index = self.productions[red_k[0]].index(trans) + 1
                self.inner_table_values[k] = { terminal: "r{}".format(reduce_index) for terminal in self.terminals}
                self.inner_table_values[k]["$"] = "r{}".format(reduce_index)
            else:
                self.inner_table_values[k] = {"$": "accept"}
        del self.state_parents[0]
        for key in self.state_parents:
            parent = self.state_parents[key]
            if parent["parent_index"] in self.inner_table_values:
                if parent["before_dot"] in self.non_terminals:
                    try:
                        self.check_for_collision(self.inner_table_values[parent["parent_index"]][parent["before_dot"]],
                                             [parent["parent_index", parent["before_dot"]]], "{}".format(key))
                    except KeyError:
                        pass
                    self.inner_table_values[parent["parent_index"]][parent["before_dot"]] = "{}".format(key)
                else:
                    try:
                        self.check_for_collision(self.inner_table_values[parent["parent_index"]][parent["before_dot"]],
                                             [parent["parent_index", parent["before_dot"]]], "s{}".format(key))
                    except KeyError:
                        pass
                    self.inner_table_values[parent["parent_index"]][parent["before_dot"]] = "s{}".format(key)
            else:
                if parent["before_dot"] in self.non_terminals:
                    self.inner_table_values[parent["parent_index"]] = {parent["before_dot"]: "{}".format(key)}
                else:
                    self.inner_table_values[parent["parent_index"]] = {parent["before_dot"]: "s{}".format(key)}

    def show_parsing_table(self):
        table = {"I{}".format(index): self.inner_table_values[index] for index in range(len(self.states))}
        with open("out.txt", "a") as file:
            self.print_and_write_to_file(self.pretty_print_map(table, "Parsing table:"), file)

    def print_and_write_to_file(self, string, file_handle):
        print(string)
        file_handle.write(string)
        file_handle.write("\n")

    def actual_parsing(self, word):

        if type(word) != list:
            raise Exception("Input sequence must be in list format")

        stack_alpha = deque()  # state stack
        stack_beta = deque()  # word stack
        stack_phi = deque()  # actions stack
        end = False

        class alpha_item(object):
            def __init__(self, value, number):
                self.value = value
                self.number = number
            def is_dummy(self):
                return self.value == -1
            def __str__(self):
                return "{}{}".format(self.number,self.value) if self.number!=-1 else "{}".format(self.value)

        stack_beta.append("$")
        for letter in reversed(word):
            stack_beta.append(letter)

        stack_alpha.append(alpha_item(0, -1))

        with open("out.txt", "a") as file:
            self.print_and_write_to_file("Parsing sequence: {}\n".format("".join([x for x in word])), file)
            self.print_and_write_to_file("Alpha | Beta | Phi", file)
            self.print_and_write_to_file("~"*20, file)
            while(end != True):
                self.print_and_write_to_file("{} | {} | {}".format("".join([str(x) for x in stack_alpha]),
                                        "".join([x for x in reversed(stack_beta)]),
                                        "-" if len(stack_phi)==0 else stack_phi[-1]),
                                             file)
                current_step = stack_beta[-1]
                current_state = stack_alpha[-1]

                if "s" in self.inner_table_values[current_state.value][current_step]:
                    current_step = stack_beta.pop()
                    corresponding_state = int(self.inner_table_values[current_state.value][current_step][1:])
                    stack_alpha.append(alpha_item(int(corresponding_state), current_step))
                    stack_phi.append("Shift {}".format(corresponding_state))

                elif "r" in self.inner_table_values[current_state.value][current_step]:
                    corresponding_production_index = int(self.inner_table_values[current_state.value][current_step][1:])-1
                    lhs = self.indexable_productions[corresponding_production_index][0]
                    rhs = self.indexable_productions[corresponding_production_index][1:]
                    for value in rhs:
                        top_of_stack = stack_alpha.pop().number
                        if top_of_stack not in rhs:
                            raise Exception("Reduce failed")
                        rhs = rhs[rhs.index(top_of_stack)+1:] + rhs[:rhs.index(top_of_stack)]

                    top_alpha = stack_alpha[-1]
                    stack_alpha.append(alpha_item(int(self.inner_table_values[top_alpha.value][lhs]), lhs))

                    stack_phi.append("Reduced by {}->{}".format(self.indexable_productions[corresponding_production_index][0],
                                                                "".join(self.indexable_productions[corresponding_production_index][1:])))

                else:
                    if 'accept' in self.inner_table_values[current_state.value][current_step]:
                        self.print_and_write_to_file("{} | {} | {}".format("".join([str(x) for x in stack_alpha]),
                                                    "".join([x for x in reversed(stack_beta)]),
                                                    "Accept"),
                                                     file)
                        self.print_and_write_to_file("Success", file)
                    else:
                        self.print_and_write_to_file("{} | {} | {}".format("".join([str(x) for x in stack_alpha]),
                                                    "".join([x for x in reversed(stack_beta)]),
                                                    "Error"),
                                                     file)
                        self.print_and_write_to_file("Error",
                                                     file)
                    end = True


    def pretty_print_map(self, map, message=None):
        the_string = ""
        if message:
            the_string += message + "\n"
        for key in map:
            the_string += "{} : {}".format(key, map[key]) + "\n"
        return the_string
