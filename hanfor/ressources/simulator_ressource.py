from __future__ import annotations

import json
import logging
import time
import uuid
from typing import List

from hanfor_flask import HanforFlask
from flask import render_template
from pysmt.shortcuts import Bool, Int, Real
from pysmt.typing import BOOL, INT, REAL

from lib_core import boogie_parsing
from lib_pea.boogie_pysmt_transformer import BoogiePysmtTransformer
from lib_pea.countertrace import CountertraceTransformer
from lib_pea.countertrace_to_pea import build_automaton
from lib_pea.pea import PhaseSetsPea
from lib_pea.req_to_pea import get_pea_from_formalisation, has_variable_with_unknown_type
from lib_pea.utils import get_countertrace_parser, strtobool
from configuration.patterns import PATTERNS
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from lib_core.data import Requirement, Formalization, VariableCollection, Variable, ScopedPattern, Scope
from ressources import Ressource

validation_patterns = {BOOL: r"^0|false|False|1|true|True$", INT: r"^[+-]?\d+$", REAL: r"^[+-]?\d*[.]?\d+$"}


class SimulatorRessource(Ressource):
    simulator_cache: dict[str, Simulator] = {}

    def __init__(self, app, request):
        super().__init__(app, request)

    def GET(self):
        command = self.request.args.get("command")

        if command == "get_simulators":
            self.get_simulators()

        if command == "get_simulator":
            self.get_simulator()

        if command == "start_simulator":
            self.start_simulator()

        if command == "scenario_save":
            self.scenario_save()

        if command == "get_ct":
            self.get_ct()

        if command == "variable_constraints":
            self.variable_constraints()

        if command == "inconsistency_pre_check":
            self.inconsistency_pre_check()

    def POST(self):
        command = self.request.form.get("command")

        if command == "create_simulator":
            self.create_simulator()

        if command == "scenario_load":
            self.scenario_load()

        if command == "scenario_exit":
            self.scenario_exit()

        if command == "step_check":
            self.step_check()

        if command == "step_next":
            self.step_next()

        if command == "step_back":
            self.step_back()

    def DELETE(self):
        command = self.request.form.get("command")

        if command == "delete_simulator":
            self.delete_simulator()

    def get_simulators(self) -> None:
        self.response.data = {"simulators": {k: v.name for k, v in self.simulator_cache.items()}}

    def get_simulator(self) -> bool:
        request = self.request.args if len(self.request.args) > 0 else self.request.form
        simulator_id = request.get("simulator_id")

        if simulator_id == "":
            self.response.success = False
            self.response.errormsg = "No simulator id given."
            return False

        simulator = self.simulator_cache[simulator_id]

        self.response.data = {
            "simulator_id": simulator_id,
            "simulator_name": simulator.name,
            "scenario": simulator.get_scenario(),
            "cartesian_size": simulator.get_cartesian_size(),
            "time_step": str(simulator.time_steps[-1]),
            "times": simulator.get_times(),
            "transitions": simulator.get_transitions(),
            "variables": simulator.get_variables(),
            "active_dc_phases": simulator.get_active_dc_phases(),
            "models": simulator.get_models(),
            "types": simulator.get_types(),
            "max_results": str(simulator.max_results),
        }

        return True

    def start_simulator(self) -> None:
        if not self.get_simulator():
            return

        simulator = self.simulator_cache[self.response.data["simulator_id"]]
        self.response.data["html"] = render_template(
            "simulator-modal/modal.html",
            simulator=simulator,
            valid_patterns=validation_patterns,
        )

    def scenario_save(self) -> None:
        if not self.get_simulator():
            return

        simulator = self.simulator_cache[self.response.data["simulator_id"]]
        scenario = Scenario(simulator.times, {k: v for k, v in simulator.models.items()})
        self.response.data["scenario_str"] = Scenario.to_json_string(scenario)

    def create_simulator(self) -> None:
        requirement_ids = json.loads(self.request.form.get("requirement_ids"))
        simulator_name = self.request.form.get("simulator_name")

        if len(requirement_ids) <= 0:
            self.response.success = False
            self.response.errormsg = "No requirement ids given."
            return

        peas = []
        var_collection = VariableCollection(self.app)

        for requirement_id in requirement_ids:
            peas_tmp = SimulatorRessource.create_phase_event_automata(requirement_id, var_collection, self.app)

            if peas_tmp is None:
                self.response.success = False
                self.response.errormsg = f"Unable to constuct phase event automaton for {requirement_id}."
                return

            peas.extend(peas_tmp)

        simulator_id = uuid.uuid4().hex
        self.simulator_cache[simulator_id] = Simulator(peas, name=simulator_name)

        self.response.data = {"simulator_id": simulator_id, "simulator_name": simulator_name}

    def get_ct(self):
        request = self.request.args if len(self.request.args) > 0 else self.request.form
        requirement_ids = json.loads(request.get("req"))
        if len(requirement_ids) <= 0:
            self.response.success = False
            self.response.errormsg = "No requirement ids given."
            return

        result = {"requirements": {}, "variables": []}

        var_collection = VariableCollection(self.app)
        variables = {k: v.type for k, v in var_collection.collection.items()}
        result["variables"] = [
            {"name": k, "type": v.type, "value": v.value} for k, v in var_collection.collection.items()
        ]

        for requirement_id in requirement_ids:
            requirement = self.app.db.get_object(Requirement, requirement_id)
            formalizations = {}
            for formalization in requirement.formalizations.values():
                counter_traces = []
                if not formalization.scoped_pattern.is_instantiatable():
                    return None
                if has_variable_with_unknown_type(formalization, variables) or formalization.type_inference_errors:
                    return None

                scope = formalization.scoped_pattern.scope.name
                pattern = formalization.scoped_pattern.pattern.name

                if len(PATTERNS[pattern]["countertraces"][scope]) <= 0:
                    raise ValueError(f"No countertrace given: {scope}, {pattern}")

                expressions = {}
                for k, v in formalization.expressions_mapping.items():
                    expressions[k] = v.raw_expression

                for i, ct_str in enumerate(PATTERNS[pattern]["countertraces"][scope]):
                    counter_traces.append(ct_str)
                formalizations[formalization.id] = {"counter_traces": counter_traces, "expressions": expressions}

            result["requirements"][requirement_id] = formalizations

        self.response.data = result

    def variable_constraints(self) -> None:
        simulator_id = self.request.args.get("simulator_id")

        simulator = self.simulator_cache[simulator_id]
        simulator.variable_constraints()

    def inconsistency_pre_check(self) -> None:
        simulator_id = self.request.args.get("simulator_id")

        simulator = self.simulator_cache[simulator_id]
        simulator.inconsistency_pre_check()

    def scenario_load(self) -> None:
        simulator_id = self.request.form.get("simulator_id")
        scenario_str = self.request.form.get("scenario_str")

        if scenario_str == "":
            self.response.success = False
            self.response.errormsg = "No scenario given."
            return

        scenario = Scenario.from_json_string(scenario_str)
        simulator = self.simulator_cache[simulator_id]
        self.simulator_cache[simulator_id] = Simulator(simulator.peas, scenario, simulator.name)

        self.get_simulator()

    def scenario_exit(self) -> None:
        self.get_simulator()

        simulator = self.simulator_cache[self.response.data["simulator_id"]]
        simulator.scenario = None
        self.response.data["scenario"] = None

    def step_check(self) -> None:
        simulator_id = self.request.form.get("simulator_id")
        time_step = self.request.form.get("time_step")
        max_results = self.request.form.get("max_results")
        variables = json.loads(self.request.form.get("variables"))

        simulator = self.simulator_cache[simulator_id]
        simulator.time_steps[-1] = float(time_step)
        simulator.max_results = int(max_results)

        var_str_mapping = {str(k): k for k in simulator.variables}
        const_mapping = {
            BOOL: lambda v: Bool(bool(strtobool(v))),
            INT: lambda v: Int(int(v)),
            REAL: lambda v: Real(float(v)),
        }

        variables = {
            var_str_mapping[k]: const_mapping[var_str_mapping[k].symbol_type()](v) if v is not None else v
            for k, v in variables.items()
        }

        simulator.update_variables(variables)

        start = time.time()
        if not simulator.check_sat():
            self.response.success = False
            self.response.errormsg = simulator.sat_error
            return
        logging.debug(f"Did sat-check. Took {time.time() - start} sec")

        self.get_simulator()

    def step_next(self) -> None:
        simulator_id = self.request.form.get("simulator_id")
        transition_id = self.request.form.get("transition_id")

        if transition_id is None or transition_id == "":
            self.response.success = False
            self.response.errormsg = "No transition id given."
            return

        simulator = self.simulator_cache[simulator_id]
        simulator.step_next(int(transition_id))
        self.get_simulator()

    def step_back(self) -> None:
        simulator_id = self.request.form.get("simulator_id")

        simulator = self.simulator_cache[simulator_id]
        if not simulator.step_back():
            self.response.success = False
            self.response.errormsg = "Step back not possible."

        self.get_simulator()

    def delete_simulator(self) -> None:
        simulator_id = self.request.form.get("simulator_id")

        if simulator_id == "":
            self.response.success = False
            self.response.errormsg = "No simulator id given."
            return

        if self.simulator_cache.pop(simulator_id, None) is None:
            self.response.success = False
            self.response.errormsg = "Could not find simulator with given id."

        self.get_simulators()

    @staticmethod
    def create_phase_event_automata(
        requirement_id: str, var_collection: VariableCollection, app: HanforFlask
    ) -> List[PhaseSetsPea]:
        result = []

        requirement = app.db.get_object(Requirement, requirement_id)

        for formalization in requirement.formalizations.values():
            if not formalization.scoped_pattern.is_instantiatable():
                continue
            peas = get_pea_from_formalisation(requirement.rid, formalization, var_collection)
            for i, pea in enumerate(peas):
                pea.requirement = requirement
                pea.formalization = formalization
                pea.countertrace_id = i
            result.extend(peas)
        return result
