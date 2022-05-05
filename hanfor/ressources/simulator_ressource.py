from __future__ import annotations

import fnmatch
import json
import multiprocessing
import os
import time
import uuid
from distutils.util import strtobool

from flask import Flask, render_template
from pysmt.shortcuts import Bool, Int, Real
from pysmt.typing import BOOL, INT, REAL

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from req_simulator.countertrace import CountertraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton
from req_simulator.scenario import Scenario
from req_simulator.simulator import Simulator
from req_simulator.utils import get_countertrace_parser
from reqtransformer import Requirement, Formalization, VariableCollection
from ressources import Ressource

from patterns import PATTERNS

validation_patterns = {
    BOOL: '^0|false|1|true$',
    INT: '^[+-]?\d+$',
    REAL: '^[+-]?\d*[.]?\d+$'
}

class SimulatorRessource(Ressource):
    simulator_cache: dict[str, Simulator] = {}

    def __init__(self, app, request):
        super().__init__(app, request)

    def GET(self):
        command = self.request.args.get('command')

        if command == 'get_simulators':
            self.get_simulators()

        if command == 'get_simulator':
            self.get_simulator()

        if command == 'start_simulator':
            self.start_simulator()

        if command == 'scenario_save':
            self.scenario_save()

    def POST(self):
        command = self.request.form.get('command')

        if command == 'create_simulator':
            self.create_simulator()

        if command == 'scenario_load':
            self.scenario_load()

        if command == 'scenario_exit':
            self.scenario_exit()

        if command == 'step_check':
            self.step_check()

        if command == 'step_next':
            self.step_next()

        if command == 'step_back':
            self.step_back()

    def DELETE(self):
        command = self.request.form.get('command')

        if command == 'delete_simulator':
            self.delete_simulator()

    def get_simulators(self) -> None:
        self.response.data = {
            'simulators': {k: v.name for k, v in self.simulator_cache.items()}
        }

    def get_simulator(self) -> bool:
        request = self.request.args if len(self.request.args) > 0 else self.request.form
        simulator_id = request.get('simulator_id')

        if simulator_id == '':
            self.response.success = False
            self.response.errormsg = 'No simulator id given.'
            return False

        simulator = self.simulator_cache[simulator_id]

        self.response.data = {
            'simulator_id': simulator_id,
            'simulator_name': simulator.name,
            'scenario': simulator.get_scenario(),
            'cartesian_size': simulator.get_cartesian_size(),
            'time_step': str(simulator.time_steps[-1]),
            'times': simulator.get_times(),
            'transitions': simulator.get_transitions(),
            'variables': simulator.get_variables(),
            'active_dc_phases': simulator.get_active_dc_phases(),
            'models': simulator.get_models(),
            'types': simulator.get_types(),
            'max_results': str(simulator.max_results)
        }

        return True

    def start_simulator(self) -> None:
        if not self.get_simulator():
            return

        simulator = self.simulator_cache[self.response.data['simulator_id']]
        self.response.data['html'] = render_template('simulator-modal.html', simulator=simulator, valid_patterns=validation_patterns)

    def scenario_save(self) -> None:
        if not self.get_simulator():
            return

        simulator = self.simulator_cache[self.response.data['simulator_id']]
        scenario = Scenario(simulator.times, {k: v for k, v in simulator.models.items()})
        self.response.data['scenario_str'] = Scenario.to_json_string(scenario)

    def create_simulator(self) -> None:
        requirement_ids = json.loads(self.request.form.get('requirement_ids'))
        simulator_name = self.request.form.get('simulator_name')

        if len(requirement_ids) <= 0:
            self.response.success = False
            self.response.errormsg = 'No requirement ids given.'
            return

        peas = []
        var_collection = VariableCollection.load(self.app.config['SESSION_VARIABLE_COLLECTION'])

        for requirement_id in requirement_ids:
            peas_tmp = SimulatorRessource.create_phase_event_automata(requirement_id, var_collection, self.app)

            if peas_tmp is None:
                self.response.success = False
                self.response.errormsg = f'Unable to constuct phase event automaton for {requirement_id}.'
                return

            peas.extend(peas_tmp)

        simulator_id = uuid.uuid4().hex
        self.simulator_cache[simulator_id] = Simulator(peas, name=simulator_name)

        self.response.data = {
            'simulator_id': simulator_id,
            'simulator_name': simulator_name
        }

    def scenario_load(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        scenario_str = self.request.form.get('scenario_str')

        if scenario_str == '':
            self.response.success = False
            self.response.errormsg = 'No scenario given.'
            return

        scenario = Scenario.from_json_string(scenario_str)
        simulator = self.simulator_cache[simulator_id]
        self.simulator_cache[simulator_id] = Simulator(simulator.peas, scenario, simulator.name)

        self.get_simulator()

    def scenario_exit(self) -> None:
        self.get_simulator()

        simulator = self.simulator_cache[self.response.data['simulator_id']]
        simulator.scenario = None
        self.response.data['scenario'] = None

    def step_check(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        time_step = self.request.form.get('time_step')
        max_results = self.request.form.get('max_results')
        variables = json.loads(self.request.form.get('variables'))

        simulator = self.simulator_cache[simulator_id]
        simulator.time_steps[-1] = float(time_step)
        simulator.max_results = int(max_results)

        var_str_mapping = {str(k): k for k in simulator.variables}
        const_mapping = {
            BOOL: lambda v: Bool(bool(strtobool(v))),
            INT: lambda v: Int(int(v)),
            REAL: lambda v: Real(float(v))
        }

        variables = {
            var_str_mapping[k]: const_mapping[var_str_mapping[k].symbol_type()](v)
            if v is not None else v for k, v in variables.items()}

        simulator.update_variables(variables)

        start = time.time()
        if not simulator.check_sat():
            self.response.success = False
            self.response.errormsg = simulator.sat_error
            return
        print('Check sat:', time.time() - start)

        self.get_simulator()


    def step_next(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        transition_id = self.request.form.get('transition_id')

        if transition_id is None or transition_id == '':
            self.response.success = False
            self.response.errormsg = 'No transition id given.'
            return

        simulator = self.simulator_cache[simulator_id]
        simulator.step_next(int(transition_id))
        self.get_simulator()

    def step_back(self) -> None:
        simulator_id = self.request.form.get('simulator_id')

        simulator = self.simulator_cache[simulator_id]
        if not simulator.step_back():
            self.response.success = False
            self.response.errormsg = 'Step back not possible.'

        self.get_simulator()

    def delete_simulator(self) -> None:
        simulator_id = self.request.form.get('simulator_id')

        if simulator_id == '':
            self.response.success = False
            self.response.errormsg = 'No simulator id given.'
            return

        if self.simulator_cache.pop(simulator_id, None) is None:
            self.response.success = False
            self.response.errormsg = 'Could not find simulator with given id.'

        self.get_simulators()

    @staticmethod
    def load_phase_event_automata(requirement_id: str, app: Flask):
        result = []

        dir = app.config['REVISION_FOLDER']
        for file in fnmatch.filter(os.listdir(dir), f'{requirement_id}_*_PEA.pickle'):
            result.append(PhaseEventAutomaton.load(os.path.join(dir, file)))

        return result

    @staticmethod
    def store_phase_event_automata(peas: list[PhaseEventAutomaton], app: Flask) -> None:
        for pea in peas:
            file = f'{pea.requirement.rid}_{pea.formalization.id}_{pea.countertrace_id}_PEA.pickle'
            pea.store(os.path.join(app.config['REVISION_FOLDER'], file))

    @staticmethod
    def delete_phase_event_automata(requirement_id: str, app: Flask):
        dir = app.config['REVISION_FOLDER']
        for file in fnmatch.filter(os.listdir(dir), f'{requirement_id}_*_PEA.pickle'):
            os.remove(os.path.join(dir, file))

    @staticmethod
    def has_variable_with_unknown_type(formalization: Formalization, variables: dict[str, str]) -> bool:
        for used_variable in formalization.used_variables:
            if variables[used_variable] == 'unknown' or variables[used_variable] == 'error':
                return True

        return False

    @staticmethod
    def create_phase_event_automata(requirement_id: str, var_collection, app: Flask) -> list[PhaseEventAutomaton] | None:
        result = []

        requirement = Requirement.load_requirement_by_id(requirement_id, app)

        variables = {k: v.type for k, v in var_collection.collection.items()}
        boogie_parser = boogie_parsing.get_parser_instance()

        for formalization in requirement.formalizations.values():
            if formalization.scoped_pattern is None or formalization.has_type_inference_errors() or \
                    SimulatorRessource.has_variable_with_unknown_type(formalization, variables):
                return None

            scope = formalization.scoped_pattern.scope.name
            pattern = formalization.scoped_pattern.pattern.name

            if len(PATTERNS[pattern]['countertraces'][scope]) <= 0:
                raise ValueError(f'No countertrace given: {scope}, {pattern}')

            expressions = {}
            for k, v in formalization.expressions_mapping.items():
                tree = boogie_parser.parse(v.raw_expression)
                expressions[k] = BoogiePysmtTransformer(var_collection.collection).transform(tree)

            for i, ct_str in enumerate(PATTERNS[pattern]['countertraces'][scope]):
                ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
                pea = build_automaton(ct, f'c_{requirement.rid}_{formalization.id}_{i}_')

                pea.requirement = requirement
                pea.formalization = formalization
                pea.countertrace_id = i
                result.append(pea)

        return result
