import json
import os
import uuid
from dataclasses import dataclass

from flask import Flask
from lark import Lark

import boogie_parsing
from req_simulator.boogie_pysmt_transformer import BoogiePysmtTransformer
from req_simulator.counter_trace import CounterTrace, CounterTraceTransformer
from req_simulator.phase_event_automaton import PhaseEventAutomaton, build_automaton
from req_simulator.simulator import Simulator
from reqtransformer import Requirement, VariableCollection, Formalization
from ressources import Ressource

ct_parser = Lark.open('../req_simulator/counter_trace_grammar.lark', rel_to=__file__, start='counter_trace',
                      parser='lalr')


class SimulatorRessource(Ressource):
    @dataclass
    class SimulatorCacheEntry:
        name: str
        simulator: Simulator

    simulator_cache: dict[str, SimulatorCacheEntry] = {}

    def __init__(self, app, request):
        super().__init__(app, request)

    def GET(self):
        command = self.request.args.get('command')

        if command == 'get_simulators':
            self.get_simulators()

    def POST(self):
        command = self.request.form.get('command')

        if command == 'create_simulator':
            self.create_simulator()

    def DELETE(self):
        command = self.request.form.get('command')

        if command == 'delete_simulator':
            self.delete_simulator()

    def get_simulators(self) -> None:
        self.response.data = {'simulators': [(k, v.name) for k, v in self.simulator_cache.items()]}

    def create_simulator(self) -> None:
        requirement_ids = json.loads(self.request.form.get('requirement_ids'))
        simulator_name = self.request.form.get('simulator_name')
        simulator_id = uuid.uuid4().hex

        requirements = [Requirement.load_requirement_by_id(id, self.app) for id in requirement_ids]

        self.simulator_cache[simulator_id] = self.SimulatorCacheEntry(simulator_name, None)

        data = {'simulator_id': simulator_id, 'simulator_name': simulator_name}
        self.response.data = data

    def delete_simulator(self) -> None:
        simulator_id = self.request.form.get('simulator_id')
        value = self.simulator_cache.pop(simulator_id, None)

        if value is None:
            self.response.success = False
            self.response.errormsg = 'No simulator with given id found.'

    @staticmethod
    def load_counter_trace(id: str, app: Flask) -> CounterTrace:
        path = os.path.join(app.config['REVISION_FOLDER'], '{}_CT.pickle'.format(id))
        if os.path.exists(path) and os.path.isfile(path):
            return CounterTrace.load(path)

    @staticmethod
    def store_counter_trace(ct: CounterTrace, id: str, app: Flask) -> None:
        path = os.path.join(app.config['REVISION_FOLDER'], '{}_CT.pickle'.format(id))
        ct.store(path)

    @staticmethod
    def load_phase_event_automaton(id: str, app: Flask) -> PhaseEventAutomaton:
        path = os.path.join(app.config['REVISION_FOLDER'], '{}_PEA.pickle'.format(id))
        if os.path.exists(path) and os.path.isfile(path):
            return PhaseEventAutomaton.load(path)

    @staticmethod
    def store_phase_event_automaton(pea: PhaseEventAutomaton, id: str, app: Flask) -> None:
        path = os.path.join(app.config['REVISION_FOLDER'], '{}_PEA.pickle'.format(id))
        pea.store(path)

    @staticmethod
    def has_variable_with_unknown_type(formalization: Formalization, variables: dict[str, str]) -> bool:
        for used_variable in formalization.used_variables:
            if variables[used_variable] == 'unknown' or variables[used_variable] == 'error':
                return True

        return False

    @staticmethod
    def create_cts_and_peas(requirement: Requirement, var_collection: VariableCollection, app: Flask) \
            -> dict[int, list[tuple[CounterTrace, PhaseEventAutomaton]]]:
        result = {}

        variables = {k: v.type for k, v in var_collection.collection.items()}
        boogie_parser = boogie_parsing.get_parser_instance()

        for formalization_index, formalization in requirement.formalizations.items():
            if formalization.has_type_inference_errors() or \
                    SimulatorRessource.has_variable_with_unknown_type(formalization, variables):
                return {}

            scope = formalization.scoped_pattern.scope.name
            pattern = formalization.scoped_pattern.pattern.name

            expressions = {}
            for k, v in formalization.expressions_mapping.items():
                tree = boogie_parser.parse(v.raw_expression)
                expressions[k] = BoogiePysmtTransformer(variables).transform(tree)

            result[formalization_index] = []
            for i, ct_str in enumerate(app.config['PATTERNS'][pattern]['counter_traces'][scope]):
                ct = CounterTraceTransformer(expressions).transform(ct_parser.parse(ct_str))
                pea = build_automaton(ct, f'c{formalization_index}_{i}_')
                result[formalization_index].append((ct, pea))

        return result
