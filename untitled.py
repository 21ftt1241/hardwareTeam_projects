# Create a dictionary to store the value pairs
value_pairs = {
    "105": "12",
    "202": "16"
}

# Get user input
inputNum = input("Enter a number (105 or 202): ")

# Check if the input corresponds to one of the pairs
if inputNum in value_pairs:
    corresponding_value = value_pairs[inputNum]
    print(f"Number {inputNum} corresponds to {corresponding_value}.")
else:
    print(f"Number {inputNum} is not found in the pairs.")
