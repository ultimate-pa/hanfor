"""
Mirko Werling, University of Freiburg, Department of Computer Science
"""

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

# ToDo: Which form does hanfor need?
# ToDO: each transition form a current state, action and next state -> bring this in a data structure
#        Which one should we use?
# Should we directly use the structure of hanfor, to make it easy?
# first data structure of state machine, or directly into hanfor requirement?



# for key, value in data.items():
  #  if value == 2:
   #     print(f"Key: {key}, Value: {value}")
