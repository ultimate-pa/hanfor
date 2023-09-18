"""
Mirko Werling, University of Freiburg, Department of Computer Science
"""

import json

# Open the JSON file for reading
with open('stateMachine_LightSwitch.json', 'r') as stateMachine:
    # Load the JSON data
    data = json.load(stateMachine)

    # Process each JSON object
    for item in data:
        id = item["ID"]
        description = item["Description"]
        type = item["Type"]
        action = item["Action"]
        stateVal = item["stateVal"]
        variable = item["variable"]
        print(f"ID: {id}, Description: {description}, Type: {type}, stateVal: {stateVal}")

print(len(data))
print("It is", data[0]["ID"])
print("Test")gi
for item in data:
    print(item)
    if item["ID"] == 2:
        print(f"Key with Value 2: {item}")
# for key, value in data.items():
  #  if value == 2:
   #     print(f"Key: {key}, Value: {value}")
