"""
2024 Mirko Werling, University of Freiburg, Department of Computer Science <mirko_werling@gmx.de>

---- reused/copied some classes from reqtransformer.py ----
"""

# import reqtransformer as reqtrans
import app as app
import logging

import boogie_parsing
from boogie_parsing import run_typecheck_fixpoint, BoogieType
from patterns import PATTERNS
from enum import Enum
from typing import Dict, Tuple

var_collection = None

class StateMachine:
    """
    Creating the state machine.
    State machine need to be in transition and list form.

    s_machine = [[s_1, a_1, s_2],
                 [s_2, a_2, s_3],
                 ...
                ]
    """
    def __init__(self, s_machine: list):
        self.transitions = s_machine
        self.states: list = []
        self.actions: list = []
        self.basics = ["State", "Action"]
        self.setting()

    def set_state_machine(self, sm_list):
        self.transitions = sm_list

    def setting(self):
        """
        Setting the states and actions, that are needed within the state machine.
        Write into global variables self.states and self.actions.
        """
        for transition in self.transitions:
            c_state = transition[0]
            if c_state not in self.states:
                self.states.append(c_state)

            action = transition[1]
            if action not in self.actions:
                self.actions.append(action)

    def create_variables(self):
        """
        Creating the variables for the Variable Collection class.
        Cause the variable names are based on the state and action names.

        :return: var_collection
        :rtype: VariableCollection
        """
        states = self.states
        actions = self.actions
        basics = self.basics

        # print(states, actions, basics)

        var_collection = VariableCollection()

        # list_variables = []
        counter = 0
        for basic in basics:
            if basic == "State":
                var_collection.add_var(var_name=basic, variable=None)

                # var = Variable(
                #     name=basic,
                #     type="ENUM",  # Enum_INT in the hanfor web interface
                #     # thought first it is a good idea to have the belongs to variables as list in the value property
                #     # value=list_val ## no value cause in the hanfor also no value
                # )
                var_collection.collection[basic].set_type("ENUM_INT")
                for state in states:
                    var_collection.add_var(var_name=state, variable=None)
                    var_collection.collection[state].set_type("ENUMERATOR_INT")
                    var_collection.collection[state].set_belongs_to_enum(basic)
                    var_collection.collection[state].set_value(str(counter))
                    counter += 1

            elif basic == "Action":
                var_collection.add_var(var_name=basic, variable=None)
                var_collection.collection[basic].set_type("ENUM_INT")
                # var_collection.collection[var.name] = var
                action = "no_op"

                # creat the no_op action
                counter = 0
                var_collection.add_var(var_name=action, variable=None)
                var_collection.collection[action].set_type("ENUMERATOR_INT")
                var_collection.collection[action].set_belongs_to_enum(basic)
                var_collection.collection[action].set_value(str(counter))

                # create the rest actions
                counter += 1
                for action in actions:
                    var_collection.add_var(var_name=action, variable=None)
                    var_collection.collection[action].set_type("ENUMERATOR_INT")
                    var_collection.collection[action].set_belongs_to_enum(basic)
                    var_collection.collection[action].set_value(str(counter))
                    counter += 1

                # list_variables.append(var)

        return var_collection

    def from_state_machine_to_requirement(self):
        """
        The function creates the requirements from the state machine.

        :return: reqs_collection : collection of all created requirements.
        :rtype: RequirementCollection.
        """
        reqs_collection = RequirementCollection()
        states = self.states
        actions = self.actions

        for transition in self.transitions:
            # print(self.transitions)
            current_state = transition[0]
            action = transition[1]
            successor_state = transition[2]

            # property for all
            type_in_csv = "requirement"

            # preparing the requirement attributes
            index = reqs_collection.next_free_id_index()
            rid = f"{index:02d}" # for get a leading zero with less than two digits
            # id = "0" + str(counter)
            description = "From " + str(current_state) + " to " + str(successor_state) + "."
            # pos_in_csv = counter

            reqs_collection.add_requirement_from_sm(req_id=rid,
                                                    req_description=description,
                                                    type_in_csv=type_in_csv,
                                                    pos_in_csv=index)
            reqs_collection.add_attributes_from_sm_to_req(rid, current_state, action, successor_state)

            # for implicit transitions
            action = "no_op"
            imp_index = reqs_collection.next_free_id_index()
            imp_id = f"{imp_index:02d}"
            imp_description = "From " + str(current_state) + " to " + str(current_state) + "."
            reqs_collection.add_requirement_from_sm(req_id=imp_id,
                                                    req_description=imp_description,
                                                    type_in_csv=type_in_csv,
                                                    pos_in_csv=imp_index)
            reqs_collection.add_attributes_from_sm_to_req(imp_id, current_state, action, current_state)
            # ToDo: Check if requirement exists before adding

        return reqs_collection

class Requirement:
    """
    The class of one Requirement. Very much reused from the reqtransformer.py.
    But without the base classes (HanforVersioned and Pickleable).
    """
    def __init__(self, id: str, description: str, type_in_csv: str, csv_row: dict[str, str], pos_in_csv: int):
        self.rid: str = id
        self.formalizations: Dict[int, Formalization] = dict()
        self.description = description
        self.type_in_csv = type_in_csv
        self.csv_row = csv_row
        self.pos_in_csv = pos_in_csv
        # self.tags: OrderedDict[str, str] = OrderedDict()
        self.status = 'Todo'
        self._revision_diff = dict()

        self.current_state: str = ""
        self.action: str = ""
        self.successor_state: str = ""
        # ToDo: Save in action all the actions that have a outgoing transition in this state. then we can replace
        #       no_op with these actions and negate them.

    def __str__(self):
        return (f'Id: {self.rid}, \nDescription: {self.description}, \nType in CSV: {self.type_in_csv}, '
                f'\nPos in CSV: {self.pos_in_csv}')

    def __repr__(self):
        return f'Requirement("{self.rid}","{self.description}",{self.type_in_csv}, {self.csv_row}, {self.pos_in_csv})'

    def _next_free_formalization_id(self):
        i = 0
        while i in self.formalizations.keys():
            i += 1
        return i

    def add_empty_formalization(self) -> Tuple[int, 'Formalization']:
        """ Add an empty formalization to the formalizations list."""
        id = self._next_free_formalization_id()
        self.formalizations[id] = Formalization(id)
        return id, self.formalizations[id]

    def do_formalization_based_on_sm(self, var_collection):
        """
        Setting the formalization in the requirement.
        Based on sm means, that scope_name and pattern_name are specific for the background of state machine,
        therefore it is hard coded here.

        :param var_collection: Collection of the variables.
        :type var_collection: VariableCollection
        """
        id, formalization = self.add_empty_formalization()
        # ToDo: Don't hard code the state machine specific arguments, instead make it as variable.
        scope_name = "GLOBALLY"
        pattern_name = "StateMachineTimeless"
        formalization_id = id
        mapping = self.do_mapping(var_collection)
        # set scoped pattern
        self.formalizations[formalization_id].scoped_pattern = ScopedPattern(
            Scope[scope_name], Pattern(name=pattern_name)
        )
        # set parent
        self.formalizations[formalization_id].belongs_to_requirement = self.rid
        # Parse and set the expressions.
        self.formalizations[formalization_id].set_expressions_mapping(mapping=mapping,
                                                                      variable_collection=var_collection,
                                                                      rid=self.rid)

        # ToDo: for implicit transitions another scope pattern name 'Invariance'
        #       implemented in pattern.py as 'Invariant'
        # ToDo: implement mapping and variable collection


    def do_mapping(self, var_collection):
        """
        Mapping the expressions to the variables, to combine the formalizations.
        Here hardcoded, because allways he same pattern.

        :return: mapping - e.g. {'R': 'State == State_Off', 'S': 'Action == Action_turn_on', 'T': 'State == State_On'}
        :rtype: dict
        """
        mapping: Dict[str, str] = {}
        ex_r = "State" + " == " + "State_" + self.current_state
        ex_s = "Action" + " == " + "Action_" + self.action
        ex_t = "State" + " == " + "State_" + self.successor_state

        r = "R"
        s = "S"
        t = "T"

        mapping[r] = ex_r
        mapping[s] = ex_s
        mapping[t] = ex_t

        return mapping


class RequirementCollection:
    """
    The class of all requirements.
    However, without base classes (HanforVersioned and Pickleable), which makes it easier.
    Combining the key features for pattern to the state machines.
    """
    def __init__(self):
        # self.requirements = list()
        # collection contains all the requirements
        self.collection: Dict[str, Requirement] = dict()

    def __str__(self):
        returnval = "The Requirement Collection contains the following requirements:\n"
        for req_id, req in self.collection.items():
            returnval += "    " + req.rid + " " + "'" + req.description + "' " + req.type_in_csv + " " + str(req.csv_row) + " " + str(req.pos_in_csv) + "\n"
        return returnval

    def __repr__(self):
        returnval = "RequirementCollection( \n"
        for req_id, req in self.collection.items():
            returnval += ("    (" + req.rid + ": Requirement(" + req.rid + " " + req.description + " " +
                          req.type_in_csv + " " + str(req.pos_in_csv) + ")\n")
        return returnval


    def add_requirement_from_sm(self, req_id: str, req_description: str, type_in_csv: str, pos_in_csv: int):
        """
        Function that adds a requirement to the collection. collection (dict)

        :param: req_id (str) : requirement id
        :param: req_description (str) : requirement description
        :param: type_in_csv (str) : type in csv #this is needed cause of the reused requirement class
        # ToDo: Could load the state machine from csv file
        :param: pos_in_csv (int) : position in csv

        """
        if req_id not in self.collection:
            requirement = Requirement(id=req_id, description=req_description, type_in_csv=type_in_csv,
                                      csv_row=None, pos_in_csv=pos_in_csv)
        print("Adding requirement with id " + str(req_id) + " to collection.")
        self.collection[req_id] = requirement

    def next_free_id_index(self):
        return len(self.collection) + 1

    def do_formalization_for_all_reqs(self, var_collection):
        """
        Function doing the formalization for all requirements in the collection of the requirement collection.

        :param: var_collection (VariableCollection) : variable collection
        :return: counter (int) : counts the formalizations
        """
        counter = 0
        for req in self.collection.values():
            req.do_formalization_based_on_sm(var_collection=var_collection)
            #print(req.formalizations.values())
            if req != None:
                for formalization in req.formalizations.values():
                    if formalization != None:
                        print(formalization)
                        counter += 1
        return counter
    def add_attributes_from_sm_to_req(self, req_id, current_state, action, successor_state):
        """
        Adding the attributes from state machine to requirement. Attributes are current_state, action
        and successor_state.

        :param: req_id : requirement id
        :param: current_state : is the (current) state of the transition
        :param: action : action leading to next state
        :param: successor_state : successor state after taking action

        """
        requirement = self.collection[req_id]
        requirement.current_state = current_state
        requirement.action = action
        requirement.successor_state = successor_state

class Formalization:
    """
    The Formalization according to a specific requirement. Very much reused from the reqtransformer.py.
    But without the base class (HanforVersioned).
    """
    def __init__(self, id: int):
        self.id: int = id
        self.scoped_pattern = ScopedPattern()
        self.expressions_mapping: dict[str, Expression] = dict()  # value - expression # key
        self.belongs_to_requirement = None
        self.type_inference_errors = dict()

    def __str__(self):
        returnval = ("The Formalization of requirement " + str(self.belongs_to_requirement) + ":\n" +
                     "Pattern: " + self.scoped_pattern.pattern.name + "\n")
        for string, expression in self.expressions_mapping.items():
            returnval += "    " + string + " " + str(expression) + "\n"
        return returnval

    def set_expressions_mapping(self, mapping, variable_collection, rid):
        """ Parse expression mapping.
            + Extract variables. Replace by their ID. Create new Variables if they do not exist.
            + For used variables and update the "used_by_requirements" set.

        :type mapping: dict
        :param mapping: {'P': 'foo > 0', 'Q': 'expression for Q', ...}
        :type variable_collection: VariableCollection
        :param variable_collection: Currently used VariableCollection.
        :type rid: str
        :param rid: associated requirement id

        :return: type_inference_errors dict {key: type_env, ...}
        :rtype: dict
        """
        for key, expression_string in mapping.items():
            # if len(expression_string) == 0:
            #    continue
            expression = Expression()
            expression.set_expression(expression_string, variable_collection, rid)
            if self.expressions_mapping is None:
                self.expressions_mapping = dict()
            self.expressions_mapping[key] = expression
        self.get_string()
        self.type_inference_check(variable_collection)

    def get_string(self):
        return self.scoped_pattern.get_string(self.expressions_mapping)

    def type_inference_check(self, variable_collection):
        """ Apply type inference check for the expressions in this formalization.
        Reload if applied multiple times.

        :param variable_collection: The current VariableCollection
        """
        allowed_types = self.scoped_pattern.get_allowed_types()
        var_env = variable_collection.get_boogie_type_env()

        for key, expression in self.expressions_mapping.items():
            # We can only check type inference,
            # if the pattern has declared allowed types for the current pattern key e.g. `P`
            if key not in allowed_types.keys():
                continue

            # Check if the given expression can be parsed by lark.
            # Else there is a syntax error in the expression.
            try:
                tree = boogie_parsing.get_parser_instance().parse(expression.raw_expression)
            except LarkError as e:
                logging.error(
                    f'Lark could not parse expression `{expression.raw_expression}`: \n {e}. Skipping type inference')
                continue
            expression.set_expression(expression.raw_expression, variable_collection, expression.parent_rid)

            # Derive type for variables in expression and update missing or changed types.
            ti = run_typecheck_fixpoint(tree, var_env, expected_types=allowed_types[key])
            expression_type, type_env, type_errors = ti.type_root.t, ti.type_env, ti.type_errors

            # Add type error if a variable is used in a timing expression
            if allowed_types[key] != [BoogieType.bool]:
                for var in expression.used_variables:
                    if variable_collection.collection[var].type != 'CONST':
                        type_errors.append(f"Variable '{var}' used in time bound.")

            for name, var_type in type_env.items():  # Update the hanfor variable types.
                if (variable_collection.collection[name].type
                        and variable_collection.collection[name].type.lower() in ['const', 'enum']):
                    continue
                if variable_collection.collection[name].type not in boogie_parsing.BoogieType.aliases(var_type):
                    logging.info(f'Update variable `{name}` with derived type. '
                                 f'Old: `{variable_collection.collection[name].type}` => New: `{var_type.name}`.')
                    variable_collection.set_type(name, var_type.name)
            if type_errors:
                self.type_inference_errors[key] = type_errors
            elif key in self.type_inference_errors:
                # TODO: refactor the whole error handling process, as this gets too complex
                del self.type_inference_errors[key]
        variable_collection.store()


class Expression:
    """
    The Expression for the formalization procedure. Very much copied from the reqtransformer.py.
    But without the base class (HanforVersioned).

    Representing an Expression in a ScopedPattern.
    For example: Let
       `Globally, {P} is always true.`
    be a Scoped pattern. One might replace {P} by
        `NO_PAIN => NO_GAIN`
    Then `NO_PAIN => NO_GAIN` is the Expression.
     """
    def __init__(self):
        self.used_variables: list[str] = list()
        self.raw_expression = None
        self.parent_rid = None

    def set_expression(self, expression: str, variable_collection: 'VariableCollection', parent_rid):
        """ Parses the Expression using the boogie grammar.
            * Extract variables.
                + Create new ones if not in Variable collection.
                + Replace Variables by their identifier.
            * Store set of used variables to `self.used_variables`
        """
        self.raw_expression = expression
        self.parent_rid = parent_rid
        # Get the vars occurring in the expression.
        parser = boogie_parsing.get_parser_instance()
        tree = parser.parse(expression)

        self.used_variables = set(boogie_parsing.get_variables_list(tree))

        new_vars = []
        for var_name in self.used_variables:
            if var_name not in variable_collection:
                variable_collection.add_var(var_name)
                new_vars.append(var_name)

        # TODO: restore if needed, not clear what this does
        # further app was not always available here, thus this has to be refactored
        # if len(new_vars) > 0:
        #    variable_collection.reload_script_results(app, new_vars)

        variable_collection.map_req_to_vars(parent_rid, self.used_variables)
        # try:
        #    variable_collection.store(app.config['SESSION_VARIABLE_COLLECTION'])
        # except:
        #    pass

    def __str__(self):
        return f'"{self.raw_expression}"'

    def type_inference_check(self, variable_collection):
        """ Apply type inference check for the expressions in this formalization.
        Reload if applied multiple times.

        :param variable_collection: The current VariableCollection
        """
        allowed_types = self.scoped_pattern.get_allowed_types()
        var_env = variable_collection.get_boogie_type_env()

        for key, expression in self.expressions_mapping.items():
            # We can only check type inference,
            # if the pattern has declared allowed types for the current pattern key e.g. `P`
            if key not in allowed_types.keys():
                continue

            # Check if the given expression can be parsed by lark.
            # Else there is a syntax error in the expression.
            try:
                tree = boogie_parsing.get_parser_instance().parse(expression.raw_expression)
            except LarkError as e:
                logging.error(
                    f'Lark could not parse expression `{expression.raw_expression}`: \n {e}. Skipping type inference')
                continue
            expression.set_expression(expression.raw_expression, variable_collection, expression.parent_rid)

            # Derive type for variables in expression and update missing or changed types.
            ti = run_typecheck_fixpoint(tree, var_env, expected_types=allowed_types[key])
            expression_type, type_env, type_errors = ti.type_root.t, ti.type_env, ti.type_errors

            # Add type error if a variable is used in a timing expression
            if allowed_types[key] != [BoogieType.bool]:
                for var in expression.used_variables:
                    if variable_collection.collection[var].type != 'CONST':
                        type_errors.append(f"Variable '{var}' used in time bound.")

            for name, var_type in type_env.items():  # Update the hanfor variable types.
                if (variable_collection.collection[name].type
                        and variable_collection.collection[name].type.lower() in ['const', 'enum']):
                    continue
                if variable_collection.collection[name].type not in boogie_parsing.BoogieType.aliases(var_type):
                    logging.info(f'Update variable `{name}` with derived type. '
                                 f'Old: `{variable_collection.collection[name].type}` => New: `{var_type.name}`.')
                    variable_collection.set_type(name, var_type.name)
            if type_errors:
                self.type_inference_errors[key] = type_errors
            elif key in self.type_inference_errors:
                # TODO: refactor the whole error handling process, as this gets too complex
                del self.type_inference_errors[key]
        variable_collection.store()


# unsicher ob notwendig !!!
class Scope(Enum):
    """
    The Scope of a formalization. Copied from the reqtransformer.py.
    """
    GLOBALLY = 'Globally'
    BEFORE = 'Before "{P}"'
    AFTER = 'After "{P}"'
    BETWEEN = 'Between "{P}" and "{Q}"'
    AFTER_UNTIL = 'After "{P}" until "{Q}"'
    NONE = '// None'

    def instantiate(self, *args):
        return str(self.value).format(*args)

    def get_slug(self):
        """ Returns a short slug representing the scope value.
        Use in applications where you don't want to use the full string.

        :return: Slug like AFTER_UNTIL for 'After "{P}" until "{Q}"'
        :rtype: str
        """
        slug_map = {
            str(self.GLOBALLY): 'GLOBALLY',
            str(self.BEFORE): 'BEFORE',
            str(self.AFTER): 'AFTER',
            str(self.BETWEEN): 'BETWEEN',
            str(self.AFTER_UNTIL): 'AFTER_UNTIL',
            str(self.NONE): 'NONE'
        }
        return slug_map[self.__str__()]

    def __str__(self):
        result = str(self.value).replace('"', '')
        return result

    def get_allowed_types(self):
        scope_env = {
            'GLOBALLY': {
            },
            'BEFORE': {
                'P': [boogie_parsing.BoogieType.bool]
            },
            'AFTER': {
                'P': [boogie_parsing.BoogieType.bool]
            },
            'BETWEEN': {
                'P': [boogie_parsing.BoogieType.bool],
                'Q': [boogie_parsing.BoogieType.bool]
            },
            'AFTER_UNTIL': {
                'P': [boogie_parsing.BoogieType.bool],
                'Q': [boogie_parsing.BoogieType.bool]
            },
            'NONE': {
            }
        }
        return scope_env[self.name]

class Pattern:
    """
    The Pattern of a formalization. Copied from the reqtransformer.py.
    """
    def __init__(self, name: str = "NotFormalizable"):
        self.name = name
        self.pattern = PATTERNS[name]['pattern']

    def is_instantiatable(self):
        return self.name != "NotFormalizable"

    def instantiate(self, scope, *args):
        return scope + ', ' + self.pattern.format(*args)

    def __str__(self):
        return self.pattern

    def get_allowed_types(self):
        return BoogieType.alias_env_to_instantiated_env(
            PATTERNS[self.name]['env']
        )

#
class ScopedPattern:
    """
    The Scoped Pattern of a formalization. Copied from the reqtransformer.py.
    """
    def __init__(self, scope: Scope = Scope.NONE, pattern: Pattern = None):
        self.scope = scope
        if not pattern:
            pattern = Pattern()
        self.pattern = pattern
        self.regex_pattern = None

    def get_string(self, expression_mapping: dict):
        #TODO: avoid having this problem in the first place
        try:
            return self.__str__().format(**expression_mapping).replace('\n', ' ').replace('\r', ' ')
        except KeyError as e:
            logging.error(f"Pattern {self.pattern.name}: insufficient "
                          f"keys in expression mapping {str(expression_mapping)}")
        return "Pattern error - please delete formalisation."


    def is_instantiatable(self) -> bool:
        return self.scope != Scope.NONE and self.pattern.is_instantiatable()

    def instantiate(self, *args):
        return self.pattern.instantiate(self.scope, *args)

    def regex(self):
        if self.regex_pattern is not None:
            return self.regex_pattern

        fmt = string.Formatter()
        fields = set()
        literal_str = self.__str__()
        for (_, field_name, _, _) in fmt.parse(literal_str):
            fields.add(field_name)
        fields.remove(None)

        for f in fields:
            literal_str = literal_str.replace('"{{{}}}"'.format(f), r'"([\d\w\s"-]*)"')

        self.regex_pattern = literal_str
        return self.regex_pattern

    def get_scope_slug(self):
        if self.scope:
            return self.scope.get_slug()
        return "None"

    def get_pattern_slug(self):
        if self.pattern:
            return self.pattern.name
        return "None"

    def __str__(self):
        return str(self.scope) + ', ' + str(self.pattern)

    def get_allowed_types(self):
        result = self.scope.get_allowed_types()
        result.update(self.pattern.get_allowed_types())
        return result

class Variable:
    """
    The variables class that are used to create the formalizations based on the state names and action names.
    Very much reused from the reqtransformer.py.
    But without the base class (HanforVersioned).
    """
    CONSTRAINT_REGEX = r"^(Constraint_)(.*)(_[0-9]+$)"

    def __init__(self, name: str, type: str, value: str):
        self.name: str = name
        self.type: str = type
        self.value: str = value
        #self.tags: set[str] = set()
        #self.script_results: str = ''
        self.belongs_to_enum: str = ''
        #self.constraints = dict()
        self.description: str = ''

    def __str__(self):
        if self.belongs_to_enum == "":
            belongs_to_enum = "Empty"
        else:
            belongs_to_enum = self.belongs_to_enum
        return (f'Name: {self.name}, Type: {self.type}, Value: {self.value}, '
                f'Belongs to enum: {belongs_to_enum}')

    def __repr__(self):
        return f'Variable("{self.name}","{self.type}",{self.value})'

    def set_type(self, new_type):
        allowed_types = ['CONST']
        allowed_types += boogie_parsing.BoogieType.get_valid_type_names()
        if new_type not in allowed_types:
            raise ValueError(f'Illegal variable type: `{new_type}`. Allowed types are: `{allowed_types}`')

        self.type = new_type

    def set_belongs_to_enum(self, enum_name:str):
        self.belongs_to_enum = enum_name

    def set_value(self, value: str):
        self.value = value

class VariableCollection:
    """
    The collection of all variables. Very much reused from the reqtransformer.py.
    But without the base classes (HanforVersioned, Pickleable).
    """
    def __init__(self):
        self.collection: Dict[str, Variable] = dict()
        self.req_var_mapping = dict()
        self.var_req_mapping = dict()

    def __contains__(self, item):
        return item in self.collection.keys()

    def __str__(self):
        """
        Seeing which variables the Variable Collection contains.
        """
        returnval = "The Variable Collection contains the following variables:\n"
        for var_name, variable in self.collection.items():
            returnval += "    " + variable.name + " " + str(variable.type + " ") + str(
                variable.value) + " " + variable.belongs_to_enum + "\n"
        return returnval

    def __repr__(self):
        """
        Representation of the Variable Collection.
        """
        returnval = "VariableCollection( \n"
        for var_name, variable in self.collection.items():
            returnval += ("    (" + var_name + ": Variable(" + variable.name + " " + str(variable.type + " ")
                          + str(variable.value) + ")\n")
        return returnval

    def get_var_names(self):
        var_names: list = []
        for key in self.collection.keys():
            var_names.append(key)

        return var_names

    def var_name_exists(self, name):
        return name in self.collection.keys()

    def add_var(self, var_name, variable=None):
        if not self.var_name_exists(var_name):
            if variable is None:
                variable = Variable(var_name, type= None, value= None)
            print("Adding variable " + var_name + " to collection.")
            self.collection[variable.name] = variable

    def map_req_to_vars(self, rid, used_variables):
        """ Map a requirement by rid to used vars."""

        if rid not in self.req_var_mapping.keys():
            self.req_var_mapping[rid] = set()
        for var in used_variables:
            self.req_var_mapping[rid].add(var)

    # ToDo: function rename is missing, cause to many calls of functions that lead to errors.

    def get_boogie_type_env(self):
        mapping = {
            'bool': boogie_parsing.BoogieType.bool,
            'int': boogie_parsing.BoogieType.int,
            'enum_int': boogie_parsing.BoogieType.int,
            'enum_real': boogie_parsing.BoogieType.real,
            'enumerator_int': boogie_parsing.BoogieType.int,
            'enumerator_real': boogie_parsing.BoogieType.real,
            'real': boogie_parsing.BoogieType.real,
            'unknown': boogie_parsing.BoogieType.unknown,
            'error': boogie_parsing.BoogieType.error
        }
        type_env = dict()
        for name, var in self.collection.items():
            if var.type is None:
                type_env[name] = mapping['unknown']
            elif var.type.lower() in mapping.keys():
                type_env[name] = mapping[var.type.lower()]
            elif var.type == 'CONST':
                # Check for int, real or unknown based on value.
                try:
                    float(var.value)
                except Exception:
                    type_env[name] = mapping['unknown']
                    continue

                if '.' in var.value:
                    type_env[name] = mapping['real']
                    continue

                type_env[name] = mapping['int']
            else:
                type_env[name] = mapping['unknown']

        # Todo: Store this so we can reuse and update on collection change.
        return type_env

    def set_type(self, name, type):
        if type in ['ENUMERATOR_INT', 'ENUMERATOR_REAL']:
            if self.enum_type_mismatch(self.collection[name].belongs_to_enum, type):
                raise TypeError('ENUM type mismatch')

        self.collection[name].set_type(type)

    def store(self, path=None):
        self.var_req_mapping = self.invert_mapping(self.req_var_mapping)

    def invert_mapping(self, mapping):
        newdict = {}
        for k in mapping:
            for v in mapping[k]:
                newdict.setdefault(v, set()).add(k)
        return newdict


if __name__ == "__main__":
    print("Starting loading state machine in Hanfor.")
    print("Which example do you want to load?\n")
    print("0 - small example\n"
          "1 - Light Switch example\n"
          "2 - Car Key Control example")
    example_choice = input()
    # print(example_choice, type(example_choice))
    sm = []
    # ToDo: Could make here state machine in csv file format.
    if example_choice == "0":
        sm = [
            ["Off", "turn_on", "On"],
            ["On", "turn_off", "Off"]

        ]
    elif example_choice == "1":
        sm = [
            ["Light_Off", "switch_right", "Parking_Light"],
            ["Parking_Light", "switch_left", "Light_Off"],
            ["Parking_Light", "switch_right", "Head_Light"],
            ["Head_Light", "switch_left", "Parking_Light"],
            ["Head_Light", "switch_right", "Fog_Light"],
            ["Fog_Light", "switch_left", "Head_Light"],
        ]
    elif example_choice == "2":
        sm = [
            ["Car_Locked", "key_u", "Car_Unlocked"],
            ["Car_Locked", "key_flap_u", "Flap_Unlocked"],
            ["Car_Locked", "key_trunk_u", "Trunk_Unlocked"],
            ["Car_Unlocked", "key_l", "Car_Locked"],
            ["Flap_Unlocked", "key_l", "Car_Locked"],
            ["Flap_Unlocked", "key_u", "Car_Unlocked"],
            ["Flap_Unlocked", "key_trunk_u", "Mixed_Unlocked"],
            ["Trunk_Unlocked", "key_flap_u", "Mixed_Unlocked"],
            ["Trunk_Unlocked", "key_l", "Car_Locked"],
            ["Trunk_Unlocked", "key_u", "Car_Unlocked"],
            ["Mixed_Unlocked", "key_l", "Car_Locked"],
            ["Mixed_Unlocked", "key_u", "Car_Unlocked"],

        ]
    else:
        print("Usage: Please type in one correct value !!!")
        exit()
    print("Take state machine with " + str(len(sm)) + " transitions:\n" + str(sm) + "\n")

    # Create state machine
    state_machine = StateMachine(sm)

    print("Done. State machine loaded successfully.\n")

    # Create variables
    print("Creating the variables ... ")

    var_collection = state_machine.create_variables()

    count = 0

    print(var_collection)
    list_variables = var_collection.get_var_names()

    print("Done. " + str(len(list_variables)) + " variables are created successfully.\n")

    # Create Requirements out of the state machine
    print("Creating the requirements ... \n ")
    req_collection = state_machine.from_state_machine_to_requirement()

    print(req_collection)

    print("Done. " + str(len(req_collection.collection)) + " requirements are created successfully.\n")

    # Create Formalizations
    print("Starting the formalization ... \n ")

    counter_forms = req_collection.do_formalization_for_all_reqs(var_collection)

    print("Done. " + str(counter_forms) + " formalizations are created successfully.\n")


    print("Transforming state machine into Hanfor successfull.\n"
          "Created:\n" +
              "    " + str(len(req_collection.collection)) + " requirements\n"
              "    " + str(counter_forms) + " formalizations")