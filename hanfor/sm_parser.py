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

# variable
states = []
actions = []

def from_state_machine_to_requirement(sm):
    """
    The function creates the requirements from the statemachine.

    :param sm: given state machine.
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
            states.append(action)

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

def adding_implicit_transitions(sm, counter):
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

def do_formalizations(reqs):
    """
    Creating formalization for all requirements.

    :param reqs: list of all requirements.
    :return: list of formalization
    """
    forms = []
    for element in reqs:
        rid = element.rid

        form = reqtrans.Formalization(
            id=rid
        )
        form.scoped_pattern = "BoundedResponse"
        # print(form)

        forms.append(form)


    return forms

def create_variables(sm):
    """

    :param sm:
    :return:
    """
    global states
    global actions
    list_variables = []
    counter = 0

    basics = ["States", "Actions"]

    for basic in basics:
        list_val = []

        if basic == "States":
            print(basic)
            for state in states:
                val = reqtrans.Variable(
                    name= state,
                    type= "ENUMERATOR",
                    value= str(counter),
                    # belongs_to_enum= basic
                )
                list_val.append(val)
            var = reqtrans.Variable(
                name= basic,
                type= "ENUM_INT",
                value= list_val
            )
            list_variables.append(var)
            counter += 1
        elif basic == "Actions":
            print(basic)
            # creat the no_op action
            counter = 0
            act = reqtrans.Variable(
                name="no_op",
                type="ENUMERATOR",
                value=str(counter),
                # belongs_to_enum="Actions"
            )
            list_val.append(act)

            # create the rest actions
            counter += 1
            for action in actions:
                act = reqtrans.Variable(
                    name= action,
                    type= "ENUMERATOR",
                    value= str(counter),
                    # belongs_to_enum= basic
                )
                list_val.append(act)
            var = reqtrans.Variable(
                name= basic,
                type= "ENUM_INT",
                value= list_val
            )
            list_variables.append(var)
            counter += 1

    return list_variables



if __name__ == "__main__":
    print("Starting loading state machine in Hanfor.")
    print("Which example do you want to load?\n")
    print("0 - small example\n"
          "1 - Light Switch example\n")
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

    # Create Formalizations
    print("Starting the formalization ... \n ")

    list_form = do_formalizations(list_req)

    # check formalizations
    # print(str(list_form) + "\n")


    print("Done. " + str(len(list_form)) + " formalizations are created successfully.\n")

    print("Creating the variables ... \n ")

    list_var = create_variables(state_machine)

    # check the write variables are existing.
    print("...\n " + str(list_var))
    for element in list_var:
        print(element.name, element.type, element.value)
        for val in element.value:
            print(val.name, val.type, val.value)

    print("Done. " + str(len(list_var)) + " variables are created successfully.\n")


    """
    req01 = reqtrans.Requirement(
        id="01",
        description="From OFF to ON.",
        type_in_csv="requirement",
        csv_row={"1": "1"},
        pos_in_csv=1
    )
    req02 = reqtrans.Requirement(
        id="02",
        description="From ON to OFF.",
        type_in_csv="requirement",
        csv_row={"2": "2"},
        pos_in_csv=2
    )

    formreq01 = reqtrans.Formalization(1)
    formreq01.scoped_pattern = "BoundedResponse"

    formreq02 = reqtrans.Formalization(2)
    formreq02.scoped_pattern = "BoundedResponse"

    print(req01.formalizations.keys())

  #  print(formreq01.scoped_pattern)
  #  print(formreq02.scoped_pattern)

  #  print(formreq01)
  #  print(formreq02)

    freeform = reqtrans.Requirement._next_free_formalization_id(req02)

    print(freeform)

    All_Req = reqtrans.RequirementCollection()
    """
    # Done
    # - Create low state machine
    # - Read states and actions, and form them into requirements
    # - Create implicit transitions, and form them into requirements

    # ToDo
    #   - Add: Enums with belongs to
    #   - search for the right variables in the hanfor examples


    print("Transforming state machine into Hanfor successfull.")

