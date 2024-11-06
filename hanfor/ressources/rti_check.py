from __future__ import annotations

from lib_pea.countertrace import Countertrace

import csv
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple
import logging

from pysmt.fnode import FNode
from pysmt.rewritings import conjunctive_partition
from pysmt.shortcuts import And, Equals, Symbol, Real, EqualsOrIff, get_model, is_sat, FALSE, get_unsat_core, Not, Solver, Or, is_valid, Implies, TRUE
from pysmt.typing import REAL

from z3 import Then, Tactic, With, Goal, Int, Bool
from lib_pea.config import SOLVER_NAME, LOGIC
from lib_pea.countertrace_to_pea import complete
from lib_pea.location import PhaseSetsLocation
from lib_pea.pea import PhaseSetsPea
from lib_pea.transition import PhaseSetsTransition
from req_simulator.scenario import Scenario
from req_simulator.utils import num_zeros
from reqtransformer import Requirement, Formalization




class RTIcheck:

    def __init__(self, ids, requirements, app) -> None:
        self.name: str = 'test'
        self.req_ids = ids
        self.requirements = requirements
        self.get_attributes(self.requirements)
        self.variables_dict = None
        self.chain_reqs_list = []
        self.rtis = []
        self.depth = 2

        self.get_variables_dict()
        self.get_chain_req_list()
        self.get_rtis()


    def exit_condition(self, requirement):
        # Generate and return the DNF of the exit condition
        return self.simplify(Not(requirement.countertrace.dc_phases[-2].invariant))
    def simplify (self, f: FNode) -> FNode:
        solver_z3 = Solver(name="z3")
        tactic3 = Then(With(Tactic("simplify"), elim_and=True), Tactic("propagate-values"))
        tactic2 = Then(Tactic('nnf'), Tactic('simplify'))
        ruru = tactic3(solver_z3.converter.convert(f)).as_expr()
        t2 =  Tactic("propagate-values")
        result = solver_z3.converter.back(ruru)
        result2 = tactic2(solver_z3.converter.convert(result)).as_expr()
        res = solver_z3.converter.back(result2)

        result = t2(solver_z3.converter.convert(result)).as_expr()
        result = solver_z3.converter.back(result)
        return res
    def get_attributes(self, requirements):
        requirements_rti = []

        for req in self.requirements:
            req.exit_options = []
            is_chain_req = False
            exit_objects = []
            exit_condition = self.exit_condition(req)
            req.exit_condition = exit_condition

            if exit_condition.is_or():
                req.chain_req = True  # chain req if exit-Condition has a or (||) in it
                exit_conditions_chain = self.get_or_list(exit_condition, [])
                for formulas in exit_conditions_chain:
                    req.exit_options.append(
                        self.ExitOptions(formulas, self.get_variables_from_exit_condtions(formulas, [])))
            else:
                req.exit_options = [self.ExitOptions(exit_condition, self.get_variables_from_exit_condtions(exit_condition, []))]

            is_start_req = False
            #if len(pea.clocks) > 0:
            #    is_start_req = True  # start req -> is timed, one of them is needed for an rti


        for req in self.requirements:
            for exit in req.exit_options:
                if len(exit.exit_variables) == 0:
                    req.exit_options.remove(exit)
            if len(req.exit_options) == 0:
                self.requirements.remove(req)

    def get_variables_dict(self):
        self.variables_dict = {}
        for req in self.requirements:
            if not req.chain_req:
                for variable1 in req.exit_options[0].exit_variables:
                    variable = variable1[0]
                    print(req.exit_options[0].exit_variables[0])
                    if variable._content.payload[1].name is "Bool":
                        if ("! " + str(variable)) in str(req.exit_options[0].exit_condition):
                            if not variable in self.variables_dict.keys():
                                self.variables_dict[variable] = {"variable": variable, "type_variable": "Bool",
                                                       "peas_positive": [],
                                                       "peas_negative": [req]}

                            else:
                                self.variables_dict[variable]["peas_negative"].append(req)
                        else:
                            if not variable in  self.variables_dict.keys():
                                self.variables_dict[variable] = {"variable": variable, "type_variable": "Bool",
                                                       "peas_positive": [req], "peas_negative": []}

                            else:
                                self.variables_dict[variable]["peas_positive"].append(req)


                    else:
                        if not variable in  self.variables_dict.keys():
                            self.variables_dict[variable] = {"variable": variable, "type_variable": "Int", "peas": [req]}

                        else:
                            self.variables_dict[variable]["peas"].append(req)


    def get_or_list(self, formula, helplist):
        for var in formula.args():
            helplist.append(var)

        return helplist
    def get_variables_from_exit_condtions(self, formula, listi):
        if formula.is_and():
            for arg in formula.args():
                self.get_variables_from_exit_condtions(arg, listi)
        else:
            variables = formula.get_free_variables()
            helplist = []
            for var in variables:
                if ("!" + str(var)) in variables and var._content.payload[1].name is "Bool":
                    helplist.append(Not(var))
                else:
                    helplist.append(var)
                listi.append(helplist)

        return listi

    def get_chain_req_list(self):
        self.chain_reqs_list = [req for req in self.requirements if req.chain_req]

        self.chain_reqs_list.sort(key=lambda x: len(x.exit_options), reverse=True)



    class RtiSet:
        def __init__(self, countertrace: Countertrace = None):
            super().__init__()

            self.countertrace: Countertrace = countertrace
            self.requirement = None
            self.formalization = None
            self.countertrace_id: int = None
            self.exit_conditions = None
            self.exit_options = None
            self.chain_req = False
            self.start_req = True

    class ExitOptions:
        def __init__(self, exit_condition: FNode,
                     exit_variables: list):
            self.exit_condition = exit_condition
            self.exit_variables = exit_variables

    def get_pair_rtis(self):
        # first serach for rtis with 2 reqs without chain reqs
        for variable in self.variables_dict:
            if self.variables_dict[variable]["type_variable"] is "Bool":
                for positive in self.variables_dict[variable]["peas_positive"]:
                    for negative in self.variables_dict[variable]["peas_negative"]:
                        if self.rti_check([positive, negative]):
                            self.rtis.append([positive, negative])
            else:
                for pea1 in self.variables_dict[variable]["peas"]:
                    for pea2 in self.variables_dict[variable]["peas"]:
                        if self.rti_check([pea1, pea2]):
                            self.rtis.append([pea1, pea2])

    def rti_check(self, requirements):
        # check if set of reqs can cause an rti
        starter_in_set = False
        # one of the reqs has to be starter req (time bound)
        for req in requirements:
            if req.start_req:
                starter_in_set = True
                break
        if not starter_in_set:
            return False
        # formmula has to be not sat
        if is_sat(self.rebuild_formula(requirements)):
            return False

        return True

    def rebuild_formula(self, list_requirements):
        """Rebuild the formula dynamically from the remaining requirements"""
        if not list_requirements:
            return TRUE  # or an appropriate base formula
        formula = self.exit_condition(list_requirements[0])
        for k in range(1, len(list_requirements)):
            formula = And(self.exit_condition(list_requirements[k]), formula)
        return self.simplify(formula)

    def chain_check(self, chain_req, other_chain_reqs, depth, possible_rti):
        #if the number of chainreqs == depth of check -> check if they are a rti by themself
        if len(possible_rti) == depth:
            if self.rti_check(possible_rti):
                self.rtis.append(possible_rti)
            else:
                #try to fill with singles
                self.fill_chain_with_singles(chain_req, other_chain_reqs, depth, possible_rti)
        elif len(possible_rti) < depth:
            #add another matching chainreq to check
            for other_req in other_chain_reqs:
                if other_req not in possible_rti:
                    formula_already = self.rebuild_formula(possible_rti)
                    formula_check_new_req = Implies(self.simplify(formula_already), self.exit_condition(other_req.pea))
                    variables_old = formula_already.get_free_variables()
                    variables_new_req = other_req.exit_condition.get_free_variables()
                    if len(set(variables_old).intersection(set(variables_new_req))) > 0:
                        if not is_valid(formula_check_new_req):
                            new_list = possible_rti + [other_req]
                            # Recursive call to check further requirements
                            logging.debug("Adding worked" + str(formula_check_new_req))
                            self.chain_check(chain_req, other_chain_reqs, depth, new_list.copy())

    def fill_chain_with_singles(self, chain_req, other_chain_reqs, depth, possible_rti):
        # list with chain reqs, fill with singles(no chain reqs) for rti
        selected_lists = []

        for sub_form in chain_req.exit_options:
            helper = []
            for var_list in sub_form.exit_variables:
                for variable in var_list:
                    variableList = []
                    if not variable in self.variables_dict:
                        return
                    if self.variables_dict[variable]["type_variable"] == "Bool":
                        if "! " + str(variable) not in str(sub_form.exit_condition):
                            variableList.append(self.variables_dict[variable]["peas_negative"])
                        else:
                            variableList.append(self.variables_dict[variable]["peas_positive"])
                    else:
                        variableList.append(self.variables_dict[variable]["peas"])
                    if len(variableList) > 1:
                        print("todo")
                    else:
                        for pea in variableList[0]:
                            if not is_sat(And(sub_form.exit_condition, pea.exit_options[0].exit_condition)):
                                helper.append(pea)
            selected_lists.append(helper)

        combinations = list(itertools.product(*selected_lists))
        for combo in combinations:
            list_from_combo = possible_rti + list(combo)
            self.rtis.append(list_from_combo)
        #     list_from_combo = possible_rti + list(combo)
        #     if(self.rti_check(list_from_combo)):
        #         rtis.append(list_from_combo)


    def last_red_phase(self):
        i = 0
        while i < len(self.rtis):
            test = []
            for req in self.rtis[i]:
                if type(req.countertrace.dc_phases[-2].bound) is not int:
                    test.append(req.countertrace.dc_phases[-2].invariant)
                else:
                    test.append(req.countertrace.dc_phases[-3].invariant)
            formula = test[0]
            for p in range(1, len(test)):
                formula = And(formula, test[p])
            if not is_sat(formula):
                self.rtis.pop(i)
            else:
                i +=1
        i = 0
        while i < len(self.rtis):
            problem = False

            if len(self.rtis[i]) == 2:
                req1 = self.rtis[i][0]
                req2 = self.rtis[i][1]
                huh = And(req1.countertrace.dc_phases[-3].invariant, req2.countertrace.dc_phases[-3].invariant)
                print(huh)
                help = self.simplify(And(req1.countertrace.dc_phases[-3].invariant, req2.countertrace.dc_phases[-3].invariant))
                print(help)
                if type(req1.countertrace.dc_phases[-2].bound) is not int and type(req2.countertrace.dc_phases[-2].bound) is not int:
                    if req1.countertrace.dc_phases[-2].bound == req2.countertrace.dc_phases[-2].bound:
                        if req1.countertrace.dc_phases[-2].bound_type == req2.countertrace.dc_phases[-2].bound_type:
                            if not is_sat(self.simplify(And(req1.countertrace.dc_phases[-3].invariant, req2.countertrace.dc_phases[-3].invariant))):
                                self.rtis.pop(i)
                                problem = True
            if not problem:
                i += 1



    def get_minimal_sets(self):
        # Iterate through rtis list from the last to the first
        rti1 = len(self.rtis) - 1
        while rti1 >= 0:
            rti2 = len(self.rtis) - 1
            while rti2 > rti1:
                csvCheck = True
                # Check if all elements of rtis[rti1] are present in rtis[rti2]
                for k in range(len(self.rtis[rti1])):
                    variabel_check = False
                    for l in range(len(self.rtis[rti2])):
                        # if rtis[rti1][k].requirement.pos_in_csv == rtis[rti2][l].requirement.pos_in_csv:
                        if self.rtis[rti1][k].countertrace == self.rtis[rti2][l].countertrace:
                            variabel_check = True
                            break  # If found, no need to continue inner loop
                    if not variabel_check:
                        csvCheck = False
                        break  # If one element is missing, break early
                # If csvCheck is true, remove the larger set (rti2)
                if csvCheck:
                    self.rtis.pop(rti2)
                rti2 -= 1
            rti1 -= 1

    def get_rtis(self):
        self.get_pair_rtis()
        print("huhu")

        for depth in range(1, self.depth):
            copy_chain_reqs = self.chain_reqs_list.copy()
            while len(copy_chain_reqs) > 0:
                self.chain_check(copy_chain_reqs[0], copy_chain_reqs, depth, [copy_chain_reqs[0]])
                copy_chain_reqs.pop(0)
        print("huhuhuhu")
        self.last_red_phase()
        self.get_minimal_sets()
        self.rti_csv_output()


    def rti_csv_output(self):
        with open('rtis.csv', 'w', encoding= 'utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Depth", "IDs", "Countertraces"])
            for rti in self.rtis:
                depth = len(rti)
                ids = [req.requirement.rid for req in rti]
                countertraces = [str(req.countertrace) for req in rti]
                writer.writerow([depth, "\n".join(ids), "\n".join(countertraces)])


