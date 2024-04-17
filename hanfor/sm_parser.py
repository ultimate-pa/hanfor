"""
Mirko Werling, University of Freiburg, Department of Computer Science
"""

"""
# for loading a json file with the the data of the state machine
import json

# Open the JSON file for reading
with open('stateMachine_LightSwitch.json', 'r') as stateMachine:
    # Load the JSON data
    data = json.load(stateMachine)

    # Process each JSON object
    print(f"# transitions: {len(data)}")
    for item in data:
        # print(item)
        # print(item.keys())
        if "Init" in item.keys():
            # print("Inside Init")
            init = item["Init"]
            print(f"Init: {init}")
        elif "Transition" in item.keys():
            # print("Inside Transition")
            transition = item["Transition"]
            print(f"Transition: {transition}")
            current_state = transition[0]
            action = transition[1]
            next_state = transition[2]
            print(f"current state: {current_state}, action: {action}, next state: {next_state}")
"""

# import ...
# import hanfor.hanfor.app as app

import reqtransformer as reqtrans

from typing import Dict, Tuple

# variable
states = []
actions = []
val_collection = None

class VariableCollection(reqtrans.VariableCollection):
    def __init__(self):
        self.collection: Dict[str, reqtrans.Variable] = dict()
        self.req_var_mapping = dict()
        self.var_req_mapping = dict()

    def __contains__(self, item):
        return item in self.collection.keys()

def from_state_machine_to_requirement(sm: list):
    """
    The function creates the requirements from the statemachine.

    :param sm: given state machine in list form.
    :return: one list of requirements for each transition in state machine.
    """
    counter = 1
    reqs = []
    global states
    global actions
    for transition in sm:
        # configure basics of state machine
        current_state = transition[0]
        if current_state not in states:
            states.append(current_state)
        successor_state = transition[2]

        action = transition[1]
        if action not in actions:
            actions.append(action)

        # preparing the requirement attributes
        id = "0" + str(counter)
        description = "From " + str(current_state) + " to " + str(successor_state) + "."
        type_in_csv = "requirement"
        csv_row = {str(counter): str(counter)}
        # pos_in_csv = counter


        req = reqtrans.Requirement(
        id=id,
        description=description,
        type_in_csv=type_in_csv,
        csv_row=csv_row,
        pos_in_csv=counter
        )
        reqs.append(req)
        counter += 1

    # adding also the implicit transitions
    for element in adding_implicit_transitions(sm, counter):
        reqs.append(element)

    return reqs

def adding_implicit_transitions(sm: list, counter: int):
    """
    Computing the implicit transitions as requirements.

    :param sm: state machine
    :param counter: counts the implicit transitions, start from last normal requirement
    :return: list of implicit transitions
    """
    list_imp_trans = []
    counter_trans = counter

    global states
    # check states
    # print(states)

    for state in states:
        # configure basics of state machine
        current_state = state
        successor_state = current_state
        # action = transition[1]

        # preparing the requirement attributes
        id = "0" + str(counter_trans)
        description = "From " + str(current_state) + " to " + str(successor_state) + "."
        type_in_csv = "requirement"
        csv_row = {str(counter_trans): str(counter_trans)}
        # pos_in_csv = counter

        req = reqtrans.Requirement(
            id=id,
            description=description,
            type_in_csv=type_in_csv,
            csv_row=csv_row,
            pos_in_csv=counter_trans
        )
        list_imp_trans.append(req)
        counter_trans += 1

    return list_imp_trans

def do_formalizations(reqs: list, vars: list):
    """
    Creating formalization for all requirements.

    :param reqs: list of all requirements.
    :return: list of formalization
    """
    forms = []
    variables = vars
    # variable_collection = variable_collection
    # mapping = form.
    for element in reqs:
        rid = element.rid

        form = reqtrans.Formalization(
            id=rid
        )
        # form.set_expressions_mapping()
        # form.scoped_pattern = "BoundedResponse" #in first version pattern
        form.scoped_pattern = "StateMachineTimeless"
        print(form.id, form.scoped_pattern, form.belongs_to_requirement)
        # form.set_expressions_mapping(mapping=mapping, variable_collection=variable_collection, rid=rid)

        # ToDo: for implicit transitions another scope pattern name 'Invariance'
        #       implemented in pattern.py as 'Invariant'
        # ToDo: get the formalization complete

        # ToDo: implement mapping and variable collection

        forms.append(form)


    return forms

def create_variables(sm: list):
    """

    :param sm:
    :return:
    """
    global states
    global actions

    list_variables = []
    counter = 0

    basics = ["State", "Action"]

    for basic in basics:
        list_val = []

        if basic == "State":
            var = reqtrans.Variable(
                name=basic,
                type="ENUM_INT",  # enumerator_int
                value=list_val
            )
            var_collection.collection[var.name] = var
            for state in states:
                sta = reqtrans.Variable(
                    name= state,
                    type= "ENUMERATOR", # enum_int
                    value= str(counter),
                )
                sta.belongs_to_enum = basic
                print(sta.name, sta.type, sta.value, sta.belongs_to_enum)
                list_val.append(sta)
                var_collection.collection[sta.name] = sta
                counter += 1

            list_variables.append(var)

        elif basic == "Action":
            # create action enum
            var = reqtrans.Variable(
                name=basic,
                type="ENUM_INT",
                value=list_val
            )
            var_collection.collection[var.name] = var

            # creat the no_op action
            counter = 0
            act = reqtrans.Variable(
                name="no_op",
                type="ENUMERATOR",
                value=str(counter),
            )
            act.belongs_to_enum = basic
            list_val.append(act)
            var_collection.collection[act.name] = act

            # create the rest actions
            counter += 1
            for action in actions:
                act = reqtrans.Variable(
                    name= action,
                    type= "ENUMERATOR",
                    value= str(counter)
                )
                act.belongs_to_enum = basic
                print(act.name, act.type, act.value, act.belongs_to_enum)
                list_val.append(act)
                var_collection.collection[act.name] = act
                counter += 1

            list_variables.append(var)


    return list_variables



if __name__ == "__main__":
    print("Starting loading state machine in Hanfor.")
    print("Which example do you want to load?\n")
    print("0 - small example\n"
          "1 - Light Switch example\n"
          "2 - Car Key Control example")
    example_choice = input()
    # print(example_choice, type(example_choice))
    state_machine = []
    if example_choice == "0":
        state_machine = [
            ["Off", "turn_on", "On"],
            ["On", "turn_off", "Off"]

        ]
    elif example_choice == "1":
        state_machine = [
            ["Light_Off", "switch_right", "Parking_Light"],
            ["Parking_Light", "switch_left", "Light_Off"],
            ["Parking_Light", "switch_right", "Head_Light"],
            ["Head_Light", "switch_left", "Parking_Light"],
            ["Head_Light", "switch_right", "Fog_Light"],
            ["Fog_Light", "switch_left", "Head_Light"],
        ]
    elif example_choice == "2":
        state_machine = [
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
    print("Take state machine with " + str(len(state_machine)) + " transitions:\n" + str(state_machine) + "\n")

    # Create Requirements out of the state machine
    print("Creating the requirements ... \n ")

    list_req = from_state_machine_to_requirement(state_machine)

    # check the write requirements are existing.
    # print("...\n " + str(list_req))
    # for element in list_req:
    #    print(element.description)

    print("Done. " + str(len(list_req)) + " requirements are created successfully.\n")

    # Create variables
    print("Creating the variables ... ")

    global var_collection
    var_collection = VariableCollection()


    list_var = create_variables(state_machine)

    # check the write variables are existing.
    # print("...\n " + str(list_var))
    count = 0
    for element in list_var:
        out = str()
        count += 1
        for val in element.value:
            out = out + str([val.name, val.type, val.value]) + ", "
            count += 1
        print(element.name, element.type + " [" + out[:-2] + "]")

    print("\nDone. " + str(count) + " variables are created successfully.\n")


    # Create Formalizations
    print("Starting the formalization ... \n ")

    list_form = do_formalizations(list_req, list_var)

    # check formalizations
    # print(str(list_form) + "\n")


    print("Done. " + str(len(list_form)) + " formalizations are created successfully.\n")


    print("Transforming state machine into Hanfor successfull.")

