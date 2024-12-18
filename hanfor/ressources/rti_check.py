from __future__ import annotations

from itertools import combinations

from lib_pea.countertrace import Countertrace
import time
import csv
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple
import logging
from fractions import Fraction
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
    """
    A class to perform RTI (Requirement Traceability Information) checks.

    Attributes:
        name (str): The name of the RTI check instance.
        req_ids (list): List of requirement IDs.
        requirements (list): List of requirements.
        variables_dict (dict): Dictionary of variables.
        chain_reqs_list (list): List of chain requirements.
        rtis (list): List of RTIs.
        depth (int): Depth of the RTI check.
    """

    def __init__(self, ids, requirements, app, depth1) -> None:
        """
        Initializes the RTIcheck instance.

        Args:
            ids (list): List of requirement IDs.
            requirements (list): List of requirements.
            app: Application instance.
            depth1 (int): Depth of the RTI check.
        """
        self.name: str = 'test'
        self.req_ids = ids
        self.requirements = requirements
        self.variables_dict = {}
        self.chain_reqs_list = []
        self.rtis = []
        self.duration = 0

        self.get_depth_from_input(depth1)
        self.get_attributes()
        self.get_variables_dict()
        self.get_rtis()

    class RtiSet:
        """
        A class to represent a set of RTIs.

        Attributes:
            countertrace (Countertrace): The countertrace associated with the RTI set.
            requirement: The requirement associated with the RTI set.
            formalization: The formalization associated with the RTI set.
            countertrace_id (int): The ID of the countertrace.
            exit_conditions (list): List of exit conditions.
            exit_options (list): List of exit options.
            chain_req (bool): Indicates if it is a chain requirement.
            start_req (bool): Indicates if it is a start requirement.
            id: The ID of the RTI set.
        """
        def __init__(self, countertrace: Countertrace):
            super().__init__()

            self.countertrace = countertrace
            self.requirement = None
            self.formalization = None
            self.countertrace_id: int = None
            self.exit_conditions = []
            self.exit_options = []
            self.chain_req = False
            self.start_req = True
            self.id = None

    class ExitOptions:
        """
        A class to represent exit options.

        Attributes:
            exit_condition (FNode): The exit condition.
            exit_variables (list): List of exit variables.
            last_red_phase: The penultimate phase.
            exit_phase: The exit phase.
        """
        def __init__(self, exit_condition: FNode, exit_variables: list, penultimate, exit_phase):
            self.exit_condition = exit_condition
            self.exit_variables = exit_variables
            self.last_red_phase = penultimate
            self.exit_phase = exit_phase

    def get_attributes(self):
        """
        Retrieves and sets the attributes for each requirement.
        """
        for i in range(len(self.requirements)-1):
            if len(self.requirements[i].countertrace.dc_phases) < 3:
                self.requirements.remove(self.requirements[i])
                i = i-1
        for req in self.requirements:
            req.exit_conditions = self.exit_condition(req)
            req.exit_conditions = self.simplify(req.exit_conditions)
            exit_conditions_chain = self.get_or_list(req.exit_conditions, [])
            penultimate = req.countertrace.dc_phases[-2]
            req.id = req.id + "_" + str(req.countertrace_id)
            if req.countertrace.dc_phases[-2].bound is not None and len(req.countertrace.dc_phases) > 2:
                penultimate = req.countertrace.dc_phases[-3]
            for exit_condition in exit_conditions_chain:
                req.exit_options.append(self.ExitOptions(exit_condition, self.get_variables(exit_condition), penultimate, req.countertrace.dc_phases[-2]))
            if len(exit_conditions_chain) > 1:
                req.chain_req = True
                self.chain_reqs_list.append(req)






    def simplify(self, f: FNode) -> FNode:
        """
        Simplifies a given formula.

        Args:
            f (FNode): The formula to simplify.

        Returns:
            FNode: The simplified formula.
        """
        solver_z3 = Solver(name="z3")
        tactic3 = Then(With(Tactic("simplify"), elim_and=True), Tactic("propagate-values"))
        tactic2 = Then(Tactic('nnf'), Tactic('simplify'))
        ruru = tactic3(solver_z3.converter.convert(f)).as_expr()
        result = solver_z3.converter.back(ruru)
        result2 = tactic2(solver_z3.converter.convert(result)).as_expr()
        res = solver_z3.converter.back(result2)

        return res

    def get_or_list(self, formula, helplist) -> list:
        """
        Retrieves a list of OR conditions from a formula.

        Args:
            formula: The formula to process.
            helplist (list): The list to store OR conditions.

        Returns:
            list: The list of OR conditions.
        """
        if formula.is_or():
            for var in formula.args():
                helplist.append(var)
        else:
            helplist.append(formula)

        return helplist

    @staticmethod
    def get_variables(exit_condition)-> list:
        """
        Retrieves the variables from an exit condition.

        Args:
            exit_condition: The exit condition to process.

        Returns:
            list: The list of variables.
        """
        vars = exit_condition.get_free_variables()
        varibales = []
        for var in vars:
            if ("! " + str(var)) in str(exit_condition):
                varibales.append(Not(var))
            else:
                varibales.append(var)
        return varibales

    def exit_condition(self, requirement)-> FNode:
        """
        Generates and returns the DNF of the exit condition for a requirement.

        Args:
            requirement: The requirement to process.

        Returns:
            FNode: The DNF of the exit condition.
        """
        return self.simplify(Not(requirement.countertrace.dc_phases[-2].invariant))

    def get_variables_dict(self):
        """
        Retrieves and sets the variables dictionary for each requirement.
        """
        for req in self.requirements:
            if req.chain_req:
                continue
            variables = self.get_variables(req.exit_conditions)
            for var in variables:
                if not var in self.variables_dict.keys():
                    if var.is_not() or var._content.payload[1].basename is "Bool":
                        self.variables_dict[var] = {"variable": var, "type_variable": "Bool", "reqs": [req]}
                    else:
                        self.variables_dict[var] = {"variable": var, "type_variable": "Int", "reqs": [req]}
                else:
                    self.variables_dict[var]["reqs"].append(req)

    def get_rtis(self):
        """
        Retrieves and sets the RTIs.
        """
        start_time = time.time()
        self.get_rtis_without_chain_reqs()
        if self.depth > len(self.chain_reqs_list):
            self.depth = len(self.chain_reqs_list)

        for depth in range(1, int(self.depth) +1):
            chain_reqs_copy = self.chain_reqs_list.copy()
            for chain_req in self.chain_reqs_list:
                self.chain_check(chain_req, depth, chain_reqs_copy, [chain_req], chain_req.exit_options.copy())
                chain_reqs_copy.remove(chain_req)

        self.get_minimum_sets()
        self.rti_csv_output()
        self.exit_conditions()
        self.duration = time.time() - start_time

    def get_rtis_without_chain_reqs(self):
        """
        Retrieves and sets the RTIs without chain requirements.
        """
        for variable in self.variables_dict:
            if self.variables_dict[variable]["type_variable"] == "Bool":
                if Not(variable) in self.variables_dict.keys():
                    positives = self.variables_dict[variable]["reqs"]
                    negatives = self.variables_dict[Not(variable)]["reqs"]
                    combinations = list(itertools.product(positives, negatives))
                    for combo in combinations:
                        if self.rti_check_exit_conditions([combo[0].exit_conditions, combo[1].exit_conditions]):
                            if self.rti_bounds([combo[0].exit_options[0], combo[1].exit_options[0]]):
                                self.rtis.append([combo[0], combo[1]])
            else:
                combinations = list(itertools.combinations(self.variables_dict[variable]["reqs"], 2))
                for combo in combinations:
                    if self.rti_check_exit_conditions([combo[0].exit_conditions, combo[1].exit_conditions]):
                        if self.rti_bounds([combo[0].exit_options[0], combo[1].exit_options[0]]):
                            self.rtis.append([combo[0], combo[1]])

    def rti_check_exit_conditions(self, ecs)-> bool:
        """
        Checks if the exit conditions are satisfiable.

        Args:
            ecs (list): List of exit conditions.

        Returns:
            bool: True if the exit conditions are not satisfiable, False otherwise.
        """
        formula = And(ecs[0], ecs[1])
        formula = self.simplify(formula)
        if not is_sat(formula):
            return True
        return False

    def rti_check_two_old(self, reqs)-> bool:
        """
        Checks if two requirements are valid RTIs.

        Args:
            reqs (list): List of requirements.

        Returns:
            bool: True if the requirements are valid RTIs, False otherwise.
        """
        if not (reqs[0].start_req or reqs[1].start_req):
            return False
        help = []
        if type(reqs[0].countertrace.dc_phases[-2].bound) is not int and type(reqs[1].countertrace.dc_phases[-2].bound) is not int:
            help.append(reqs[0].countertrace.dc_phases[-2].invariant)
            help.append(reqs[1].countertrace.dc_phases[-2].invariant)
            if reqs[0].countertrace.dc_phases[-2].bound == reqs[1].countertrace.dc_phases[-2].bound:
                if not is_sat(And(help[0], help[1])):
                    return True
                return False
        return True

    def rti_csv_output(self):
        """
        Outputs the RTIs to a CSV file.
        """
        with open('rtis.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["#Requirements", "depth", "IDs", "Countertraces", "Exit Conditions"])
            for rti in self.rtis:
                count = len(rti)
                depth = sum(1 for req in rti if req.chain_req)
                ids = [req.id for req in rti]
                countertraces = [str(req.countertrace) for req in rti]
                ecit_conditions = [str(req.exit_conditions) for req in rti]
                writer.writerow([count, depth, "\n".join(ids), "\n".join(countertraces), "\n".join(ecit_conditions)])

    def exit_conditions(self):
        """
        Outputs the exit conditions to a CSV file.
        """
        with open('ecs.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["chain-req", "countertrace", "IDs", "Exit Conditions"])
            for req in self.requirements:
                writer.writerow([str(req.chain_req), str(req.countertrace).replace(';', ':'), req.requirement.rid, req.exit_conditions])

    def chain_check(self, chain_req, depth, chain_reqs, reqs_in_check, exit_conditions):
        """
        Checks the chain requirements.

        Args:
            chain_req: The chain requirement to check.
            depth (int): The depth of the check.
            chain_reqs (list): List of chain requirements.
            reqs_in_check (list): List of requirements in check.
            exit_conditions (list): List of exit conditions.
        """
        if len(reqs_in_check) == depth:
            self.fill_with_singles(chain_req, depth, chain_reqs, reqs_in_check, exit_conditions)
        else:
            for new_chain_req in chain_reqs:
                new_ec = exit_conditions.copy()
                possible_rti = False
                if new_chain_req not in reqs_in_check:
                    for ec in new_chain_req.exit_options:
                        new_ec_ = False
                        for old_exit_condition in exit_conditions:
                            if self.rti_check_exit_conditions([ec.exit_condition, old_exit_condition.exit_condition]):
                                if self.rti_bounds([ec, old_exit_condition]):
                                    possible_rti = True
                                    if old_exit_condition in new_ec:
                                        new_ec.remove(old_exit_condition)
                                    new_ec_ = True
                        if not new_ec_:
                            new_ec.append(ec)
                    if possible_rti:
                        new_list = reqs_in_check.copy() + [new_chain_req]
                        if len(new_ec) == 0:
                            self.rtis.append(new_list)
                        else:
                            self.chain_check(chain_req, depth, chain_reqs, new_list.copy(), new_ec.copy())

    def fill_with_singles(self, chain_req, depth, chain_reqs, reqs_in_check, exit_conditions):
        """
        Fills the RTIs with single requirements.

        Args:
            chain_req: The chain requirement to check.
            depth (int): The depth of the check.
            chain_reqs (list): List of chain requirements.
            reqs_in_check (list): List of requirements in check.
            exit_conditions (list): List of exit conditions.
        """
        singles_list = []
        for ec in exit_conditions:
            help = []
            for var in ec.exit_variables:
                if var.is_not() or var._content.payload[1].basename is "Bool":
                    if Not(var) in self.variables_dict.keys():
                        for req in self.variables_dict[Not(var)]["reqs"]:
                            if self.rti_check_exit_conditions([ec.exit_condition, req.exit_conditions]):
                                if self.rti_bounds([req.exit_options[0], ec]):
                                    help.append(req)
                else:
                    if var in self.variables_dict.keys():
                        for req in self.variables_dict[var]["reqs"]:
                            if self.rti_check_exit_conditions([ec.exit_condition, req.exit_conditions]):
                                if self.rti_bounds([req.exit_options[0], ec]):
                                    help.append(req)
            if len(help) > 0:
                singles_list.append(help)
            else:
                return
        combinations = list(itertools.product(*singles_list))
        for combo in combinations:
            helpi = []
            for i in combo:
                helpi.append(i)
            self.rtis.append(helpi + reqs_in_check)

    def rti_bounds(self, exit_options)-> bool:
        """
        Checks the bounds of the exit options.

        Args:
            exit_options (list): List of exit options.

        Returns:
            bool: True if the bounds are valid, False otherwise.
        """
        help = []
        if type(exit_options[0].exit_phase.bound) is not int and type(exit_options[1].exit_phase.bound) is not int:
            if exit_options[0].exit_phase.bound == exit_options[1].exit_phase.bound:
                if not is_sat(And(exit_options[0].last_red_phase.invariant, exit_options[1].last_red_phase.invariant)):
                    return False
            elif exit_options[0].exit_phase.bound._content.payload > exit_options[1].exit_phase.bound._content.payload:
                if not is_sat(And(exit_options[0].exit_phase.invariant, exit_options[1].last_red_phase.invariant)):
                    return False
            elif exit_options[0].exit_phase.bound._content.payload < exit_options[1].exit_phase.bound._content.payload:
                if not is_sat(And(exit_options[0].last_red_phase.invariant, exit_options[1].exit_phase.invariant)):
                    return False
        return True

    def get_minimum_sets(self):
        """
        Retrieves and sets the minimum sets of requirements that are RTIs.
        """
        minimum_sets = []
        self.rtis.sort(key=lambda x: len(x))
        copy = self.rtis.copy()
        self.rtis = []
        i = 0
        while i < len(copy):
            j = i + 1
            while j < len(copy):
                if all(x in copy[i] for x in copy[j]):
                    copy.remove(copy[j])
                else:
                    j += 1
            i += 1
        self.rtis = copy

    def get_req_mapping(self) -> dict[str, dict[str, RtiSet]]:
        """
        Retrieves the mapping of requirements.

        Returns:
            dict: The mapping of requirements.
        """
        result = defaultdict(lambda: defaultdict(dict))

        id = 0
        for rti in self.rtis:
            for req in rti:
                result[id][req.requirement.rid + "_" + str(req.formalization.id) + "_" + str(req.countertrace_id)] = req
            id += 1

        return result
    def get_time(self):
        """
        Retrieves the duration of the RTI check.

        Returns:
            float: The duration of the RTI check.
        """
        time = self.duration / 60
        return round(time, 2)

    def get_depth_from_input(self, depth1):
        try:
            int(depth1)
            self.depth = int(depth1)
            return True
        except ValueError:
            self.depth = 1
            return False