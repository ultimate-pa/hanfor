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


# for key, value in data.items():
  #  if value == 2:
   #     print(f"Key: {key}, Value: {value}")
