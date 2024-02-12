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

def from_state_machine_to_requirement(sm):
    """

    :param sm: given state machine.
    :return: one list of requirements for each transition in state machine.
    """
    print("Into the function.")
    counter = 1
    reqs = []
    for transition in sm:
        # configure basics of state machine
        current_state = transition[0]
        successor_state = transition[2]
        action = transition[1]

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

    for element in adding_implicit_transitions(sm, counter):
        reqs.append(element)
    print(reqs)

    return reqs

def adding_implicit_transitions(sm, counter):
    list_imp_trans = []

    counter_trans = counter
    for transition in sm:
        # configure basics of state machine
        current_state = transition[0]
        successor_state = current_state
        action = transition[1]

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






if __name__ == "__main__":
    print("Starting loading state machine in Hanfor.")
    state_machine = [
        ["Off", "turn_on", "On"],
        ["On", "turn_off", "Off"]

    ]
    print("state machine: " + str(state_machine))
    list_req = from_state_machine_to_requirement(state_machine)

    print("list of all requirements" + str(list_req))

    # check the write requirements are existing.
    for element in list_req:
        print(element.description)

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

    # Done
    # - Create low state machine
    # - Read states and actions, and form them into requirements
    # - Create implicit transitions, and form them into requirements

    # ToDo
    #   - Add pattern to requirement

    print("ENDING")

