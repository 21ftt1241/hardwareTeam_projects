# Create a nested dictionary to store the value pairs
value_pairs = {
    "105": {
        "trig": 24,
        "echo": 18
    },
    "202": {
        "trig": 21,
        "echo": 22
    }
}

# Get user input
inputNum = input("Enter a number (105 or 202): ")

# Check if the input corresponds to one of the groups
if inputNum in value_pairs:
    corresponding_group = value_pairs[inputNum]
    print(f"Number {inputNum} corresponds to the group:")
    trig_value = corresponding_group["trig"]
    echo_value = corresponding_group["echo"]
    print(f"trig = {trig_value}")
    print(f"echo = {echo_value}")
else:
    print(f"Number {inputNum} is not found in the groups.")
