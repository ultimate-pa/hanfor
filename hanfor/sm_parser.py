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
import reqtransformer as req

if __name__ == "__main__":
    print("Loading state machine in Hanfor.")
    req01 = req.Requirement(id="01", description="From OFF to ON.", type_in_csv="requirement", csv_row={"1": "1"},
                            pos_in_csv=1)
    req02 = req.Requirement(id="02", description="From ON to OFF.", type_in_csv="requirement", csv_row={"2": "2"},
                            pos_in_csv=2)

    formreq01 = req.Formalization(1)
    formreq01.scoped_pattern = "BoundedResponse"

    formreq02 = req.Formalization(2)
    formreq02.scoped_pattern = "BoundedResponse"

    print(formreq01.scoped_pattern)

    print(formreq02)

    All_Req = req.RequirementCollection()

    print("ENDING")



# do class instances for each requirement
# Reqtransfomer does requirements, but loads it from csv data

# one transition is one requirement
# requirement has specific pattern
# initial requirement, has specific pattern

# ToDo: Which form does hanfor need?
# ToDO: each transition form a current state, action and next state -> bring this in a data structure
#        Which one should we use?
# Should we directly use the structure of hanfor, to make it easy?
# first data structure of state machine, or directly into hanfor requirement?



# for key, value in data.items():
  #  if value == 2:
   #     print(f"Key: {key}, Value: {value}")
