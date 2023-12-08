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
    req01 = req.Requirement(id="01", description="From OFF to ON.", type_in_csv="requirement", csv_row="01",
                            pos_in_csv="01")
    req02 = req.Requirement(id="02", description="From ON to OFF.", type_in_csv="requirement", csv_row="01",
                            pos_in_csv="02")
    All_Req = req.RequirementCollection()
    print(All_Req)
    print(All_Req.requirements)

    print(req01, req01.csv_row)
    print(req02, req02.csv_row)

    All_Req.requirements.append(req01)
    All_Req.requirements.append(req02)

    print(All_Req)
    print(All_Req.requirements)


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
