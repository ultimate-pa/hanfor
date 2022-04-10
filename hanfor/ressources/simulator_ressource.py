from __future__ import annotations

import fnmatch
import json
import os
import uuid
from distutils.util import strtobool

from flask import Flask, render_template
from pysmt.shortcuts import Bool, Int, Real
from pysmt.typing import BOOL, INT, REAL

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from req_simulator.countertrace import CountertraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton
from req_simulator.simulator import Simulator
from req_simulator.utils import get_countertrace_parser
from reqtransformer import Requirement, Formalization, VariableCollection
from ressources import Ressource


class SimulatorRessource(Ressource):
    simulator_cache: dict[str, Simulator] = {}

    def __init__(self, app, request):
        super().__init__(app, request)

    def GET(self):
        command = self.request.args.get('command')

        if command == 'get_simulators':
            self.get_simulators()

        if command == 'start_simulator':
            self.start_simulator()

    def POST(self):
        command = self.request.form.get('command')

        if command == 'create_simulator':
            self.create_simulator()

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
        self.response.data = {'simulators': {k: v.name for k, v in self.simulator_cache.items()}}

    def start_simulator(self) -> None:
        simulator_id = self.request.args.get('simulator_id')

        if len(simulator_id) <= 0:
            self.response.success = False
            self.response.errormsg = 'No simulator selected.'
            return

        simulator = self.simulator_cache[simulator_id]

        data = {
            'simulator_id': simulator_id,
            'simulator_name': simulator.name,
            'cartesian_size': simulator.get_cartesian_size(),
            'html': render_template('simulator-modal.html', simulator=simulator),
            'time_step': str(simulator.time_steps[-1]),
            'times': simulator.get_times(),
            'variables': simulator.get_variables(),
            'active_dc_phases': simulator.get_active_dc_phases(),
            'models': simulator.get_models(),
            'types': simulator.get_types()
        }
        self.response.data = data

    def create_simulator(self) -> None:
        requirement_ids = json.loads(self.request.form.get('requirement_ids'))

        if len(requirement_ids) <= 0:
            self.response.success = False
            self.response.errormsg = 'No requirement selected.'
            return

        peas = []
        for requirement_id in requirement_ids:
            peas_tmp = SimulatorRessource.create_phase_event_automata(requirement_id, self.app)

            if peas_tmp is None:
                self.response.success = False
                self.response.errormsg = f'Unable to constuct phase event automaton for {requirement_id}.'
                return

            peas.extend(peas_tmp)

        simulator_name = self.request.form.get('simulator_name')
        simulator_id = uuid.uuid4().hex

        self.simulator_cache[simulator_id] = Simulator(peas, name=simulator_name)
        data = {'simulator_id': simulator_id, 'simulator_name': simulator_name}
        self.response.data = data

    def step_check(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        time_step = self.request.form.get('time_step')
        variables = json.loads(self.request.form.get('variables'))

        simulator = self.simulator_cache[simulator_id]

        simulator.time_steps[-1] = float(time_step)

        var_str_mapping = {str(k): k for k in simulator.variables}
        const_mapping = {
            BOOL: lambda v: Bool(bool(strtobool(v))),
            INT: lambda v: Int(int(v)),
            REAL: lambda v: Real(float(v))
        }

        variables = {var_str_mapping[k]: const_mapping[var_str_mapping[k].symbol_type()](v) if v is not None else v for k, v in
                     variables.items()}

        simulator.update_variables(variables)
        simulator.check_sat()

        data = {
            'time_step': str(simulator.time_steps[-1]),
            'transitions': simulator.get_transitions()
        }
        self.response.data = data

    def step_next(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        transition_index = self.request.form.get('transition_index')

        if transition_index == '':
            self.response.success = False
            self.response.errormsg = 'No transition selected.'
            return

        simulator = self.simulator_cache[simulator_id]
        simulator.step_next(int(transition_index))

        data = {
            'cartesian_size': simulator.get_cartesian_size(),
            'times': simulator.get_times(),
            'time_step': str(simulator.time_steps[-1]),
            'variables': simulator.get_variables(),
            'active_dc_phases': simulator.get_active_dc_phases(),
            'models': simulator.get_models()
        }
        self.response.data = data

    def step_back(self) -> None:
        simulator_id = self.request.form.get('simulator_id')

        simulator = self.simulator_cache[simulator_id]
        if not simulator.step_back():
            self.response.success = False
            self.response.errormsg = 'Step back not possible.'

        data = {
            'cartesian_size': simulator.get_cartesian_size(),
            'times': simulator.get_times(),
            'time_step': simulator.time_steps[-1],
            'variables': simulator.get_variables(),
            'active_dc_phases': simulator.get_active_dc_phases()
        }
        self.response.data = data

    def delete_simulator(self) -> None:
        simulator_id = self.request.form.get('simulator_id')

        if len(simulator_id) <= 0:
            self.response.success = False
            self.response.errormsg = 'No simulator selected.'
            return

        value = self.simulator_cache.pop(simulator_id, None)

        if value is None:
            self.response.success = False
            self.response.errormsg = 'Could not find simulator with given id.'

        self.response.data = {'simulators': {k: v.name for k, v in self.simulator_cache.items()}}

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
    def create_phase_event_automata(requirement_id: str, app: Flask) -> list[PhaseEventAutomaton] | None:
        result = []

        requirement = Requirement.load_requirement_by_id(requirement_id, app)
        var_collection = VariableCollection.load(app.config['SESSION_VARIABLE_COLLECTION'])

        variables = {k: v.type for k, v in var_collection.collection.items()}
        boogie_parser = boogie_parsing.get_parser_instance()

        for formalization in requirement.formalizations.values():
            if formalization.scoped_pattern is None or formalization.has_type_inference_errors() or \
                    SimulatorRessource.has_variable_with_unknown_type(formalization, variables):
                return None

            scope = formalization.scoped_pattern.scope.name
            pattern = formalization.scoped_pattern.pattern.name

            expressions = {}
            for k, v in formalization.expressions_mapping.items():
                tree = boogie_parser.parse(v.raw_expression)
                expressions[k] = BoogiePysmtTransformer(var_collection.collection).transform(tree)

            for i, ct_str in enumerate(app.config['PATTERNS'][pattern]['countertraces'][scope]):
                ct = CountertraceTransformer(expressions).transform(get_countertrace_parser().parse(ct_str))
                pea = build_automaton(ct, f'c_{requirement.rid}_{formalization.id}_{i}_')
                pea.requirement = requirement
                pea.formalization = formalization
                pea.countertrace_id = i
                result.append(pea)

        return result
